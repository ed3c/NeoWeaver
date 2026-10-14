# Native Codex capture and fixed parser-decision verification

`neoweaver.native` connects an actual Codex process capture to a fixed parser-response
Oracle and the existing `neoweaver.replay.inspect_pair`. The two public operations
separate execution from verification. This boundary covers source-assisted
validation. It does not establish isolation, causal gain, training or transfer.

## Inputs and ownership

`NativeTask` freezes the selected executable, model, effort, prompt bytes, response
schema bytes, population bytes, deadline and seed policy. `FixedConditions` holds
original replay references available before launch. Missing references remain
`None`; inspection names each gap. These data are selections, not credentials.

The Verification Owner fixes `DecisionOracle(task, expected, reference)` before
both generations. Its `expected` bytes contain literal decisions, independent of
the candidate's parser or answer. The Runner receives no Oracle. The validation
driver reads the original hash-pinned task and Oracle outside both source roots,
freezes them before launch, and checks the original bytes again afterward.
This API does not authenticate who constructed a Python object. It does not prove
that a Provider cannot read other files on the Host.

`NativeCapture` retains each launch's own task, conditions, original
`StagedSourcePair` commit/tree/treatment lineage, per-arm manifest, argv and private
capture directory. An inspection-time conditions parameter cannot relabel the
launch. `NativeOracleResult` binds its result to the exact capture and Oracle objects.
The pair API accepts captures and one fixed Oracle, not caller-supplied verdicts.

## Single invocation and retained evidence

`run_native_arm(pair, arm, task, conditions, capture_directory)` validates the
original two manifests before and after one invocation. Its argv uses the selected
Codex executable with `exec`, `--skip-git-repo-check`, `--json`, selected model and
effort, `--sandbox read-only`, `approval_policy="never"`, `--output-schema` and
`--output-last-message`. The prompt is supplied through stdin. There is no shell,
model fallback, invented seed, application retry, resume or Provider publication.
Any internal Provider retry remains visible in raw output and is not a new API call.

A fresh private directory outside both source arms contains `launch.json`,
`prompt.txt`, `schema.json`, `population.json`, `raw.ndjson`, `stderr.bin`,
`last-message.txt` when present, and `process.json`. Launch and process records
retain the exact selection and observed result. Timeout retains the available raw
prefix and an unknown process outcome. A launch error is separate from stderr.
Source drift never refreshes the accepted manifest. An unknown outcome requires
original Owner readback; this API cannot resume or repeat it.

Capture paths are canonicalized after symlink rejection. Existing paths and
source overlap refuse before launch. Inspection compares the retained launch,
process and output bytes and revalidates the original manifests. These checks
identify accidental drift or substitution; they are not a new authenticity system
or protection against a concurrent malicious Host changing both data and records.

## Completion and independent decisions

The decoder accepts one original `thread.started` and one `turn.started`, followed
by a completed turn. It checks any supplied thread/turn identities, item lifecycle
and actual usage fields. Repeated, contradictory, unfinished or malformed events
refuse. The installed CLI's nonfatal hook-warning items remain in the raw capture.
A top-level Provider error conservatively leaves completion INCONCLUSIVE.

The final completed agent message before `turn.completed` must agree with the
output-last-message file, allowing surrounding whitespace. An earlier JSON answer,
commentary, process exit 0, output file alone or `turn.failed` cannot establish
completion. The decoder does not infer a final phase field or concatenate a
historical interrupted trace with a resumed trace.

The independent comparator checks exactly `decisions` and exactly the
`case`, `classification`, `condition` fields for every case. It rejects duplicate
JSON keys, invalid types, repeated case IDs, missing/extra cases and nonfinite JSON.
Comparison uses case IDs, so list order is irrelevant.

| Observation | Scoped result | Completion |
| --- | --- | --- |
| Completed, valid decisions equal the fixed literals | `MATCH_SCOPED` | `True` |
| Completed, valid decisions differ | `FAIL_SCOPED` | `False` |
| Malformed protocol/answer, changed binding or source | `REFUSED` | `None` |
| Missing/partial/unavailable native completion or unavailable capture | `INCONCLUSIVE` | `None` |

