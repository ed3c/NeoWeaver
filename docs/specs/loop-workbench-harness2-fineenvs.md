# NeoWeaver ↔ Loop Workbench ↔ Harness² / FineEnvs

Status: proposed, read-only UI bridge with a fail-closed source projection.
There is NO Trainer, Harness² executor binding, native RL episode or performance
gain in NeoWeaver yet. Do not present this as an active integration.

## Existing authoritative planes

Soodles: issue/admission/execution/acceptance/owner continuation.
Noodle: native Host, worktree, worker isolation, user review and original ACK.
NeoWeaver: TaskSnapshot, PatchProposal, RolloutObservation, PairedReplay,
VerificationResult, RewardObservation, TrainingBatch and TransferArtifact.
Medium-compiler/TanStack Start: read-only visualization of selected, already
reviewed public references. No cloud control plane or extra scheduler.

All references must be opaque strings issued by original Producers. A UI
projection does not manufacture SHA, PR head, PID, tool argv, episode ID,
observation, logprob, missing steps, readiness or reward. Selected refs are
not evidence of consumption.

## Harness² adapter: conceptual, not executed

Pin the researched upstream google-research/harness2 commit:
1cfe254e8d25b15f37048c3730134686abe60335
(Apache-2.0, subject to its third-party benchmark/dataset licenses).

Original Harness² task recursion = Propose → Probe → Compose:
- Propose: Harness² candidate intent to a NeoWeaver bounded PatchProposal
  only after source-bound FailureScope and original mutation allowlist.
- Probe: isolated baseline/candidate run to original Snapshot Runner
  RolloutObservations. Harness² probe outputs do not certify acceptance;
  independent protected oracle verification remains required.
- Compose: accepted candidate and original verification to an Owner-reviewed
  TransferArtifact; composition alone does not grant deployment rights.
- Reflect: evidence-supported lesson to original Lesson lineage. Harness²
  persistent improvement harness is not a second NeoWeaver state owner.

Harness² expressly optimizes harness components with frozen model weights;
NeoWeaver's optional open Solver training is a separate proposal with valid
own-token generation lineage. Never derive gradient samples from Codex
transcripts without original token provenance.

Security discriminator: public Harness² repository says executors can have
unrestricted network and Codex sandbox disabled. NEVER run its default task
executor on private/held-out test tasks or production credentials. Require a
disposable sandbox, network restrictions, rights review, separate immutable
verifier and original Host authorization first. Benchmark answers/rubrics
must not leak into the agent's task channel.

## FineEnvs adapter: episode semantics

Pin adithya-s-k/FineEnvs at 410fb3454a903646f814bb752513c56fed3eae78.
Its Simulation RL Environments / PortSimEnv example is an inspiration for
deterministic tasks and state-action-observation-reward contracts, NOT a
simulation of NeoWeaver's actual workflows.

Task/dataset: original TaskSnapshot and dataset split.
Action: one original owner-admitted bounded PatchProposal/tool action.
Observation: original effect readback and RolloutObservation refs.
Backend/state: scoped disposable replay with original environment snapshot.
Reward: original independent verifier/ref; null on missing or unknown result.
Termination: owner-observed completed/truncated/unknown.
Repeated observations keep their true episode order. The UI may show a
recorded negative result; it cannot invent the counterfactual reward.

The bridge JSON schema (contracts/loop-workbench-evidence-v0.schema.json)
is a viewer exchange, NOT a new persistent task, training or delivery status
machine. The Python projection is pure and refuses incomplete reward proof.
An adapter writing actual source files is intentionally absent.

## User-visible surface and future TanStack Start routes

/loops: Goal → Repo → Run → isometric original DAG → source inspector.
/environments: Task, Actions, Observation, State, Reward, Termination,
/replay: baseline vs candidate paired traces and normalized cost/validity,
/harness: Propose–Probe–Compose results and persistent lesson lineage.

The first TanStack Start isolated preview is in medium-compiler
apps/loop-workbench; its environment cards are intentionally NOT CONNECTED.
Future server handlers must not forward opaque UI IDs into owner effects.
If private execution UI is later authorized, its server must authenticate the
Session and call the original Owner request/readback interface; separate user
consent and hard gates still apply. Public hosting remains readonly.

## Acceptance tests before saying integrated

1. Original Producer and Consumer refs resolve without readback drift.
2. Negative cases: mismatched run/episode/actor, missing verifier, foreign
   model tokens, leaked held-out task, unauthorized capabilities and unknown
   effects all refuse or remain UNKNOWN.
3. Same task/environment/budget/seed policy paired replay plus independent
   verifier and protected regression readback; Cost per Verified Task is
   computed only from available original measured components.
4. Noodle native Stage consumption, feedback and Soodles next consumption
   verified separately. Whole Goal requires complete requirements coverage.
5. Browser confirms original IDs, no false green edge/reward and no exposed
   private source. Local/Cloud geometry parity requires separate tests.

Upstream:
https://github.com/google-research/harness2
https://github.com/adithya-s-k/FineEnvs
https://huggingface.co/spaces/FineEnvs/simulation-rl-environments
https://tanstack.com/start/latest
