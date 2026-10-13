# A5.2 Bounded Docker Execution Transport

`neoweaver.execution.run_container_arm(pair, arm, task, evidence_dir)` adds one executable transport after A5.1 source staging. The **original Task/Environment Owner** supplies a digest-pinned Docker image, exact command argv, bounded deadline, and a selected evidence destination. The function never invents a task, input refs, acceptance, container image, credentials, Oracle or permission.

## Inputs and execution

- The existing `StagedSourcePair` must contain distinct baseline/candidate directories whose complete current tracked file contents match the recorded SHA-256 entries. Unexpected files, symlinks, aliased arms, and altered bytes refuse before execution.
- `ContainerTask.image` must be `repository@sha256:64-hex-digest`. `argv` is a nonempty tuple of exact arguments (no shell), and `timeout_seconds` is an explicitly supplied integer between 1 and 300. The transport does **not** pull new images.
- The Host-selected `docker` CLI must be installed. The container command includes `--network=none`, `--read-only`, `--cap-drop=ALL`, `--security-opt=no-new-privileges`, resource limits, an unprivileged uid, and a read-only bind mount of only the selected staged source copy.
- The destination must be fresh and outside both staged copies. The Host generates the container name, invokes Docker once and records actual stdout/stderr in separate byte files. A second arm requires its own separately selected evidence directory and invocation.

## Evidence and stop boundary

`ContainerCapture` includes the arm, runtime-generated container name, CLI exit status, stdout/stderr paths and digests, observed wall time, and original source manifest identity. Transport outcome is `EXIT_RECORDED`, `BACKEND_REFUSED`, or `UNKNOWN_OUTCOME`. Docker client exit code 0 means only a process exit; it does **not** prove task completion, independent oracle acceptance or sandbox isolation.

For every result: `task_completed=None`, `effect_status=unknown`, `isolation_verified=false`, `authorizes_landing=false`. These are intentional proof limits. In particular, the receipt cannot be substituted for `RunReadback` or fed into `inspect_pair` as a verified original Runner result.

If a client timeout, transport failure or ambiguous external outcome occurs, preserve the actual container name/captures and request a **fresh Docker Provider readback before any retry**. The transport does not repeat writes, silently delete an unknown container or manufacture a terminal task result.

## Verification

`tests/test_execution.py` covers the original pinned command shape, negative source/identity cases, safe destination handling, no-Docker refusal, Docker client failure, one-shot timeout and persisted output. Its Docker transport is **mocked** so GitHub CI can run without a privileged daemon. It does not claim that the Docker flags were successfully enforced by a real kernel or that native Agent behavior ran. A genuine Docker engine and an Owner-selected image/task are needed for physical isolation/readback verification.

## Remaining requirements

**A5.2 not yet complete:** the original TaskSnapshot/Environment Producer must bind the task, environment, Solver/seed/budget and protected oracle; a selected trusted Docker/runtime host must execute both arms and independently inspect isolation and actual output. The original independent Verifier then judges task success and produces legitimate `RunReadback` for existing `inspect_pair`. A6 training eligibility, A7 transfer and whole Goal remain unverified.
