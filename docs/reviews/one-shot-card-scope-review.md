# NeoWeaver 44-Card / Behavior Scope Review — Session-composed One-Shot Prompt

This is a source-backed **review artifact**, not an accepted Registry rewrite, execution authorization, or native Agent evaluation. The source of the original full 10 REQ, 44 Card contents and exact scope membership remains `docs/compiled/specification.json`, `docs/compiled/card-proposals.json`, and `docs/compiled/semantic-sidecars.json`. The historical compiled verification file is immutable evidence. Current parser evidence is separately recorded at `docs/parser-verification.json`.

## Review rules and source-of-truth boundaries

- R Roadmap suggests units and known existing Card references; it cannot schedule execution. Session can choose an earlier observed failure or different minimal sufficient scope.
- Card-generation feedback repairs **the first incorrect premise in the original Card producer** during compilation, before independent source-semantic acceptance. It is **not** the existing Stage `PromptDelta`.
- Session uses accepted REQ/C/G/S/SPEC/V plus current Source/Owner readback to compose a *consumer-specific* One-Shot Prompt: observable Goal/local clauses, inputs, refusal/non-cases, original oracle, stop boundary and free implementation choice. Do not concatenate full Card prose.
- Only the original Host/CLI validates existing Card ID bindings, revisions, source and owner next; do not ask an Agent to invent digest, paths, argv, IDs, measured costs or timestamps.
- A Card count or typed-link shape cannot prove semantic completeness. Selected Parser scope does not close parent REQs, replay, Trainer, Native Transfer or Provider delivery.

## R39 source-backed entry correction in current candidate

The original R39 had one direct link, `based_on → S38`. This current
candidate retains it and adds `based_on → SPEC-trainability-boundary`
to identify the Parser unit's **local ParsedProposal/DiagnosticRefusal exit**.
R39 revision advances from 2 to 3; the full ten parent requirements and
other 43 Card identities/semantics remain unchanged. SPEC08 itself has the
V09/C31/G33/G34 links. R39 does *not* redundantly list those as direct
entries or imply any transitive Scope closure.

This Card revision changes the current proposed knowledge record, not the
original historical compiled verification receipts. It cannot establish a
native Noodle Stage, fresh P-class behavior, Trainer or frozen Codex transfer.
Remaining R units need source-grounded entry review if Session selects them.

## Full 44 / 44 Card review

The scope-role column is copied as existing semantic classification from the original scope sidecar; it is **not** a newly inferred runtime state. `KEEP` means preserve the present boundary, `REFINE` indicates a source-level or future revision recommendation, not that source files were already updated.

