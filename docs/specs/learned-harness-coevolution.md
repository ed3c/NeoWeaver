# SPEC — NeoWeaver Learned Harness Co-evolution

Status: PROPOSED; implementation and native proof NOT_RUN.
Source of requirement: user-requested Frozen Codex transfer and Harness/Policy co-evolution.
Source contracts: [FactoryWeaver v7.2](https://github.com/ed3c/factoryweaver/blob/main/skills/factoryweaver/SKILL.md), [Prompt Carrier Contract](https://github.com/ed3c/factoryweaver/blob/main/references/prompt-carrier-and-ownership.md), [verify-factoryweaver](https://github.com/ed3c/factoryweaver/blob/main/.cursor/skills/verify-factoryweaver/SKILL.md), [Soodles AGENTS](https://github.com/ed3c/soodles/blob/main/AGENTS.md).

## Goal / Measurement / Persistence / Stop
- **Goal:** Train a bounded Harness Patch Proposer and optionally an open-weight Solver, then transfer accepted patches to native *frozen* Codex through actually supported Skills/MCP/plugin capabilities. Never claim Codex weights changed.
- **Measurement:** compare fixed task, environment, solver, seed and resource budget; record completion receipts, protected regressions, decision count, token/tool/latency costs, and held-out transfer. Success requires no hard-gate violation and repeatable positive paired effect; no numerical gain is assumed.
- **Persistence:** original task, source references, hypotheses, patch and immutable acceptance receipts remain accessible to their consumers. IDs, hashes, commit heads, argv and timestamps belong to producers; never model-authored.
- **Stop:** unknown effect -> original owner readback; missing capability -> NOT_RUN/BLOCKED; regression -> reject and roll back; no observed benefit -> NOOP. Do not create a second scheduler/owner/verification truth.

## REQ and SPEC — logical cards (proposals, not v1 registry records)
| Requirement | Mechanism / constraint | Proof and counterexample |
|---|---|---|
| REQ-01 Source integrity | Preserve actual Issue Goal, acceptance, Repo snapshot, training rights and full original REQ inventory | A generated summary cannot authorize a merge |
| REQ-02 Three planes | Learning may propose, Execution may sandbox, independent Verification determines acceptance | Self-reported success is a rejection |
| REQ-03 Trainability | Candidate has bounded mutable surface and patch parser, reproducible task and replay | Arbitrary source rewrite without replay is not RL-ready |
| REQ-04 Two policies | Proposer πθ modifies Harness; optional open Solver πφ is trained only with valid own token provenance; Codex φC stays frozen | Codex transcript cannot be treated as Proposer policy-gradient tokens |
| REQ-05 Causal attribution | A=H0/φ0, B=H1/φ0, C=H0/φ1, D=H1/φ1; separate frozen Codex H0/H1 transfer | Improvement in D alone cannot identify cause |
| REQ-06 Scoped patch | Only observed failure supports a single causal target; capability probe before generating plugin patch | Proposed unsupported native Hook must be rejected |
| REQ-07 Plugin transfer | Verified artifact maps solely to capability-proven Skill, MCP wrapper, or supported lifecycle interface | Proposal != installed or consumed plugin |
| REQ-08 Full lifecycle | Soodles Outer chooses only real needed method and admission; Noodle Poteto receives bounded delta and implements freely; Test/Schema results read back; provider owns effects | Writer-complete != merged/receipted goal |
| REQ-09 Learning dataset | Training/validation/held-out partition; trace refs preserved; producer binds rollout/action/reward; legal rights for code/data/model/trace checked independently | A sample with guessed tokens, leaked held-out tests or noncommercial rights is ineligible |
| REQ-10 Lesson lineage | LESSON.md references observed issue/commit/PR relations and actual rework edges, distinguishing unknown from observed | Do not invent SHA, DAG edge or closure |

## SPEC — handoff and first-inference-breakpoint map
| Hop / carrier | Producer → Consumer | Permitted reasoning | Deterministic rule / refusal |
|---|---|---|---|
| 0 Requirement & AGENTS | Original user/source → selected Session | Interpret goal; preserve unknown premises | Unread sources remain K, referenced skill is not loaded skill |
| 1 REQ/SPEC/card | FactoryWeaver compiler → independent reviewer | Mechanism, counterexample, typed knowledge links | v7.2 shape via original tools; semantic truth separate |
| 2 Scope/Prompt Delta | Accepted source → Soodles Session | Single causal atom; NOOP if next known | Original Issue contract/admission owns next and effects |
| 3 Task snapshot | Original Environment → Frozen solver | None for IDs/heads | Same task, budget, base and provider simulation |
| 4 Baseline trace | Frozen solver → Observer | Candidate cause only as hypothesis | Raw ordered events + refs; no invented log |
| 5 Failure scope | Observer/Session → Proposer | Select evidenced target within allowlist | Unobserved failure -> NOOP, unknown provider -> readback |
| 6 Patch proposal | πθ → Parser/Validator | Generate change only in selected target | Typed parse, static check, sandbox/capability; fail closed |
| 7 Paired replay | Snapshot runner → independent Verifier | No success self-certification | Baseline & candidate separate isolated copies; negative controls |
| 8 Reward | Verify owner → Trainer | Decide learning policy from verified outcomes | Hard gates before soft reward; token/action/reward attribution |
| 9 Alternate model update | Trainer → open Solver / Proposer | SFT/GRPO policy adaptation | Freeze counterpart per ablation, no held-out leakage |
| 10 Codex transfer | Accepted artifact → capability adapter → Frozen Codex | Choose minimal supported mapping | Actual plugin/Skill/MCP probe, native fresh-consumer capture |
| 11 Delivery & lessons | Outer owner/Provider → effect readback → LESSON.md | Analyze first false premise and rework | Provider outcome != CI != writer-complete; return original next |

## P-class / CLI state contracts
- Session carries semantic Goal/authorization and selects only a genuinely unresolved thinking condition. P-class describes conditional guidance, never grants effects. A real CLI owns legal transitions, generated input identities, exact next argv and unknown-effect readback.
- Soodles Outer Loop selects original issue contract, admissions, necessary pstack/ponytail/waza checks. No automatic outer-skill invocations solely because a card mentions them.
- Noodle Poteto Inner Loop consumes a bulleted accepted Goal, affected callers, non-cases, acceptance, one Prompt Delta, preselected playbook and writer exit. It can freely implement within that admitted scope; it cannot redefine original acceptance.
- Test Manager selects focused positive and discriminating negative controls once. Schema Manager consumes observed feedback and provides typed next; original Owner/Provider certifies delivery. Hook only on native event; Cron only on existing authorized schedule.
- Every hop supplies exact producer-issued references; consumer never re-derives digests, IDs, credentials, commit heads, replay arguments or decisions already supplied by owner.

## Acceptance evidence and verification
1. **Specification:** inspect actual source, lossless REQ coverage, card meaning, typed causal links, counterexample, goal & non-cases. FactoryWeaver v7.2 CLI shape PASS is not semantic PASS.
2. **Reader/CLI:** original FactoryWeaver exporter/reader and scoped Soodles CLI, fixed bytes, refusals and selected consumer readback. Read-only Reader is not admission.
3. **Native:** fresh Agent uses saved P-class bytes, original outer admission, Noodle stage consumption, necessary Test/Schema feedback, capability-proven plugin, Frozen Codex replay and provider readback. Preserve precise proof ceiling.
Run the upstream verify-factoryweaver doctor/feature-map maintain repeatedly *in an executable checkout*. A GitHub connector cannot execute its local Python verification. Mark all such checks NOT_RUN until captured.
Do not invent additional feature-map entries unless a distinct observable boundary is demonstrated; otherwise update original mapped feature.
