"""Materialize two pinned Git source copies; never execute a task.

Staging proves copied tracked Git blob bytes, NOT process/network isolation.
The original Snapshot/Environment Owner still supplies task and permissions.
"""
from dataclasses import dataclass, replace
import hashlib
import os
import stat
from pathlib import Path, PurePosixPath
import subprocess

from .patches import OwnerRef, ParsedProposal

MAX_SOURCE_BYTES = 64 * 1024 * 1024
MAX_FILES = 10000


class SnapshotRefusal(ValueError):
    """Refuse a non-pinned or unsafe source/staging boundary."""

    def __init__(self, condition):
        self.condition = condition
        super().__init__(condition)


@dataclass(frozen=True, slots=True)
class SourceFile:
    path: str
    sha256: str
    executable: bool


@dataclass(frozen=True, slots=True)
class SourceManifest:
    files: tuple[SourceFile, ...]
    sha256: str


@dataclass(frozen=True, slots=True)
class StagedSource:
    directory: Path
    manifest: SourceManifest


@dataclass(frozen=True, slots=True)
class StagedSourcePair:
    commit: str
    tree: str
    baseline: StagedSource
    candidate: StagedSource
    treatment_applied: bool = False
    status: str = "FILESYSTEM_COPIES_ONLY"
    authorizes_execution: bool = False
    authorizes_landing: bool = False


@dataclass(frozen=True, slots=True)
class TargetBinding:
    source_commit: str
    snapshot_ref: OwnerRef
    target_ref: OwnerRef
    expected_source_ref: OwnerRef
    relative_path: str
    expected_source: bytes
    protected_paths: tuple[str, ...]


def _relative_path(name):
    if type(name) is not str or not name or "\\" in name or "\0" in name:
        raise SnapshotRefusal("unsafe_source_path")
    path = PurePosixPath(name)
    if (path.is_absolute() or ".." in path.parts or ".git" in path.parts
            or path.as_posix() != name or name == "."):
        raise SnapshotRefusal("unsafe_source_path")
    return path


def _manifest(files):
    digest = hashlib.sha256()
    for entry in files:
        digest.update(entry.path.encode("utf-8") + b"\0")
        digest.update(b"x" if entry.executable else b"-")
        digest.update(bytes.fromhex(entry.sha256))
    return SourceManifest(tuple(files), digest.hexdigest())


def validate_source_pair(pair: StagedSourcePair) -> None:
    """Check both original arm manifests without accepting newly observed bytes."""
    if type(pair) is not StagedSourcePair:
        raise SnapshotRefusal("invalid_source_pair")
    roots = []
    for source in (pair.baseline, pair.candidate):
        if (type(source) is not StagedSource or not isinstance(source.directory, Path)
                or not source.directory.is_absolute()):
            raise SnapshotRefusal("invalid_source_pair")
        root = source.directory
        if root.is_symlink() or any(parent.is_symlink() for parent in root.parents):
            raise SnapshotRefusal("source_missing_or_symlink")
        if not root.is_dir():
            raise SnapshotRefusal("source_missing_or_symlink")
        roots.append(root.resolve(strict=True))
    if roots[0] == roots[1]:
        raise SnapshotRefusal("reused_source_directory")
    if roots[0] in roots[1].parents or roots[1] in roots[0].parents:
        raise SnapshotRefusal("overlapping_source_directories")
    for source in (pair.baseline, pair.candidate):
        manifest = source.manifest
        if (type(manifest) is not SourceManifest or type(manifest.files) is not tuple
                or not 1 <= len(manifest.files) <= MAX_FILES):
            raise SnapshotRefusal("invalid_source_manifest")
        expected = {}
        for entry in manifest.files:
            if type(entry) is not SourceFile:
                raise SnapshotRefusal("invalid_source_manifest")
            _relative_path(entry.path)
            if (entry.path in expected or type(entry.executable) is not bool
                    or type(entry.sha256) is not str or len(entry.sha256) != 64
                    or any(ch not in "0123456789abcdef" for ch in entry.sha256)):
                raise SnapshotRefusal("invalid_source_manifest")
            expected[entry.path] = entry
        if _manifest(manifest.files).sha256 != manifest.sha256:
            raise SnapshotRefusal("invalid_source_manifest")
        observed = set()
        total_bytes = 0
        def unavailable(error):
            raise error
        for directory, dirs, files in os.walk(source.directory, followlinks=False, onerror=unavailable):
            root = Path(directory)
            if any((root / name).is_symlink() for name in dirs):
                raise SnapshotRefusal("source_symlink")
            for name in files:
                file = root / name
                if file.is_symlink() or not stat.S_ISREG(file.stat().st_mode):
                    raise SnapshotRefusal("source_symlink")
                relative = file.relative_to(source.directory).as_posix()
                entry = expected.get(relative)
                if entry is None:
                    raise SnapshotRefusal("unexpected_source_file")
                with file.open("rb") as source_file:
                    data = source_file.read(MAX_SOURCE_BYTES - total_bytes + 1)
                total_bytes += len(data)
                if total_bytes > MAX_SOURCE_BYTES:
                    raise SnapshotRefusal("source_too_large")
                if (hashlib.sha256(data).hexdigest() != entry.sha256
                        or stat.S_IMODE(file.stat().st_mode) != (0o755 if entry.executable else 0o644)):
                    raise SnapshotRefusal("source_changed")
                observed.add(relative)
        if observed != expected.keys():
            raise SnapshotRefusal("source_changed")