| Existing Card | Series | Related Behavior Scope | Current Parser scope role | Review | Claim / correction at the earliest boundary |
|---|---|---|---|---|---|
| `REQ-source-integrity` | REQ | Source integrity | `context_only` | KEEP | Source inventory and immutable Goal references must stay complete; the parser atom covers only fixed reference preservation. |
| `SPEC-source-integrity-boundary` | SPEC | Source integrity | `context_only` | KEEP | Source Reader returns MappedUnit/NamedGap; no parser execution or permission is inferred. |
| `V-source-integrity-discriminating-controls` | V | Source integrity | `context_only` | KEEP | A fixed source-unit set plus changed TaskSnapshot or weakened acceptance must defeat a coverage-count-only PASS. |
| `REQ-three-planes` | REQ | Three-plane isolation | `context_only` | KEEP | Parent requires independent Execution and Verification; parser non-effects meet only an initial clause. |
| `SPEC-three-planes-boundary` | SPEC | Three-plane isolation | `context_only` | KEEP | Preflight returns ParsedProposal/DiagnosticRefusal, not Runner or VerifierResult. |
| `V-three-planes-discriminating-controls` | V | Three-plane isolation | `context_only` | KEEP | Protected-oracle mutation refuses locally; sandbox isolation and independent runtime acceptance remain unobserved. |
| `REQ-trainability` | REQ | Trainability / Replay | `context_only` | KEEP | Trainability retains task replay and bounded training beyond current parser completion. |
| `SPEC-trainability-boundary` | SPEC | Pure parser / Refusal | `local_exit` | REFINE | Use actual `parse_proposal(raw, fixed_inputs)` mapping and opaque Owner refs; do not imply parser deserializes a TaskSnapshot object. |
| `V-trainability-discriminating-controls` | V | Pure parser / Refusal | `local_control` | REFINE | Bind 28 scoped Parser tests via separate current evidence; do not rewrite historical compiled NOT_RUN or claim replay. |
| `REQ-two-policies` | REQ | Policy eligibility / Trainer | `deferred` | KEEP | Proposer, optional Solver and frozen Codex require actor-specific token provenance and distinct update ownership. |
| `SPEC-two-policies-boundary` | SPEC | Policy eligibility / Trainer | `deferred` | KEEP | EligibleTrainingSample is dataset output; model update and frozen counterpart are later Trainer readbacks. |
| `V-two-policies-discriminating-controls` | V | Policy eligibility / Trainer | `deferred` | KEEP | Foreign actor tokens, mismatched reward/split and Codex updates must fail independent eligibility/Trainer checks. |
| `REQ-causal-attribution` | REQ | Causal evaluator | `deferred` | KEEP | Four matched experiment arms and separate frozen Codex paired transfer are preserved as parent acceptance. |
| `SPEC-causal-attribution-boundary` | SPEC | Causal evaluator | `deferred` | KEEP | A/B, A/C and four-arm interaction have different evidence minima; matched A/D yields joint total only. |
| `V-causal-attribution-discriminating-controls` | V | Causal evaluator | `deferred` | KEEP | Never infer component effects or whole-Goal repeatability from D alone or mismatched conditions. |
| `REQ-scoped-patch` | REQ | Failure hypothesis selection | `context_only` | REFINE | Scoped patch requires observed failure and causal hypothesis; distinguish this rule from the proposed bootstrap parser implementation. |
| `SPEC-scoped-patch-boundary` | SPEC | Failure hypothesis selection | `context_only` | KEEP | FailureScope is an upstream observed-hypothesis boundary, not the parser result or measured causal benefit. |
| `V-scoped-patch-discriminating-controls` | V | Failure hypothesis selection | `context_only` | KEEP | Unrelated allowed target and unknown prior write are discriminating negatives; Reader/Owner facts remain mandatory. |
| `REQ-plugin-transfer` | REQ | Frozen Codex adapter | `deferred` | KEEP | Mapping accepted artifact to capability-proven interfaces is not native transfer consumption. |
| `SPEC-plugin-transfer-boundary` | SPEC | Frozen Codex adapter | `deferred` | KEEP | Adapter MappingProposal cannot claim installation, Host load, Hook execution or effects. |
| `V-plugin-transfer-discriminating-controls` | V | Frozen Codex adapter | `deferred` | KEEP | Fresh instruction/consumer use and independent effect must be separately observed; a prior Stop event is not learned-patch transfer. |
| `REQ-full-lifecycle` | REQ | Soodles / Noodle lifecycle | `deferred` | KEEP | Writer completion and selected Manager readback cannot replace Provider or parent result. |
| `SPEC-full-lifecycle-boundary` | SPEC | Soodles / Noodle lifecycle | `deferred` | KEEP | Original Issue/Stage/Test/Schema/provider continuations remain separate; conditional managers are never compulsory. |
| `V-full-lifecycle-discriminating-controls` | V | Soodles / Noodle lifecycle | `deferred` | KEEP | Verify real admitted Stage/Delta consumption, necessary tests and schema next consumption, then applicable Provider receipt. |
| `REQ-learning-dataset` | REQ | Dataset eligibility | `deferred` | KEEP | Dataset rights, train/validation/held-out separation and action/reward lineage remain hard gates. |
| `SPEC-learning-dataset-boundary` | SPEC | Dataset eligibility | `deferred` | KEEP | TrainingBatch is eligible train-only data, not evidence of update; leakage requires source-aware review. |
| `V-learning-dataset-discriminating-controls` | V | Dataset eligibility | `deferred` | KEEP | Change only actor/reward/split/rights premise to discriminate quarantine; no fabricated training success. |
| `REQ-lesson-lineage` | REQ | Rework provenance | `deferred` | KEEP | Rework DAG needs observed Source/Issue/Commit/PR and first wrong premise, not inferred history. |
| `SPEC-lesson-lineage-boundary` | SPEC | Rework provenance | `deferred` | KEEP | FactoryWeaver reconciliation and NeoWeaver native implementation are distinct Source/Consumer histories. |
| `V-lesson-lineage-discriminating-controls` | V | Rework provenance | `deferred` | KEEP | Chronology plus successful CI does not establish a causal repair; require failure/diff/after-control. |
| `C-independent-immutable-verification` | C | Cross-scope immutable verification | `constraint` | KEEP | Immutable verifier oracle must be independently fixed; current parser inherits protected-target restriction only. |
| `C-actor-scoped-credit-assignment` | C | Policy eligibility / Trainer | `deferred` | KEEP | Actor/action/reward lineage concept applies to Trainer, not current Parser exit. |
| `G-cards-preserve-original-effect-ownership` | G | Cross-scope effect ownership | `constraint` | KEEP | Proposal/Card/Reader cannot grant native effects; preserve as reused constraint, not repeated task delta. |
| `G-hard-gates-precede-reward` | G | Cross-scope acceptance gates | `constraint` | KEEP | Hard gates precede reward; parser only inherits protected-acceptance rule, not all reward-training checks. |
| `T-harness-only-versus-joint-policy-update` | T | Causal evaluator | `deferred` | KEEP | Harness-only and optional joint comparison require matched task/population/budget; never force full factorial for parser. |
| `E-joint-result-does-not-identify-a-component-effect` | E | Causal evaluator | `deferred` | KEEP | Joint total under A/D does not identify components; conditional proof is not a universal causal law. |
| `Q-choose-the-first-evaluation-population` | Q | Measurement population | `deferred` | KEEP | Read original chosen evaluation population first; unknown selection blocks replay/performance, not local parser. |
| `S-start-at-the-patch-acceptance-boundary` | S | Pure parser / Strategy | `strategy` | REFINE | The three-failed-corrections stop clause needs its actual applicable Session policy; do not install a universal parser retry counter. |
| `R-verify-a-bounded-delivery-sequence` | R | Parent Roadmap / Scope discovery | `deferred` | REFINE | R lists causal phases but only links to S card; add justified existing card references for each proposed unit when revising R, without making scheduler/Stage next. |
| `P-repeat-a-matched-replay-safely` | P | Matched replay | `deferred` | KEEP | Practice replay requires actual runner/isolated environment and verified references; never promote Practice to Soodles P-class. |
| `N-factoryweaver-reconciliation-precedes-neoweaver-recompilation` | N | Historical FactoryWeaver source | `context_only` | KEEP | Historical FactoryWeaver sequence grounds source correction; none of its merges prove NeoWeaver Trainer. |
| `D-matching-raw-catalog-pin-still-allowed-duplicate-keys` | D | Historical parser counterexample | `context_only` | KEEP | Observed FactoryWeaver duplicate-key ambiguity supports Neo parser negative input but is not an observed Neo bug. |
| `K-training-data-and-token-provenance-unavailable` | K | Training prerequisite gap | `deferred` | KEEP | Unknown rights and own-generation tokens block dependent policy training; preserve independent parser work. |
| `K-native-codex-transfer-has-no-observed-consumer` | K | Native transfer prerequisite gap | `deferred` | KEEP | Missing native load/fresh consumer prevents transfer-success claim; only an actually required Hook needs event/trust. |

