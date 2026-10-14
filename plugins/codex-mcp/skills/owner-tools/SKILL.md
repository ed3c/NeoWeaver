---
name: neoweaver-owner-tools
description: Call existing original-owner read-only CLI/Validator through a pinned Codex MCP adapter. Never infer effects, launch tests or create a second Soodles owner.
---

# Original-owner MCP Tools

Use this skill only when the installed Codex host actually advertises the `neoweaver-owner-tools` MCP connection. A named plugin or Markdown file alone is not capability evidence.

Call `bridge_capabilities` first. Exact source pinning is provided by the host environment; do not generate or guess a SHA or repository root. Missing and stale pins are a typed refusal, not permission to discover another owner.

The tools call **existing** owners:
- `soodles_test_plan` consumes the original Soodles Test Manager's `test --plan --base`. Never infer a PASS, execute a test, use `--full`, or alter the returned scope.
- `factoryweaver_project` uses FactoryWeaver's canonical read-only `validate`, `project`, or advisory `route`. Cards, System Prompt references, and route proposals do not grant task admission.
- `neoweaver_patch_parse` and `neoweaver_training_screen` reuse NeoWeaver's original typed validators. Supplied inputs are not independent Provider truth; neither output authorizes execution, training or landing.
- `owner_evidence_range` consumes an **existing** Soodles FileRef, validates source SHA and reads exact bytes within the configured root. It does not create another Acceptance Producer or evidence authority.

No arbitrary shell, filesystem writes, test execution, provider effects, automatic compaction or native Codex tool interception are exposed by this plugin. Actual write-and-verify behavior belongs to the original admitted Noodle Writer and existing Test Manager; it cannot be recreated by an unbound MCP edit command. Tool refusal requires the current Session to obtain missing original-owner inputs, not to retry a possibly completed side effect.

A SoL-Pi candidate is a **separate Pi Harness execution**, not Codex with an installed extension. Benchmark native Codex H0/H1 with the same frozen executable, model and workload; compare native Pi / Pi+SoL-Pi separately and report cross-Harness comparisons as transfer evidence, not one-mechanism causality. See `docs/codex-mcp-harness-boundary.md` in the NeoWeaver source repository.
