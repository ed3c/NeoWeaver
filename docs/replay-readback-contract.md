# A5 Paired Replay Readback — structural gate, not a Snapshot Runner

`neoweaver.replay.inspect_pair(baseline, candidate)` is the smallest
read-only consumer of **original Runner-produced** `RunReadback` records.
It reuses `OwnerRef` from the original PatchProposal parser. No new TaskSnapshot
producer, Scheduler, Stage, provider credential, CLI, filesystem binding,
or execution authorization is created.

The original Source/Environment Owner must supply the real TaskSnapshot and
execution preconditions. The original Runner must execute **two separately
isolated copies** and return run, sandbox and capture references. These are
opaque references, not paths inferred by an Agent. The independent Verifier
must inspect the underlying captures and protected oracle outside candidate
control. A matching string alone does not prove a trustworthy original producer,
actual sandbox isolation, complete traces, or an immutable oracle.

## Exact scoped behavior

* `REFUSED`: wrong arm order, malformed reference/type or internally
  inconsistent terminal observation.
* `INCONCLUSIVE`: any mismatch in snapshot, task, environment, Solver, seed
  policy, budget or oracle; missing original fixed conditions or harness references; missing/reused run, sandbox or capture references;
  missing terminal outcome or unknown external effect. An unknown is never
  converted into failure, zero cost or safe retry.
* `STRUCTURALLY_COMPARABLE`: two claimed terminal observations with matching
  fixed conditions, different declared run/sandbox/capture references and no
  declared unknown effect. Only reported completion values are exposed.
  `evidence_ceiling=DECLARED_RUNNER_READBACKS_ONLY` and
  `authorizes_landing=false` remain fixed. This is **not**
  independent acceptance, demonstrated isolation, native replay PASS,
  model improvement, Reward Observation or Training Eligibility.

The `harness_ref` may differ between H0 and H1; an unchanged H0/H0
control is also legal but is not evidence of a treatment gain.
No difference, reward, confidence interval, or effect is inferred
from one declared pair. Provider writes and effects are never executed.
Neither candidate nor parser may modify the independent evaluator.

## Verification and remaining work

`python3 -m unittest discover -s tests -v` executes focused positive,
negative and unknown controls in `tests/test_replay.py` together with
existing parser and compiled-specification cases.

Remaining A5: real Original TaskSnapshot/Environment Producer, two
genuinely isolated executable copies, original Runner raw captures, protected
regression gate and independently evaluated matched observations. The readback
gate does not replace any of these. A6 training rights/token lineage and A7
frozen Codex transfer remain separate. The original ten requirements and
historical compilation `NOT_RUN` bytes are unchanged.

## Native capture consumer

`neoweaver.native.inspect_native_pair` now supplies readbacks from actual native
captures and independent fixed parser decisions. Each arm retains its own launch
selection. The adapter reports actual launch/source differences before the original
pair verdict can be interpreted, and passes unknown effects and missing sandbox
references through unchanged. Missing original fixed references now produce named
INCONCLUSIVE gaps; malformed nonempty references still refuse.

This implementation supplies the raw-capture and task-decision connection described
in the [native contract](native-replay-contract.md). It does not close the remaining
isolation, protected regression, environment, repeatability or effect proofs above.
The live H0/H0 observation is recorded separately in LESSON; the original A5 fixture
controls remain declared-readback evidence.
