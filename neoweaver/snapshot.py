"""Materialize two pinned Git source copies; never execute a task.

Staging proves copied tracked Git blob bytes, NOT process/network isolation.
The original Snapshot/Environment Owner still supplies task and permissions.
"""
from dataclasses import dataclass
import hashlib
from pathlib import Path, PurePosixPath
import subprocess

MAX_SOURCE_BYTES = 64 * 1024 * 1024
MAX_FILES = 10000


class SnapshotRefusal(ValueError):
    """Refuse a non-pinned or unsafe source/staging boundary."""

    def __init__(self, condition):
        self.condition = condition
        super().__init__(condition)


@dataclass(frozen=True, slots=True)
class StagedSourcePair:
    commit: str
    tree: str
    source_manifest_sha256: str
    source_files: tuple[tuple[str, str], ...]
    baseline_dir: Path
    candidate_dir: Path
    status: str = "FILESYSTEM_COPIES_ONLY"
    authorizes_execution: bool = False
    authorizes_landing: bool = False


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
    # Compute identity from actual path/blob bytes, rather than model-authored
    # refs or a Git archive (which may omit/substitute files via .gitattributes).
    manifest = hashlib.sha256()
    for name, data, executable in files:
        manifest.update(name.encode("utf-8") + b"\0")
        manifest.update(b"x" if executable else b"-")
        manifest.update(hashlib.sha256(data).digest())
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
        commit=commit, tree=tree, source_manifest_sha256=manifest.hexdigest(),
        source_files=tuple((name, hashlib.sha256(data).hexdigest()) for name, data, _ in files),
        baseline_dir=destination / "baseline", candidate_dir=destination / "candidate")