## Parser Scope: six selected Cards, not six total requirements

- `SPEC-trainability-boundary` (local exit): Owner-fixed input mapping plus raw Proposal → ParsedProposal or DiagnosticRefusal; no Replay.
- `V-trainability-discriminating-controls` (local control): valid input acceptance, duplicate-key/stale/protected/missing/extra-field negatives; actual current Parser tests are a separate evidence source.
- `C-independent-immutable-verification`, `G-cards-preserve-original-effect-ownership`, `G-hard-gates-precede-reward` (constraints): apply only current Parser-relevant portions. Do not copy all Learning Reward/Training clauses into the Writer prompt.
- `S-start-at-the-patch-acceptance-boundary` (strategy): parser bootstrap justified as a proposed engineering slice, not an observed native training failure.

The scope sidecar names four parent requirements (`REQ-source-integrity`, `REQ-three-planes`, `REQ-trainability`, `REQ-scoped-patch`) while keeping all ten parent REQs in continuation. The R card is a potential index of future causal scopes, **not** an automatically selected Noodle stage. The other 38 Cards remain context, constraints or deferred obligations as actually labeled; do not delete or silently promote their exits.

## Proposed One-Shot semantic projection for the current Parser Consumer

**Goal:** Correct the pure PatchProposal parser to accept only legal current single-surface edits and return an immutable ParsedProposal or named DiagnosticRefusal.

