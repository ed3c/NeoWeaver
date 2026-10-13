"""Execute one fixed-source arm through an external Docker engine.

Captures a real Docker CLI process, not proof of task completion or sandbox
isolation. The original Owner still selects the image, task and oracle.
"""
from dataclasses import dataclass
import hashlib
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
    command = [docker, "run", "--rm", "--pull=never", "--name", name,
               "--network=none", "--read-only", "--cap-drop=ALL",
               "--security-opt=no-new-privileges", "--pids-limit=64",
               "--memory=512m", "--cpus=1", "--user=65534:65534",
               "--tmpfs=/tmp:rw,nosuid,nodev,size=32m",
               "--env=PYTHONDONTWRITEBYTECODE=1", "--workdir=/workspace",
               "--mount", "type=bind,src=" + str(source) + ",dst=/workspace,readonly",
               task.image, *task.argv]
    evidence.mkdir()
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
    # No automatic Docker cleanup on unknown outcome: inspect original provider.
    return ContainerCapture(arm, name, status, exit_code,
                            stdout_path, stderr_path, stdout_sha, stderr_sha,
                            duration, pair.source_manifest_sha256)