## Original pair consumer and proof ceiling

`inspect_native_pair(baseline, candidate, oracle)` verifies each capture and calls
original `inspect_pair` once. Each `RunReadback` uses that capture's conditions,
actual thread ID, created capture directory and independent completion. Explicit
`launch_mismatches` identify differing executable, task/prompt/schema/population,
model/effort/deadline/seed policy or original source pair even when missing effects
already make the aggregate INCONCLUSIVE. Caller refs cannot conceal those differences.

The native adapter always retains `effect_status="unknown"`,
`isolation_verified=False` and `sandbox_ref=None`. Paths, PIDs and read-only argv
cannot establish a sandbox identity. Two `MATCH_SCOPED` results can therefore coexist
with pair `INCONCLUSIVE`. `CONTROL_H0_H0` means an unchanged validated source pair;
a candidate arm name does not mean H1. Applied treatment lineage is separately
reported and never implies gain. No result authorizes training or landing.

## Reproduction and evidence scope

The bounded driver calls the product API once per unchanged H0 arm, then calls
independent pair inspection once. Its input is the original private task JSON,
including the Owner's hash-pinned `selected_native_task` selection and fresh
`evidence_root`. The Oracle file is outside both materialized source copies and is
not passed in argv or prompt. Source-assisted tests may expose parser behavior;
this population is validation-only, never a held-out benchmark.

```text
python3 scripts/run_native_parser_control.py /private/task.json EXACT_CLEAN_SOURCE_HEAD
python3 -m unittest discover -s tests -p 'test_native*.py' -v
python3 -m unittest discover -s tests -p 'test_replay.py' -v
python3 -m unittest discover -s tests -p 'test_candidate_treatment.py' -v
python3 scripts/check_compiled_contracts.py
```

The `tests/test_native*.py` controls use literal protocol fixtures and mocked
processes. They cover final versus commentary/failed/partial completion, item
lifecycle, invalid Unicode, duplicate JSON/cases, wrong literal conditions,
source/capture drift, traversal/overlap/symlink refusal, reused runs/captures,
per-launch mismatches and absent original conditions. They are not live evidence.
Live observations and their limitations are recorded in [LESSON](../LESSON.md).
The original Managers, CI and Provider separately read back delivery.

## Original requirement progress

These are local contributions and remaining proofs. The original statements and
falsifiers in the [full specification](specs/learned-harness-coevolution.md), all
44 Card identities and historical compiled evidence remain unchanged.

| Original requirement | This unit contributes | Required proofs still OPEN |
| --- | --- | --- |
| REQ-01 Source integrity | Original source manifests and immutable launch selections | Whole-source semantic coverage, data rights |
| REQ-02 Three planes | Runner excludes Oracle; independent fixed comparator | Genuine isolation, protected acceptance/effect gates |
| REQ-03 Trainability | Source-bound native capture consumer | Reproducible isolated replay suitable for training |
| REQ-04 Two policies | Frozen Codex observations only | Proposer/open Solver generation tokens and update lineage |
| REQ-05 Causal attribution | H0/H0 connection control and named mismatches | Real H1, matched causal comparisons, repeated positive effect |
| REQ-06 Scoped patch | Reuses original applied-treatment lineage | Observed task failure and justified beneficial patch |
| REQ-07 Plugin transfer | Actual native task transport | Learned artifact install/load/fresh consumption/effect |
| REQ-08 Full lifecycle | Admitted writer's implementation and scoped controls | Original Manager consumption, matching-head CI, Provider delivery |
| REQ-09 Learning dataset | Fixed source-assisted validation population | Rights, train/held-out partitions, eligible reward/token lineage |
| REQ-10 Lesson lineage | Actual defect/review/correction records | Original Provider PR/merge/closure readbacks |

The parent Goal remains OPEN. Native task completion does not close any whole
requirement, certify a Trainer, or upgrade historical `NOT_RUN` evidence.
