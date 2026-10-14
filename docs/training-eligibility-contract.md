# A6 Training Eligibility — direct inputs, no FileRef or Provider Authentication

The A6 screening input is one `TrainingCandidate`: `actor`, `method`,
`partition`, `rights`, `acceptance`, `protected_regressions`,
`effect_status`, `lineage`, `token_provenance`, `replay`,
`verifier`, and `reward`.

These are **task and evaluation facts supplied by the current Session or an actual
runtime**, not a second chain of opaque `OwnerRef`, FileRef, SHA-256, source
directories, or Provider-authentication metadata. The original Producer still
owns its truth; this module does not independently verify its inputs. It also
never asks an Agent to invent a digest, operation ID, provenance receipt,
runtime identity, credentials, or new approval steps.

## One deterministic decision

`inspect_training_candidate(candidate)` returns exactly one typed,
non-authorizing result.

| Status | Meaning |
| --- | --- |
| `REFUSED` | Invalid type or unsupported decision value |
| `BLOCKED` | Frozen Codex policy, validation/held-out, denied rights, acceptance/protected-gate failure, mismatched lineage, self-verification or failed replay |
| `INCONCLUSIVE` | Unknown rights, split, results, effect, lineage, replay, verifier or reward; missing policy-owned tokens for a method that needs them |
| `STRUCTURALLY_ELIGIBLE` | Supplied decision facts are internally consistent; not actual evidence of model trainability |

The SFT Proposer does not need an invented policy-gradient token reference.
Policy-gradient updates and open Solver training require available
policy-owned token provenance. Frozen Codex is never treated as a trainable
policy. No soft reward or cost can override a hard gate.

Every result retains `eligible_for_training=false`,
`authorizes_landing=false` and `evidence_ceiling=SUPPLIED_FACTS_ONLY`.
No Trainer, optimizer, model execution, real Dataset Rights reading, rewards,
native replay, rollback, or Frozen Codex transfer is performed.

## Removed overdesign

The former A6.1–A6.3 `neoweaver/evidence.py`, source FileRef and
`verify_owner_evidence` / `read_pinned_owner_evidence` stages had **no
authenticated Producer or real downstream Trainer consumer**. Extra file
digests, directory-FD security checks, matching `readback=observed` and
self-declared `OwnerRef` equality did not make the data true. They have been
deleted rather than maintained as new CI or Native Agent admission gates.

This change is scoped to **A6 eligibility**. Existing PatchProposal
mutation-boundary references and A5 replay matching identities are different,
already consumed contracts; they are not this unused A6 FileRef layer.

## Verification and future real work

`python3 -m unittest discover -s tests -v` covers one permitted declaration,
missing policy-owned tokens, refused frozen Codex/held-out/denied rights,
acceptance/protected regressions, lineage and verifier mismatch, unknown
outcomes and zero file/process/network side effects.

A real training run would still need actual Data, rights, matched replay,
independent acceptance, a configured Trainer/checkpoint and rollback. This is
a **product correctness requirement when training is actually requested**,
not a demand to build speculative Provider Authenticity or FileRef
infrastructure in advance. All ten original parent requirements remain open
until genuinely verified.
