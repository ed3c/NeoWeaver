# A5.2 Bounded Docker Execution Transport

`neoweaver.execution.run_container_arm(pair, arm, task, evidence_dir)` adds one executable transport after A5.1 source staging. The **original Task/Environment Owner** supplies a digest-pinned Docker image, exact command argv, bounded deadline, and a selected evidence destination. The function never invents a task, input refs, acceptance, container image, credentials, Oracle or permission.

## Inputs and execution

- The existing `StagedSourcePair` contains separate baseline and candidate directories and manifests from the staging Producer. Both complete file lists, SHA-256 entries, and executable bits must match, including when H1 alone is selected. Unexpected files, symlinks, overlapping arms, changed baseline, and later candidate drift refuse before execution. A permitted H1 uses the manifest returned by `apply_candidate_treatment`; manually changing bytes does not grant a new manifest.
- `ContainerTask.image` must be `repository@sha256:64-hex-digest`. `argv` is a nonempty tuple of exact arguments (no shell), and `timeout_seconds` is an explicitly supplied integer between 1 and 300. The transport does **not** pull new images.
- The Host-selected `docker` CLI must be installed. The container command includes `--network=none`, `--read-only`, `--cap-drop=ALL`, `--security-opt=no-new-privileges`, resource limits, an unprivileged uid, and a read-only bind mount of only the selected staged source copy.
- The destination must be fresh and outside both staged copies. The Host generates a container name; Docker writes its original container ID to a private `--cidfile`. The container is deliberately **not auto-removed**, allowing exact-ID read-only Provider inspection after exit or an ambiguous transport outcome. stdout/stderr are preserved in separate byte files. A second arm requires its own evidence directory and invocation.

## Evidence and stop boundary

`ContainerCapture` includes the arm, runtime-generated container name, CLI exit status, stdout/stderr paths and digests, observed wall time, and the selected arm's source manifest identity. Transport outcome is `EXIT_RECORDED`, `BACKEND_REFUSED`, or `UNKNOWN_OUTCOME`. Docker client exit code 0 means only a process exit; it does **not** prove task completion, independent oracle acceptance or sandbox isolation.

For every result: `task_completed=None`, `effect_status=unknown`, `isolation_verified=false`, `authorizes_landing=false`. These are intentional proof limits. In particular, the receipt cannot be substituted for `RunReadback` or fed into `inspect_pair` as a verified original Runner result.

If a client timeout, transport failure, missing/malformed `--cidfile`, or ambiguous external outcome occurs, preserve the actual container name, any engine-written ID, and captures. Obtain a **fresh Docker Provider readback before any retry**. The transport does not repeat writes, silently delete a container or manufacture a terminal task result.

`inspect_container_capture(capture, original_task, original_staged_pair)` uses the **actual engine-created 64-hex container ID** for a read-only `docker inspect`. Before contacting Docker it compares the capture manifest to the original selected arm manifest and re-checks both staged arms, private producer-written CID file and stdout/stderr SHA-256. It refuses a mismatched source, changed capture, substituted CID or arbitrary caller-supplied directory. It then checks exact container ID/name, recorded client exit vs provider exit, pinned image, original command, unprivileged user, network/rootfs/capabilities/privileges/resource options and the read-only original source mount. Missing ID, missing provider record, nonterminal state or changed settings cannot return `CONFIG_AND_EXIT_MATCH`. This is **Docker Provider metadata agreement**, not proof of OS-level sandbox isolation, task/oracle success, fixed process genealogy, clean external effects or permission to start training. The original Owner retains explicit container cleanup after verified readback; no automatic cleanup occurs on unknown outcomes.

## Verification

`tests/test_execution.py` covers the original pinned command shape, negative source/identity cases, safe destination handling, no-Docker refusal, Docker client failure, one-shot timeout and persisted output. `tests/test_candidate_treatment.py` also connects real temporary Git blobs through the existing parser, bounded application, both arm transports, and inspection. Its literal-byte controls distinguish permitted H1 from manual drift, stale bindings, protected paths, symlinks, and capture substitution. Docker transport and provider responses in these tests are **mocked** so GitHub CI can run without a privileged daemon. It does not claim that the Docker flags were successfully enforced by a real kernel or that native Agent behavior ran. A genuine Docker engine and an Owner-selected image/task are needed for physical isolation/readback verification.

## Remaining requirements

**A5.2 not yet complete:** the original TaskSnapshot/Environment Producer must bind the task, environment, Solver/seed/budget and protected oracle; a selected trusted Docker/runtime host must execute both arms and independently inspect isolation and actual output. The original independent Verifier then judges task success and produces legitimate `RunReadback` for existing `inspect_pair`. A6 training eligibility, A7 transfer and whole Goal remain unverified.
