# A6 Training Eligibility — declaration-only, no training

The existing original requirements **REQ-two-policies** and **REQ-learning-dataset** separate the Harness Proposer's action lineage, optional open Solver token lineage, frozen Codex traces, dataset rights/splits and independent reward evidence. `neoweaver.learning.inspect_training_candidate(candidate)` is a pure screening function over **Original Producer-supplied** records. It does not fetch any referenced payload, invoke a model, update weights, choose a Trainer, schedule retraining or grant effects.

## Actual producer / consumer boundaries

- `GenerationEvidence` comes from the original Generation Owner: actor, policy, observation, action, generation and optionally own-token references.
- `EvaluationEvidence` comes from the original replay/verifier/reward Owners: observation/action identity to match Generation, rollout, replay, independent verifier, immutable oracle and reward references, plus reported acceptance, protected-regression and external-effect states.
- `TrainingCandidate` carries the selected `train | validation | held_out | unknown` partition, `allowed | denied | unknown` rights decision and **separate original dataset partition/rights references**. These are opaque `OwnerRef` values, not paths, invented hashes, or model authentication credentials.
- `method` is `sft` or `policy_gradient`, as selected by the original training policy owner. Missing Proposer token reference is tolerated **only** for a proposed SFT source record; on-policy Proposer gradient use and every open Solver candidate need original token provenance. Frozen Codex transcript is never permitted as trainable policy-owned tokens.

## Four non-authorizing results

| Result | Conditions | Interpretation |
| --- | --- | --- |
| `REFUSED` | Malformed record, type or unsupported actor/status/method | No learning judgment |
| `BLOCKED` | Frozen Codex policy, validation/held-out update, denied rights, failed acceptance/protected regression, self-reported verifier, mismatched observation/action | Known declared hard gate violated; candidate must not enter training |
| `INCONCLUSIVE` | Unknown rights, split, gates or effect; missing required generation, token, replay, oracle, reward, or source reference | Original Owner readback required; **unknown is not zero or failure** |
| `STRUCTURALLY_ELIGIBLE` | Supported, internally matched declarations with train partition, source refs, rights declared allowed, protected gates declared pass | Merely consistent **claimed** data, not verified real inputs or update authority |

Every result preserves `eligible_for_training=false` and `authorizes_landing=false`. `evidence_ceiling=DECLARED_EVIDENCE_RELATIONS_ONLY` never changes. Referenced objects are not cryptographically attested; matching `OwnerRef` strings cannot prove actual ownership, data rights, independently observed reward, sandbox isolation, on-policy lineage or immutability.

## Objective discriminating controls

`tests/test_learning.py` verifies normal declared relation matching, frozen Codex refusal, withheld tokens on SFT/PG or open Solver, validation/held-out exclusion, rights denial and hard-gate precedence, missing/unknown data, self-verifier rejection, cross-observation/action mismatch, malformed references and absence of file/process/network side effects.

## Remaining real requirements

Before **any** update, the original Dataset Owner must inspect the actual rights and split receipts and protect held-out partition, the Generation Owner must supply genuine policy/action/token lineage, the Runner/independent Verifier must establish original replay and hard-gate results, and the Trainer must select its already authorized update method and rollback checkpoint. No full A5 physical run or A6 Trainer existed at this source-only correction stage. A7 Frozen Codex native transfer and repeatable paired effect are still unobserved; the ten parent REQs and old compiled evidence are unchanged.