def apply_candidate_treatment(pair: StagedSourcePair, proposal: ParsedProposal,
                              binding: TargetBinding) -> StagedSourcePair:
    """Replace one admitted tracked file; failures never refresh source authority.

    A failed or interrupted write needs original Owner readback before another
    action. This helper does not execute, retry, restore or authorize landing.
    """
    if (type(pair) is not StagedSourcePair or type(proposal) is not ParsedProposal
            or type(binding) is not TargetBinding or len(proposal.changes) != 1):
        raise SnapshotRefusal("invalid_treatment_input")
    if pair.treatment_applied:
        raise SnapshotRefusal("treatment_already_applied")
    change = proposal.changes[0]
    if (binding.source_commit != pair.commit or binding.snapshot_ref != proposal.snapshot_ref
            or binding.target_ref != change.target_ref
            or binding.expected_source_ref != change.expected_source_ref):
        raise SnapshotRefusal("source_binding_mismatch")
    relative = _relative_path(binding.relative_path).as_posix()
    if type(binding.protected_paths) is not tuple:
        raise SnapshotRefusal("invalid_protected_paths")
    protected = tuple(_relative_path(path).as_posix() for path in binding.protected_paths)
    if (relative in protected or change.target_ref == proposal.fixed_inputs.acceptance_ref
            or change.target_ref in proposal.fixed_inputs.protected_target_refs):
        raise SnapshotRefusal("protected_target")
    if type(binding.expected_source) is not bytes:
        raise SnapshotRefusal("invalid_expected_source")
    if pair.baseline.manifest != pair.candidate.manifest:
        raise SnapshotRefusal("source_changed")
    validate_source_pair(pair)
    expected = next((entry for entry in pair.baseline.manifest.files if entry.path == relative), None)
    if expected is None:
        raise SnapshotRefusal("target_not_tracked")
    target = pair.candidate.directory / relative
    if target.stat().st_nlink != 1:
        raise SnapshotRefusal("target_hardlink")
    if (hashlib.sha256(binding.expected_source).hexdigest() != expected.sha256
            or (pair.baseline.directory / relative).read_bytes() != binding.expected_source
            or (pair.candidate.directory / relative).read_bytes() != binding.expected_source):
        raise SnapshotRefusal("stale_expected_source")
    replacement = change.replacement.encode("utf-8")
    original_size = sum((pair.candidate.directory / entry.path).stat().st_size
                        for entry in pair.candidate.manifest.files)
    if original_size - len(binding.expected_source) + len(replacement) > MAX_SOURCE_BYTES:
        raise SnapshotRefusal("source_too_large")
    files = tuple(replace(entry, sha256=hashlib.sha256(replacement).hexdigest())
                  if entry.path == relative else entry for entry in pair.candidate.manifest.files)
    with target.open("wb") as output:
        output.write(replacement)
    result = replace(pair, candidate=replace(pair.candidate, manifest=_manifest(files)),
                     treatment_applied=True)
    validate_source_pair(result)
    return result


