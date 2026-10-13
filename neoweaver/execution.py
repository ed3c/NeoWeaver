"""Execute one fixed-source arm through an external Docker engine.

Captures a real Docker CLI process, not proof of task completion or sandbox
isolation. The original Owner still selects the image, task and oracle.
"""
from dataclasses import dataclass
import hashlib
import json
import os
from pathlib import Path
import re
import secrets
import shutil
import subprocess
import time

from .snapshot import StagedSourcePair


class ExecutionRefusal(ValueError):
    def __init__(self, condition):
        self.condition = condition
        super().__init__(condition)


@dataclass(frozen=True, slots=True)
class ContainerTask:
    image: str             # Original Environment Owner's digest-pinned image
    argv: tuple[str, ...]  # Original Task Owner's exact executable argv
    timeout_seconds: int   # Original selected deadline, bounded here


@dataclass(frozen=True, slots=True)
class ContainerCapture:
    arm: str
    container_name: str
    status: str             # EXIT_RECORDED / BACKEND_REFUSED / UNKNOWN_OUTCOME
    exit_code: int | None
    stdout_path: Path
    stderr_path: Path
    stdout_sha256: str
    stderr_sha256: str
    elapsed_seconds: float
    source_manifest_sha256: str
    container_id: str | None = None
    effect_status: str = "unknown"
    isolation_verified: bool = False
    task_completed: bool | None = None
    authorizes_landing: bool = False


_IMAGE = re.compile(r"^[a-zA-Z0-9][a-zA-Z0-9._:/-]*@sha256:[0-9a-f]{64}$")


def _check_source(pair, arm):
    if type(pair) is not StagedSourcePair or arm not in ("baseline", "candidate"):
        raise ExecutionRefusal("invalid_source_pair")
    target = pair.baseline_dir if arm == "baseline" else pair.candidate_dir
    if target.is_symlink() or not target.is_dir():
        raise ExecutionRefusal("source_missing_or_symlink")
    # The original producer must supply distinct stages, not two aliases.
    if pair.baseline_dir.resolve() == pair.candidate_dir.resolve():
        raise ExecutionRefusal("reused_source_directory")
    expected = dict(pair.source_files)
    if not expected or len(expected) != len(pair.source_files):
        raise ExecutionRefusal("invalid_source_manifest")
    observed = {}
    for directory, dirs, files in os.walk(target, followlinks=False):
        root = Path(directory)
        for name in dirs:
            if (root / name).is_symlink():
                raise ExecutionRefusal("source_symlink")
        for name in files:
            file = root / name
            if file.is_symlink() or not file.is_file():
                raise ExecutionRefusal("source_symlink")
            relative = file.relative_to(target).as_posix()
            if relative not in expected:
                raise ExecutionRefusal("unexpected_source_file")
            observed[relative] = hashlib.sha256(file.read_bytes()).hexdigest()
    if observed != expected:
        raise ExecutionRefusal("source_changed")
    return target.resolve(strict=True)


