# Bounded candidate treatment

`neoweaver.snapshot.apply_candidate_treatment(pair, proposal, binding)` connects
the existing Parser to the existing execution transport. It consumes one
`ParsedProposal` and an original caller-fixed `TargetBinding`. It writes one
candidate file and returns a new `StagedSourcePair`. It executes no task.

## Producer and Consumer

`materialize_source_pair` reads a clean exact Git HEAD and creates two copies.
Each `StagedSource` contains a directory and a `SourceManifest`. Manifest entries
record tracked relative paths, content SHA-256, and executable bits. The initial
baseline and candidate manifests describe the same Git blobs.

`parse_proposal` retains its existing pure acceptance boundary. Its output does
not authorize effects. The original caller supplies `TargetBinding` with the
source commit, snapshot reference, target reference, expected-source reference,
tracked relative path, expected source bytes, and protected paths. Opaque
references are compared directly. Their strings are never decoded into paths.
The binding is trusted caller input, not a new authentication mechanism.

The application Producer compares the binding to the parsed proposal and staged
commit. Both staged copies must still match their original manifests and the
target must match the expected bytes. Unsafe or untracked paths, protected paths,
symlinks, a hardlinked candidate target, overlapping stages, stale bindings, and
previously applied treatments refuse before replacement. A protected file cannot
be selected through an allowed reference alias when its path is in the original
protected-path binding.

The function writes the proposal's UTF-8 replacement only to the candidate
target. The target's mode is retained. It derives the candidate manifest by
replacing that one original entry's hash. It does not refresh hashes for other
observed files. Baseline, other candidate files, and the original Git checkout
remain fixed. A failed or interrupted write requires original Owner readback.

`run_container_arm` and `inspect_container_capture` validate both complete arm
manifests, including bytes and modes, before consuming the selected arm.
`ContainerCapture.source_manifest_sha256` identifies that arm's manifest.
Inspection rejects a capture whose arm and manifest disagree before Docker
readback. Later target, non-target, or baseline drift cannot become accepted
source through this API. Reusing the old pair after a changed treatment also
fails its source check.

## Controls and evidence limits

`tests/test_candidate_treatment.py` uses real temporary Git blobs and the public
Parser, staging, application, transport, and inspection APIs. The positive
control compares H0 and H1 to literal bytes. Negative controls cover manual
drift, stale bindings and expected bytes, protected targets and aliases, unsafe
paths, symlinks, hardlinks, repeated treatment, later drift, mode drift, and
capture substitution. Refused transport and inspection paths do not call Docker.
Docker execution and provider responses are mocked in these tests.

The source checks do not prevent another process from changing files between a
check and a mount or write. They do not establish kernel isolation. The existing
transport retains unknown-outcome and original Provider readback obligations.
`ContainerCapture` is not `RunReadback` or a task PASS. `effect_status=unknown`,
`isolation_verified=false`, `task_completed=None`, and `authorizes_landing=false`
remain unchanged.

Live Docker execution still requires the original Owner's pinned image, task,
authorization, and provider readback. A responding daemon alone supplies none of
those task inputs. Source delivery, native Replay, independent oracle acceptance,
learning, frozen Codex transfer, and whole Goal have separate acceptance. All ten
REQ, 44 Cards, and historical verification bytes remain retained.
