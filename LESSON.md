# LESSON.md — First Inference Breakpoint & Rework Playbook

Status: initial design baseline; no NeoWeaver implementation Issue, PR or execution claims are implied.

## Procedure
1. Read original Goal, REQ and source evidence; get original owner-provided next. Preserve unchanged next (NOOP).
2. For each actual Producer → Consumer hop record the input carrier, output carrier, observed consumer action, evidence and trust boundary.
3. Find the **earliest unsupported premise** (not the last visible failure). Distinguish OBSERVED / HYPOTHESIS / UNKNOWN / NOT_RUN.
4. Record a discriminating positive and negative case. Fix only one causal atom in its original owner; keep independent Oracle unchanged.
5. Run focused verify-factoryweaver shape/semantic/reader/native levels as available. Local-only PASS never upgrades native status. Re-drive impacted boundary after correction.
6. Connect evidence-backed Issue → commit → PR → rework Issue → correcting commit as a DAG. Never manufacture edge/metadata to complete the graph.
7. Record cost of repeated decisions/tests from normal execution and actual Schema Manager consumer readback. Stop if no observed barrier.

## Evidence record template
| Field | Required content |
|---|---|
| Goal / REQ | Source-backed goal and original acceptance |
| Hop | Producer, exact carrier, consumer |
| Premise | Original claim, assumption, counterexample |
| Outcome | OBSERVED / HYPOTHESIS / UNKNOWN / NOT_RUN |
| Correction | First break, single owner, bounded changed atom |
| Discriminators | Positive and negative runnable conditions |
| Proof | Spec / Reader CLI / fresh native / provider, each separately |
| DAG | Real issue URL, commit URL, PR URL, rework edge; unknown left blank |
| Next | Owner-issued next or named missing prerequisite |

## Baseline history
| Event | Issue | Commit | PR | Rework edge | Evidence |
|---|---|---|---|---|---|
| NeoWeaver specification initiation | NOT_OBSERVED | Pending current write receipt | NOT_OBSERVED | NONE_OBSERVED | User requirement + FactoryWeaver source contract |
| FactoryWeaver full maintain | NOT_RUN | — | — | UNKNOWN | Requires actual source checkout and native Soodles consumer |
| Frozen Codex learned patch transfer | NOT_RUN | — | — | UNKNOWN | Requires implementation, supported plugin capability and fresh replay |

## Explicit first-breakpoint hypotheses (not observed defects)
- Missing Task snapshot identity: source truth has not crossed into Environment; fix original producer, never prompt-compute hashes.
- Patch modifies validator: learned reward becomes self-reported; reject at immutable boundary.
- Codex plugin cannot intercept an action: stop at capability probe; route only through supported Skill/MCP interface.
- Token lineage missing: do not train solver policy from reconstructed transcript; train distinct proposer when valid generation tokens exist.
- PR completed but Issue receipt missing: writer exit is not provider delivery; request original owner readback.

Maintain this file after actual readbacks; log only proven commit DAG links and regression-caused rework.
