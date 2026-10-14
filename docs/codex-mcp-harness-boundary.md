# Codex MCP original-owner tools and frozen-harness candidate experiment

Status: **source implementation candidate**, not a verified Codex plugin installation, Native Harness action, or SoL-Pi performance gain. The parent ten REQs remain in [learned-harness-coevolution](specs/learned-harness-coevolution.md); this document is one bounded REQ-07 tool-transport atom and does not alter the original acceptance.

## Why this atom exists

Natural-language instructions such as "use the selected Test Manager", "do not guess the next owner", and "read only the required evidence" can trigger wasted model choices. Those mechanically answerable steps should use the original registered Producer and a tool call. **The tool is not a second producer or workflow state machine.** Do not move truly semantic Scope choice, authorization, provider effects, Native Hook approval or acceptance into a model-shaped wrapper.

The first implementation lives at `plugins/codex-mcp/` and implements an **MCP stdio server** without additional Python dependencies. Its eight bounded read-only tools are:

| Tool | Original producer | Guaranteed narrow scope |
| --- | --- | --- |
| `bridge_capabilities` | Git source readback | Reports configured exact HEADs; no claim of live Codex capability |
| `soodles_test_plan` | `./soodles test --base SHA --plan` | One fixed, read-only Test Manager selection; no `--full`, no tests run |
| `soodles_cli_contracts` | `./soodles schema cli-contracts` | Original CLI inventory and control gaps, not native branch proof |
| `soodles_knowledge_inspect` | `./soodles knowledge inspect BUNDLE_SHA_REF` | Forwards existing Host-bound Bundle FileRef; refusal remains refusal, `next=null` grants no effects |
| `factoryweaver_project` | `scripts/factoryweaver.py` | `validate` / `project` / `route` on an existing repo-scoped knowledge record; no effect |
| `neoweaver_training_screen` | `neoweaver.learning.inspect_training_candidate` | Existing A6 eligibility from **supplied** facts only, never training authorization |
| `neoweaver_patch_parse` | `neoweaver.patches.parse_proposal` | Existing proposal parser with **supplied** fixed inputs only, never a committed patch |
| `owner_evidence_range` | Original immutable Soodles FileRef | Exact SHA-256 and root-bound byte-range read; no new archive, owner or digest assignment |

`*_source_not_pinned`, `*_head_mismatch`, `original_test_base_not_pinned`, `original_evidence_hash_mismatch`, `original_output_exceeds_bound_no_truncated_pass` are **refusals**, never a retry hint or PASS. The server does not execute arbitrary model-provided shell strings. It does not supply separate scheduler, hidden fallback, Provider or Soodles admission.

## Installation and pinning (user-controlled, not performed by this repository)

**Local Codex MCP CLI** (when the user has cloned all three sources):

```sh
codex mcp add neoweaver-owner-tools \
  --env HARNESS_NEOWEAVER_ROOT=/absolute/NeoWeaver \
  --env HARNESS_NEOWEAVER_HEAD=<CURRENT_NEO_HEAD_FROM_GIT> \
  --env HARNESS_SOODLES_ROOT=/absolute/soodles \
  --env HARNESS_SOODLES_HEAD=<CURRENT_SOODLES_HEAD_FROM_GIT> \
  --env HARNESS_SOODLES_TEST_BASE_SHA=<TEST_MANAGER_SELECTED_BASE_SHA> \
  --env HARNESS_FACTORYWEAVER_ROOT=/absolute/FactoryWeaver \
  --env HARNESS_FACTORYWEAVER_HEAD=<CURRENT_FACTORY_HEAD_FROM_GIT> \
  --env HARNESS_EVIDENCE_ROOT=/absolute/original-owner-evidence \
  -- python3 /absolute/NeoWeaver/plugins/codex-mcp/server.py
```

The placeholders are **real values to be read from the corresponding original owner**, not strings to paste literally or model-computed digests. To avoid leaking private repositories, configuration contains no credentials. If a repo is not connected, omit its environment bindings; its tools refuse and the others remain available.

