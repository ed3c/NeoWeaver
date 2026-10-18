# NeoWeaver — Harness² + Agent RL environment view interface

Status: **PROPOSED / read-only contract only** (2026-10-18).

## Original requirements stay in force

This extension references [the original ten logical requirements](specs/learned-harness-coevolution.md) and its current typed TaskSnapshot / RolloutObservation / PairedReplay / RewardObservation / TransferArtifact contracts. It creates no owner, scheduler, rollout executor, reward calculator, training gate, model-update authority or second task state machine. Preserve original Source/Env/Verifier/Dataset/Trainer/Transfer owners and opaque references. Any absent evidence is UNKNOWN, never zero or PASS.

## Sources and distinct semantics

- **Harness²**: [google-research/harness2](https://github.com/google-research/harness2) at \`1cfe254e8d25b15f37048c3730134686abe60335\` (Apache-2.0). Task-level **Propose → Probe → Compose** and harnessing-level persistent improvement operate on eight harness surfaces: system prompt, guardrails, memory, tool guidance, subagents, skills, scripts and plugins. Published framework holds model weights fixed in its harnessing experiments. Do not re-label this as RL training.
- **FineEnvs**: [adithya-s-k/FineEnvs](https://github.com/adithya-s-k/FineEnvs) at \`410fb3454a903646f814bb752513c56fed3eae78\` (Apache-2.0); requested [Hugging Face Space](https://huggingface.co/spaces/FineEnvs/simulation-rl-environments) is a visual reference, not proof of a specific API. Consider OpenEnv / OpenReward ORS / Verifiers / NeMo Gym as *environment adapter options*. These differ in transport and reward timing; no universal episode exporter is assumed.
- **Loop Studio UI**: the proposed medium-compiler \`docs/loop-studio-design-contract.md\`, \`contracts/loop-ui-artifact-v1.schema.json\`, and optional TanStack Start frontend. Rendering does not cause an environment step or Trainer update.

## Data flow, not an execution pipeline

\`\`\`text
Original Repo Source / TaskSnapshot / permissions
     -> Original Environment Owner: Reset + Step + terminal/partial observations
     -> Original Observer + Verifier: truth/readback and hard gates
     -> [optional] original Harness² task probe / harness improvement evidence
     -> [optional] original RL reward / dataset eligibility / Trainer evidence
     -> READ-ONLY EpisodeViewV1 sidecar (existing opaque refs only)
     -> reviewed disclosure (if public) -> TanStack Start Loop Studio inspector
\`\`\`

A future sidecar must consume original immutable readbacks. It cannot serialize a whole private trace into the cloud. The existing \`neoweaver.learning.inspect_training_candidate\` remains the sole supported A6 eligibility gate, not a UI-derived shortcut. A diagram is not an RL environment.

## EpisodeViewV1 proposed input
See \`../contracts/episode-view-v1.schema.json\`. Fields are references or explicit unknown:
- \`original_refs\`: Owner-provided task, environment, source, consent/rights, and evaluation refs. Missing refs stay null and block only dependent views.
- \`episode\`: original reset, step list of observation/action/step receipt refs, terminal ref or null; ordering supplied by original Episode Producer. A step ID from an animation is forbidden.
- \`harness\`: baseline/candidate refs, one of eight mutation surfaces, task-level/harnessing-level label, original comparison readback or null. No optimization or improved outcome claim without paired observations.
- \`learning\`: model/policy refs, true train/validation/held-out partition, original reward/verifier refs and eligibility result; missing numeric rewards stay null, never inferred. Codex frozen inference and open-weight training are distinct.
- \`display\`: \`PROPOSED\`, \`OBSERVED\`, \`UNKNOWN\`, \`INCONCLUSIVE\` original status plus evidence gaps. These are label projections, not validity or acceptance.

## Integration boundary
1. **Harness adapter** (future): source-bound identity bridge for harness candidate and probe readbacks. No arbitrary Python execution on public UI and no harness patch application on display actions.
2. **Environment adapter** (future): exact native Reset/Step/Verify/terminal and environment-version evidence, per supported protocol, including deterministic seed and timeouts. No guessed endpoints.
3. **Validation**: independent acceptance and protected regressions, negative controls for stale/fabricated episode refs, unseen completion and unsupported adapter. Do not reward UNKNOWN, and do not train on held-out data.
4. **Visualization**: use the existing Loop v2 Graph as the main evidence topology and one explicitly referenced EpisodeView side panel. Components render physical process as a source-linked *metaphor* via Anatomy; motion is not telemetry.
5. **Transport/deployment**: local Host and public reviewed snapshot stay isolated. TanStack Start routes \`/experiments/$experimentId\` are reserved until real backend capability, source permission, SSR security, and browser acceptance exist.

## Acceptance matrix
- Readable external specification and syntactically valid sidecar schema: **SOURCE ONLY**.
- External Harness² binary installed or real Codex probe executed: **NOT_RUN**.
- FineEnvs environment constructed, reset/step receipts verified: **NOT_RUN**.
- Trainer rewards / native Agent RL improvements: **NOT_RUN**.
- TanStack Start production rendering from an authorized public snapshot: **NOT_RUN**.
- Tested two-way runtime or cross-repo write adapter: **NOT_RUN**.

**First actionable engineering gate:** select one existing NeoWeaver failure + real original Environment Owner, produce one complete disposable baseline episode with honest verification and negative control, then decide whether a read-only view adapter is warranted. Don't install two RL stacks just because a visualization can show them.