def _git(root, *args):
    try:
        output = subprocess.run(["git", "-C", str(root), *args],
                                capture_output=True, timeout=30, check=False)
    except (OSError, subprocess.TimeoutExpired) as error:
        raise SnapshotRefusal("git_read_unavailable") from error
    if output.returncode:
        raise SnapshotRefusal("git_read_refused")
    return output.stdout


def _git_files(root, commit):
    """Read original Git blob objects; archive export rules cannot hide files."""
    entries = _git(root, "ls-tree", "-r", "-z", "--full-tree", commit).split(b"\0")
    files = []
    seen = set()
    total_bytes = 0
    for entry in filter(None, entries):
        try:
            metadata, raw_path = entry.split(b"\t", 1)
            mode, kind, object_sha = metadata.split(b" ", 2)
            name = raw_path.decode("utf-8")
        except (ValueError, UnicodeError) as error:
            raise SnapshotRefusal("invalid_git_tree_entry") from error
        path = PurePosixPath(name)
        parts = path.parts
        if (not parts or path.is_absolute() or ".." in parts or "." in parts
                or "\\" in name or parts[0] == ".git"
                or "/".join(parts) != name or name in seen):
            raise SnapshotRefusal("unsafe_git_tree_path")
        seen.add(name)
        if mode not in (b"100644", b"100755") or kind != b"blob":
            raise SnapshotRefusal("unsupported_git_tree_entry")
        if len(seen) > MAX_FILES:
            raise SnapshotRefusal("source_too_large")
        try:
            blob_sha = object_sha.decode("ascii")
        except UnicodeError as error:
            raise SnapshotRefusal("invalid_git_tree_entry") from error
        payload = _git(root, "cat-file", "blob", blob_sha)
        total_bytes += len(payload)
        if total_bytes > MAX_SOURCE_BYTES:
            raise SnapshotRefusal("source_too_large")
        files.append((name, payload, mode == b"100755"))
    if not files:
        raise SnapshotRefusal("empty_source_tree")
    return files


def materialize_source_pair(root, commit, destination):
    """Stage exact clean HEAD to two new dirs; return Git-blob-derived proof.

    Creates files only under a non-existing destination. Does not run any
    candidate/task code or assert sandboxing. A partial write needs original
    owner readback/cleanup, never blind retry or overwrite.
    """
    root = Path(root).resolve(strict=True)
    requested = Path(destination).absolute()
    if requested.is_symlink() or any(parent.is_symlink() for parent in requested.parents):
        raise SnapshotRefusal("unsafe_destination")
    destination = requested.resolve(strict=False)
    if (not root.is_dir() or destination == root or root in destination.parents
            or destination in root.parents or not destination.parent.is_dir()):
        raise SnapshotRefusal("unsafe_destination")
    if destination.exists():
        raise SnapshotRefusal("destination_exists")
    if (type(commit) is not str or len(commit) != 40
            or any(ch not in "0123456789abcdef" for ch in commit)):
        raise SnapshotRefusal("invalid_commit")
    if Path(_git(root, "rev-parse", "--show-toplevel").decode().strip()).resolve() != root:
        raise SnapshotRefusal("not_git_root")
    head = _git(root, "rev-parse", "HEAD").decode().strip()
    if head != commit:
        raise SnapshotRefusal("stale_source_head")
    tree = _git(root, "rev-parse", "HEAD^{tree}").decode().strip()
    if _git(root, "status", "--porcelain", "--untracked-files=all").strip():
        raise SnapshotRefusal("dirty_source")
    files = _git_files(root, commit)
    manifest = _manifest(tuple(SourceFile(name, hashlib.sha256(data).hexdigest(), executable)
                               for name, data, executable in files))
    try:
        destination.mkdir()
    except FileExistsError as error:
        raise SnapshotRefusal("destination_exists") from error
    for arm in ("baseline", "candidate"):
        target = destination / arm
        target.mkdir()
        for rel, data, executable in files:
            to = target / rel
            to.parent.mkdir(parents=True, exist_ok=True)
            with to.open("xb") as output:
                output.write(data)
            to.chmod(0o755 if executable else 0o644)
    return StagedSourcePair(
        commit=commit, tree=tree,
        baseline=StagedSource(destination / "baseline", manifest),
        candidate=StagedSource(destination / "candidate", manifest))