**Portable Codex plugin:** `plugins/codex-mcp/plugin.json`, `mcp.json` and `skills/owner-tools/SKILL.md` declare the same local stdio server. The portable `mcp.json` uses `${PLUGIN_ROOT}/server.py`; it does **not** bundle the three original repositories. Their explicit source roots and pinning remain necessary. Plugin installation and user trust must be separately observed. See official [OpenAI plugins docs](https://developers.openai.com/plugins/build/plugins) and [Agent Plugins stdio MCP spec](https://agent-plugins.org/specification). Do not claim this package is submitted to the public directory or automatically deploys local scripts.

## Actual CLI Tool Call state and error mapping

An installed Codex MCP `tools/call` names one tool with a typed, closed argument shape. It never asks the model to construct a Shell command or choose a new CLI. `soodles_cli_contracts({})` delegates unchanged to the existing Schema Manager CLI. `soodles_knowledge_inspect({bundle_ref})` accepts only the **original Host-issued** absolute path + SHA-256 inside the configured evidence root, passes that pin unchanged to the original Soodles Reader, and returns its `next/effects/refusal` without alteration. The bridge does **not** hash arbitrary model-chosen text to synthesize a Source Ref.

A nonzero original CLI exit produces `status=OWNER_REFUSAL` and MCP `isError=true`. An original typed `refused/invalid` status is also an MCP error even if the command exited zero. Status `needs_scope` is a named non-terminal plan condition, **not** a PASS or permission to fall back to the full suite. A successful `tools/call` means only the read-only inspection completed; it does not upgrade source semantics, effect permission, Native Agent coverage or PR landing.

These are mechanically constrained read-only calls. `edit_and_verify`, reducer, ObservationPack, and Online Context Compact are **not** installed by this MCP. Codex native hooks require independent supported capability/trust/event evidence. The native frozen Codex vs installed bridge H0/H1 is still `NOT_RUN` until the actual installed Host invokes the tool and the original Owner result is captured.

## Important non-equivalences

1. **Action Fusion is not atomic or idempotent by default.** SoL-Pi's `then_run` combines a file mutation and a selected Bash tool into one Model Turn; it checks intervening file changes within its fused queue. It does not globally lock unrelated writers, deduplicate arbitrary build side effects or make a failed multi-step shell command transactional. The prompt example `writeFileSync + execFileSync + contentHash` cannot serve as Soodles's stable external operation/receipt.
2. **An MCP tool cannot automatically intercept all native Codex edit/tool-result events.** `PreToolUse` and `PostToolUse` require separately supported/trusted Codex Hooks and their actual event capture. This candidate installs no Hook. SoL-Pi's ObservationPack and native compaction remain Pi-specific unless a measured Codex Host hook path supports equivalent semantics.
3. **Large output is not silent success.** The bridge refuses original CLI JSON over its bounded output size. The caller should obtain the original authoritative FileRef and call `owner_evidence_range`; it must not rerun the original Producer to synthesize the same data. A receipt does not confer write authority.
4. **Training Eligibility is not training.** H0 Frozen Codex cannot be gradient-updated through this plugin; NeoWeaver's original `eligible_for_training=false` stays unchanged even when the supplied facts are structurally eligible.
5. **No new metadata pipeline.** Hashes, source versions, original context/event IDs and selected validation argv originate only with existing Producers. `owner_evidence_range` verifies an existing SHA rather than asking the model to generate one.

## Proposed future write-and-verify seam — not implemented

Implement `edit_and_verify` **only** inside an admitted Noodle Stage or its existing authorized command carrier, after tracing real callers. Require original authorization and one existing source-bound Test Manager selection; use a stable operation ID, CAS over the selected file version, original writer readback, single effect-owner deduplication, explicit test argv and persistent outcome. If the write outcome is unknown, reconcile before replay. Re-running tests may have side effects or nondeterministic outcomes; never promise identical execution results solely from a content hash. No arbitrary `verifyCommand` accepted from the Model.

For existing Soodles work, prefer its current `runtime.test_argv` / Manager continuation, not a second command selector. If direct `edit_and_verify` would require another authority layer without a real caller, keep this feature as `NOOP`.

## Frozen Codex versus SoL-Pi candidate measurement

| Experiment | H0 | H1 | Evidence claim |
| --- | --- | --- | --- |
| **Codex MCP treatment** | Same frozen Codex executable/model, current admitted tools | Same frozen Codex executable/model **plus installed MCP bridge** | Only MCP exposure changed; compare tool selection/correctness/cost with pinned task |
| **SoL-Pi mechanism** | Pi at its pinned upstream release, four mechanisms off | Same Pi version/model with exactly **one** SoL-Pi mechanism enabled | Mechanism-specific causal effect, provided the same task and resources |
| **Cross-host transfer** | Frozen Codex | Pi + SoL-Pi | Exploratory host comparison; **not** evidence the isolated SoL-Pi mechanism caused a difference |

Do not install the full SoL-Pi four-feature configuration into the production Soodles Writer to achieve parity. The upstream Pi extension is a distinct Harness; cross-host differences include tool affordances, model context and Host scheduling. For the mechanism experiment, turn on one feature at a time, pin Pi and SoL-Pi versions and retain the full configuration.

Maintain the NeoWeaver source specification's **H0/M0, H1/M0, H0/M1, H1/M1** causal accounting only when a genuinely trainable M1 is available. A frozen Codex transcript is data about Codex behavior, not valid Codex policy-gradient tokens. A controlled H0/H1 can measure Harness change while the Solver remains frozen.

### Acceptance controls for this atom

- Static Python source tests check MCP initialization, tools/list, real stdio tool/refusal, exact allowlists and protocol.
- Positive: original A6 screening, valid PatchProposal parse and bound recall preserve the original output meaning.
- Negative: unconfigured repo, stale HEAD, wrong Test Manager base, arbitrary execution attempt, traversal, stale patch, changed evidence bytes, non-UTF-8 byte slice and oversize original result are refused; no false-positive success.
- Next proof: run actual **fresh Codex CLI** with the installed MCP server on a source-pinned read-only task and capture the Tool Call plus original CLI readback. Then run the paired baseline. An install status alone is not native consumption.
- No checked Codex executable, Pi release/provider credentials or Mac host is available in this GitHub-only source task: these remain `NOT_RUN`.

The original Soodles Test Manager still selects necessary controls. `tests/test_mcp_bridge.py` is the immediate affected test scope; existing NeoWeaver CI may run broader original unit suites per its own pinned workflow, which must be reported separately. Plugin artifact and docs do not change `docs/specs/learned-harness-coevolution.md`'s ten original requirements.