def run_container_arm(pair: StagedSourcePair, arm: str, task: ContainerTask,
                      evidence_dir: Path) -> ContainerCapture:
    """Run only with explicitly selected inputs; never auto retry or certify PASS.

    The Docker engine must be supplied by the actual Host. With no engine,
    refuse without making an output directory. Unknown writes require Docker
    provider readback using the returned container name, not another run.
    """
    if type(task) is not ContainerTask or not isinstance(task.image, str) or not _IMAGE.fullmatch(task.image):
        raise ExecutionRefusal("image_not_digest_pinned")
    if (type(task.argv) is not tuple or not task.argv or
            any(type(arg) is not str or not arg or "\0" in arg for arg in task.argv)):
        raise ExecutionRefusal("invalid_task_argv")
    if type(task.timeout_seconds) is not int or not 1 <= task.timeout_seconds <= 300:
        raise ExecutionRefusal("invalid_timeout")
    source = _check_source(pair, arm)
    docker = shutil.which("docker")
    if not docker or not Path(docker).is_file():
        raise ExecutionRefusal("docker_unavailable")
    requested = Path(evidence_dir).absolute()
    if (requested.is_symlink() or any(parent.is_symlink() for parent in requested.parents)
            or not requested.parent.is_dir()):
        raise ExecutionRefusal("unsafe_evidence_dir")
    evidence = requested.resolve(strict=False)
    arm_roots = (pair.baseline_dir.resolve(), pair.candidate_dir.resolve())
    if (evidence.exists() or any(evidence == root or evidence in root.parents
                                 or root in evidence.parents for root in arm_roots)):
        raise ExecutionRefusal("evidence_dir_exists_or_overlaps")

    # Name originates in the executing Host rather than an Agent-authored prompt.
    name = "nw-replay-" + secrets.token_hex(12)
    cidfile = evidence / "container.cid"
    command = [docker, "run", "--pull=never", "--name", name,
               "--cidfile", str(cidfile),
               "--network=none", "--read-only", "--cap-drop=ALL",
               "--security-opt=no-new-privileges", "--pids-limit=64",
               "--memory=512m", "--cpus=1", "--user=65534:65534",
               "--tmpfs=/tmp:rw,nosuid,nodev,size=32m",
               "--env=PYTHONDONTWRITEBYTECODE=1", "--workdir=/workspace",
               "--mount", "type=bind,src=" + str(source) + ",dst=/workspace,readonly",
               task.image, *task.argv]
    evidence.mkdir(mode=0o700)
    stdout_path, stderr_path = evidence / "stdout.bin", evidence / "stderr.bin"
    start = time.monotonic()
    # Stream directly to durable evidence, not unbounded in-memory pipes.
    with stdout_path.open("xb") as stdout_file, stderr_path.open("xb") as stderr_file:
        try:
            result = subprocess.run(command, stdout=stdout_file, stderr=stderr_file,
                                    timeout=task.timeout_seconds + 10, check=False)
            exit_code = result.returncode
            status = "BACKEND_REFUSED" if exit_code in (125, 126, 127) else "EXIT_RECORDED"
        except subprocess.TimeoutExpired:
            exit_code, status = None, "UNKNOWN_OUTCOME"
        except OSError as error:
            stderr_file.write(str(error).encode())
            exit_code, status = None, "UNKNOWN_OUTCOME"
    duration = time.monotonic() - start
    with stdout_path.open("rb") as output:
        stdout_sha = hashlib.file_digest(output, "sha256").hexdigest()
    with stderr_path.open("rb") as output:
        stderr_sha = hashlib.file_digest(output, "sha256").hexdigest()
    # Read the engine-created identity even on failure; never invent its ID.
    container_id = None
    if cidfile.exists():
        if cidfile.is_symlink() or not cidfile.is_file():
            status = "UNKNOWN_OUTCOME"
        else:
            raw_id = cidfile.read_text(encoding="utf-8").strip()
            if re.fullmatch(r"[0-9a-f]{64}", raw_id):
                container_id = raw_id
            else:
                status = "UNKNOWN_OUTCOME"
    elif status == "EXIT_RECORDED":
        # Docker client exit 0 alone cannot establish that a container existed.
        status = "UNKNOWN_OUTCOME"
    # Intentionally retain the named container for exact-ID Provider readback.
    # Original Owner owns later cleanup; no unknown-effect retries.
    return ContainerCapture(arm, name, status, exit_code,
                            stdout_path, stderr_path, stdout_sha, stderr_sha,
                            duration, pair.source_manifest_sha256, container_id)


@dataclass(frozen=True, slots=True)
class ContainerInspection:
    status: str   # CONFIG_AND_EXIT_MATCH / INCONCLUSIVE / REFUSED
    reasons: tuple[str, ...]
    container_id: str | None
    observed_exit_code: int | None = None
    scope: str = "DOCKER_PROVIDER_METADATA_ONLY"
    isolation_verified: bool = False
    task_completed: bool | None = None
    authorizes_landing: bool = False


