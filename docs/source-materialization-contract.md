# A5 Git Source Materialization — source copies, not native replay

`neoweaver.snapshot.materialize_source_pair(root, commit, destination)` consumes an **existing exact Git HEAD** and materializes every regular tracked Git blob into two new directories (`baseline/` and `candidate/`). This implements one bounded source-preparation step after the Parser and `inspect_pair()` readback gate.

## Preconditions and evidence

- The input must be a **clean Git repository root** at the supplied 40-character commit. The helper obtains HEAD, Git Tree and status from Git; the caller explicitly chooses a new destination outside the source checkout. No Issue, TaskSnapshot, runtime argv or credential is inferred.
- Read content through `git ls-tree` and `git cat-file blob`, not the worktree or `git archive`. This preserves tracked bytes even if `.gitattributes` uses `export-ignore` or `export-subst`.
- Only regular tracked files (Git mode `100644` / `100755`) are accepted. Symlinks, submodules, unsafe/duplicate paths, bad refs, stale/dirty source, non-root checkout and preexisting output refuse. Total file count and bytes are bounded.
- `StagedSourcePair` returns the original Git commit/tree, separate baseline and candidate `StagedSource` records. Each record contains its directory and a `SourceManifest` with the computed digest, per-file SHA-256, and executable bit. Both manifests initially describe the same Git blobs. Edits to one copy do not edit the other or the source checkout.
- If interrupted after destination creation, inspect the original owner-selected output before any cleanup/retry. The helper does not erase or overwrite unknown prior writes.

## Bounded candidate treatment

`apply_candidate_treatment(pair, proposal, binding)` is the same staging Producer's bounded write boundary after `parse_proposal`. `TargetBinding` comes from the original caller. It fixes the source commit, snapshot reference, opaque target and expected-source references, tracked relative path, expected bytes, and protected paths. The function compares references as data. It does not derive paths from reference strings or establish authorization from a proposal.

Before writing, the function validates both staged copies against their original manifests. It refuses a stale source binding, stale expected bytes, protected path, unsafe path, symlink, overlapping stages, or previously applied treatment. It replaces only the candidate target with the proposal's UTF-8 bytes and preserves the file's executable bit. The candidate manifest is derived by replacing that one original entry. Other hashes are retained, rather than accepted from a scan of changed files. The original Git checkout and baseline remain untouched.

`validate_source_pair` checks the complete file lists, content hashes, and executable bits of both arms. Transport and inspection consume this check even when only H1 is selected. Later baseline or candidate drift cannot be incorporated into a new valid manifest by another treatment call. A failed or interrupted local write requires original Owner readback before any retry.

The public API and source controls are described in [Candidate treatment](candidate-treatment-contract.md). These Python records are trusted caller data, not an authentication or admission framework.

## Evidence ceiling

`status=FILESYSTEM_COPIES_ONLY`, `authorizes_execution=false`, `authorizes_landing=false`. Two directories are **not** process/network security isolation. This helper executes Git reads and local staging writes, but never executes a task, runs a model, selects an Agent playbook, issues Provider effects or produces native `RunReadback`. A structural source-pair receipt cannot establish independent acceptance or causal improvement.

## Required next gate

The original TaskSnapshot/Environment Owner must still freeze the actual task, source/environment, Solver, seed policy, budget, immutable oracle and rights. A separately authorized Runner must execute two *actually isolated* arms and produce distinct raw run/sandbox/capture references plus terminal observations. Only those may feed existing `neoweaver.replay.inspect_pair()`, followed by independent verification against original protected gates. Native replay PASS, A6 Training Eligibility and A7 Frozen Codex Transfer remain **NOT_RUN**.

`python -m unittest discover -s tests -v` includes real temporary Git object controls for matching copies, distinct writes, `.gitattributes` export rules, symlink refusal, stale/dirty source and existing-output refusal. These are implementation controls, not a live TaskSnapshot or fresh Native Agent capture.