**Given:** The original `parse_proposal(raw: bytes, fixed_inputs: Mapping)` API, proposal schema, original Owner-fixed opaque references, allowlist and protected target list. The parser must not resolve these references into paths or substitute other producers' authorization.

**Required behavior:** Preserve successful legal input; refuse duplicate JSON keys, invalid encoding/number/string, stale expected source, missing/extra fixed inputs, protected/out-of-allowlist/causal-mismatch targets, multiple complete replacements with no ordering, credential/effect fields. Return the original named diagnostic, not a synthetic write result.

**Hard boundaries:** No Replay, Trainer, Host plugin installation, external Side Effects or claim of Provider delivery. Current Parser local acceptance is not the whole Trainability/Goal acceptance.

**Verification:** Consume the original focused Parser positive and negative controls, preserving raw bytes, exact refusal conditions and no-effects evidence. Original Test Manager remains the scope owner; one existing later verification result is not a new `PromptDelta`.

**Freedom:** Noodle/Session implementation choices, code structure and local correction sequence remain free within the actual admitted contract. Use the existing API/validation boundary; do not create a replacement factory, scheduler, or identity generator.

**Stop:** Return actual changed behavior, scoped tests and named blockers to original Stage Owner. Unknown prior effect must be read back before any retry. Do not fabricate `next.argv` or mark parent Goal completed.

This text is a **proposed semantic projection** and has not been observed as consumed by a fresh native Noodle Stage.

## Material follow-ups and discriminating controls

| Finding | First affected producer | Positive control | Negative control / proof ceiling |
|---|---|---|---|
| R Roadmap lacks complete candidate Card-index edges | R per-type semantic generation and accepted R revision | Existing verified Scope references can be found without inventing identities | A prose R order alone does not imply card selection, admission or execution |
| SPEC08 opaque reference contract may be read as decoded Snapshot | SPEC per-type prompt / Neo parser spec | Actual raw/fixed mapping accepted | Any claim of parser reading the referenced file requires an actual Runner Source/Owner observation |
| V09 current Parser PASS appears only in later evidence | Scoped evidence reader, not immutable old compilation | 28 Parser controls recorded separately | Do not turn historical `NOT_RUN` into native `PASS` |
| S38's three failures may be mistaken for parser retry counter | Current applicable Soodles Session policy / strategy card | The real owner reassesses after its defined repeated failures | Do not invent automatic retries, attempt IDs, new Timer or universal counter |
| Parent Goal cannot be reduced to six selected cards | Scope Assembly and original Issue reconciliation | All 10 parent REQs remain in full record | No Parser success may close Replay, Dataset, Learning, Native Transfer |
| One-Shot instruction could omit G or promote deferred SPEC | Session prompt composition, independent source reviewer | Contains all applicable invariants and a local SPEC/V oracle | Missing protected-target constraint or adding Training-as-parser-exit is REVISE |

## Evidence and release ceiling

- Original source/card semantics were historically scoped-reviewed; this table is a current read-only content inspection and recommendation, not a fresh native Agent observation.
- Current `docs/parser-verification.json` reports Parser local test evidence. It cannot rewrite historical `docs/compiled/verification.json` `parser_implementation=NOT_RUN`.
- Native admitted Noodle One-Shot instruction consumption, P-class adherence, RL, frozen Codex transfer and whole Parent Goal remain unverified in this review.
- Change the actual compiled R/SPEC/V/S Card only through original FactoryWeaver compiler/delta and new review evidence. Do not hand-edit historical compiled JSON or mechanically increase revision IDs.