def inspect_container_capture(capture: ContainerCapture, task: ContainerTask,
                              pair: StagedSourcePair) -> ContainerInspection:
    """Independent *read-only* Docker metadata readback bound to an engine ID.

    Config matching is not kernel isolation or original task/oracle success.
    Transport/capture identity and original task remain separate authorities.
    """
    if type(capture) is not ContainerCapture or type(task) is not ContainerTask:
        return ContainerInspection("REFUSED", ("invalid_input_type",), None)
    if (type(capture.container_id) is not str or
            not re.fullmatch(r"[0-9a-f]{64}", capture.container_id)):
        return ContainerInspection("INCONCLUSIVE", ("missing_engine_container_id",), None)
    ident = capture.container_id
    if capture.status != "EXIT_RECORDED" or type(capture.exit_code) is not int:
        return ContainerInspection("INCONCLUSIVE", ("no_recorded_client_exit",), ident)
    if (type(task.image) is not str or not _IMAGE.fullmatch(task.image)
            or type(task.argv) is not tuple or not task.argv
            or any(type(x) is not str or not x for x in task.argv)):
        return ContainerInspection("REFUSED", ("invalid_original_task",), ident)
    if type(pair) is not StagedSourcePair or pair.source_manifest_sha256 != capture.source_manifest_sha256:
        return ContainerInspection("REFUSED", ("source_manifest_mismatch",), ident)
    try:
        source = _check_source(pair, capture.arm)
    except (ExecutionRefusal, OSError) as error:
        reason = error.condition if isinstance(error, ExecutionRefusal) else "source_unreadable"
        return ContainerInspection("INCONCLUSIVE", (reason,), ident)
    # The original capture producer owns both logs and the engine CID file.
    stdout_path, stderr_path = capture.stdout_path, capture.stderr_path
    if (not isinstance(stdout_path, Path) or not isinstance(stderr_path, Path) or
            stdout_path.parent != stderr_path.parent or
            stdout_path.name != "stdout.bin" or stderr_path.name != "stderr.bin"):
        return ContainerInspection("REFUSED", ("invalid_capture_paths",), ident)
    cidfile = stdout_path.parent / "container.cid"
    for file in (stdout_path, stderr_path, cidfile):
        if file.is_symlink() or not file.is_file():
            return ContainerInspection("INCONCLUSIVE", ("missing_bound_capture",), ident)
    try:
        with stdout_path.open("rb") as fp:
            stdout_sha = hashlib.file_digest(fp, "sha256").hexdigest()
        with stderr_path.open("rb") as fp:
            stderr_sha = hashlib.file_digest(fp, "sha256").hexdigest()
        original_cid = cidfile.read_text(encoding="utf-8").strip()
    except (OSError, UnicodeError):
        return ContainerInspection("INCONCLUSIVE", ("capture_read_unavailable",), ident)
    if (stdout_sha != capture.stdout_sha256 or stderr_sha != capture.stderr_sha256 or
            original_cid != ident):
        return ContainerInspection("REFUSED", ("capture_or_cid_mismatch",), ident)
    docker = shutil.which("docker")
    if not docker or not Path(docker).is_file():
        return ContainerInspection("INCONCLUSIVE", ("docker_unavailable",), ident)
    try:
        result = subprocess.run([docker, "inspect", "--type", "container", "--format", "{{json .}}", ident],
                                capture_output=True, timeout=10, check=False)
    except (OSError, subprocess.TimeoutExpired):
        return ContainerInspection("INCONCLUSIVE", ("provider_read_unavailable",), ident)
    if result.returncode != 0:
        return ContainerInspection("INCONCLUSIVE", ("provider_container_missing",), ident)
    try:
        obj = json.loads(result.stdout)
    except (ValueError, UnicodeError):
        return ContainerInspection("REFUSED", ("malformed_provider_response",), ident)
    if type(obj) is not dict or obj.get("Id") != ident:
        return ContainerInspection("REFUSED", ("wrong_provider_identity",), ident)
    state, cfg, host, mounts = (obj.get(k) for k in ("State", "Config", "HostConfig", "Mounts"))
    if any(type(x) is not dict for x in (state, cfg, host)) or type(mounts) is not list:
        return ContainerInspection("REFUSED", ("malformed_provider_contract",), ident)
    exit_value = state.get("ExitCode")
    if state.get("Status") != "exited" or state.get("Running") is not False or type(exit_value) is not int:
        return ContainerInspection("INCONCLUSIVE", ("provider_not_terminal",), ident)
    reasons = []
    def required(condition, key):
        if not condition:
            reasons.append(key)
    required(exit_value == capture.exit_code, "exit_code_mismatch")
    required(obj.get("Name") == "/" + capture.container_name, "container_name_mismatch")
    required(cfg.get("Image") == task.image, "image_mismatch")
    required(cfg.get("User") == "65534:65534", "user_mismatch")
    required(cfg.get("Cmd") == list(task.argv), "task_argv_mismatch")
    required(host.get("NetworkMode") == "none", "network_not_none")
    required(host.get("ReadonlyRootfs") is True, "rootfs_not_readonly")
    required(host.get("Privileged") is False, "privileged_container")
    required(host.get("AutoRemove") is False, "container_autoremoved")
    required("ALL" in (host.get("CapDrop") or []), "capabilities_not_dropped")
    required(any(opt in ("no-new-privileges", "no-new-privileges:true")
                 for opt in (host.get("SecurityOpt") or [])), "new_privileges_allowed")
    required(host.get("PidsLimit") == 64, "pids_limit_mismatch")
    required(host.get("Memory") == 512 * 1024 * 1024, "memory_limit_mismatch")
    required(host.get("NanoCpus") == 1_000_000_000, "cpu_limit_mismatch")
    found = [x for x in mounts if type(x) is dict and x.get("Destination") == "/workspace"]
    required(len(mounts) == 1 and len(found) == 1 and
             found[0].get("Type") == "bind" and
             found[0].get("Source") == str(source.resolve()) and
             found[0].get("RW") is False, "readonly_source_mount_mismatch")
    return ContainerInspection("INCONCLUSIVE" if reasons else "CONFIG_AND_EXIT_MATCH",
                               tuple(reasons), ident, exit_value)
