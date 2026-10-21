# Harness² 第一個實作單位與完整驗收追蹤

本次授權來自 2026-10-22 使用者要求「先確認實作授權，再依 Handoff 的最小實作順序推進」。
原 [Soodles #445 Handoff](https://github.com/ed3c/soodles/blob/092dfa94aae6c9888d055102e35479a18f64214d/docs/handoffs/2026-10-21-harness2/handoff.md)
只授權當時的文件交付。本次指示授權後續實作，沒有授權 merge、Promotion 或 activation。

本文件記錄 N-class 實作與觀察。它不是新的 admission、Agent 指引或效果收據。
原十項 NeoWeaver REQ、44 Cards、既有 Oracle 與 deferred RL 要求均保留。

## 本次範圍與選擇理由

Parent Goal 是在 NeoWeaver 保留完整、未修改的 Google Harness²，
以合法訂閱 CLI 執行原生優化，再交原 Soodles Owner 獨立驗證 Promotion。
本次先驗證 Handoff 第 2 步，再實作第 3 步的 data-only producer。
本機 dispatcher Source Candidate 另在 Soodles；live native runtime 尚未接通。

第一個 Source-supported 斷點是「安裝 Python wheel 就保留完整 upstream」。
上游 pyproject 只將 harness2 套件納入 wheel；原 repository 另外保有
Benchmarks 支援檔、third_party、dependencies、scripts、docs 與 LICENSE。
因此本次同時保留完整 pinned Git checkout 和原 Python 安裝，不修改 upstream。

Thinking Router 採 V2 Adversarial Review，核對錯誤來源與效果推論。
Ambitious 採 Depth，要求可重跑的原始實作觀察。沒有必須新增五方法檢視的前提，
條件式 V3 本輪為 NOOP。這是目前 Session 的方法紀錄，不是 CLI 或 native Agent invocation 證明。

原 Source-bound Prompt Delta 保留於 #445 第 4 節。
本輪唯一新增的實作指引是：完整來源 checkout 與 installed distribution 分開核對；
保留所有原 CLI，實跑 credential-free demo 的兩個 modes。
兩者的結果均不能提升成 subscription native 或 Promotion PASS。

## 執行路徑與可觀察邊界

requirements-harness2.txt 使用與 NeoWeaver #22 相同的完整 upstream commit。
獨立 harness2.yml 在標準 Ubuntu runner 讀取該 pin，保留完整 Google checkout，
以同一 pin 安裝 Python distribution。原 specification.yml 沒有改動。
Job 沒有 model login、subscription token、paid API key 或 dispatcher 操作。
只有 main 的正常 push 才會發布 harness2-experiment-v1。
內容只有 schema、固定的 neoweaver-validation-k1 experiment 和 upstream pin。
PR job 不發布 proposal；artifact 不能授權本機執行。

scripts/check_harness2.py 先核對 Git root、HEAD 和原 tree 的每個 tracked entry。
Git 計算實際 bytes 的 blob identity。缺檔、變更 bytes、symlink 替代、
executable mode 變更和額外非忽略檔案均拒絕。此控制也檢查 assume-unchanged 隱藏的 drift。
它是來源完整性控制，不是隔離、執行授權或對並行敵意寫入的保證。

來源通過後，checker 使用全新、與 upstream 分開的 output 執行原 demo。
它核對兩個 ledger tasks 在 parallel 和 sequential 的 literal 結果。
它再核對已安裝 distribution 的 VCS commit、完整 console entrypoint inventory，
逐一執行 7 個原 CLI 的 help，最後重讀 upstream bytes。
拒絕會返回非零值。既有 output 不覆寫，也不把舊 demo 當成新執行。

本機重跑需要 Python 3.12 或 3.13、Git、requirements-harness2.txt 的安裝，
完整 upstream checkout，以及尚未存在的獨立 output 路徑。
實際指令形狀如下，路徑由操作者選定；它不產生 Owner continuation。

```text
python scripts/check_harness2.py --source /absolute/upstream-checkout --output /absolute/new-demo-output
```

## 本機觀察與必要缺口

2026-10-22 本機 source check 核對 114 個 tracked files。
原 deterministic demo 完成 2 個 tasks、0 failures，兩 modes 的答案均相符。
7 個原 CLI 的 help 已執行。這不是官方 Benchmarks 或模型原生執行。
原 upstream 5 個 workflow controls 已通過，涵蓋拒絕、失敗 selection、
reflection/library 和 resume；它們採 scripted DemoProposer，不使用訂閱模型。
本次 6 個來源拒絕 controls 已通過。GitHub job 須另讀 matching-head Provider 結果。

目前 Codex 回報 ChatGPT login。這只證明本機登入。
Claude auth status 回報 loggedIn=false。Docker daemon 回報 Linux。
這些讀回不能證明 Linux runtime 有合法訂閱登入、四種 transport 已接通、
network egress policy 生效或 native isolation 通過。
沒有搬運任何登入資料，沒有使用付費 API fallback，也沒有啟動模型。

原 validation-candidate request 的 loop inspect 回報 refused。
其 control_root 已不存在；原 next 要求 supervisor 提供 execution_envelope。
已讀回原 admission 保存的 task-envelope.json，但沒有重建消失的 control worktree、
替換原 runtime 身分或重播歷史 worker。歷史 retain_baseline 決定仍保留。
這個缺口禁止將舊 Candidate 當成目前有效 Promotion 輸入，不阻止本次獨立 source 工作。

## Fresh source reconciliation

| Source | 本次讀回 |
| --- | --- |
| Google Harness² main | 1cfe254e8d25b15f37048c3730134686abe60335，與 Handoff 相同 |
| NeoWeaver main | c3084edfb31085737ed23031b2194de9df74d556，與 Handoff 相同 |
| Soodles main | 1f5bfbe19d553304ca2f60138fe2c22519d655dd，與 Handoff 相同 |
| NeoWeaver #22 | open，633486e296d60875722d2389ebe635c510bd8299；唯讀 Adapter 保持原證據上限 |
| NeoWeaver #21、#20、#18 | 仍 open；只讀相依介面，沒有合併或採用其 Candidate |
| Soodles #436 | open，b192f07f91d61259b6998d7396c52d4fbd0daa10；本次 Provider mergeable=false |
| Soodles #443、#444 | open；保留其 handoff／Test Manager／migrate-class 範圍，不併入本次變更 |

## 本輪 A01–A20 狀態增量

下方原始矩陣保留 Handoff 當時的綁定。此表只追加本輪結果，不改寫歷史。

| ID | 本輪狀態與證據上限 |
| --- | --- |
| A01 | 本機 VERIFIED：完整 pinned source bytes 與 installed CLI inventory；main 尚未整合 |
| A02 | NOT_RUN：8 個 surface 的訂閱 native mutation 未實測 |
| A03 | NOT_RUN：原 deterministic parallel demo 已觀察，不等於 native model recursion |
| A04 | NOT_RUN：原 deterministic sequential demo 已觀察，不等於 native model recursion |
| A05 | NOT_RUN：僅上游 scripted library/reflection controls 通過 |
| A06 | NOT_RUN：僅上游 scripted resume/drift controls 通過 |
| A07 | 本機 demo/preflight VERIFIED；public GitHub job 待本次 exact-head readback |
| A08 | Source Candidate 已有 data-only producer 與本機 dispatcher；live main-run／admission 未驗證 |
| A09 | BLOCKED：本機 ChatGPT login 已觀察；Linux 訂閱 transport、egress／isolation 未驗證 |
| A10 | BLOCKED：Claude 未登入，四種 transport 未驗證 |
| A11 | BLOCKED：原 LAB subscription-compatible Judge 未驗證 |
| A12 | BLOCKED：原 JobBench grader 的訂閱路徑未驗證 |
| A13 | BLOCKED：Docker 可用不證明 WorkBuddy solver／judge compatibility |
| A14 | NOT_RUN：新 integration 尚無 native H0/H1；歷史窄範圍 pair 不挪用 |
| A15 | NOT_RUN：新 integration 沒有開啟 validation 或 final held-out |
| A16 | NOT_RUN：尚無已實作 Promotion Owner 可供 model-to-code 同步驗證 |
| A17 | 部分觀察：本輪沒有模型登入資料／私有 trace 上傳；完整 integration 尚未驗證 |
| A18 | NOT_RUN：原歷史 request custody 讀回 refused；沒有 Promotion 效果 |
| A19 | NOT_RUN：沒有 Noodle production Stage 消費或 frozen Stage 改寫 |
| A20 | NOT_RUN：沒有 native 改善或 Cost per Verified Task 主張 |

## 保留的全部已確認決策

以下保留原 Handoff 的決策原文。HOF-02 與「handoff only now」
指 2026-10-21 文件交付回合；本輪實作授權另見開頭的使用者指示。
其餘決策不因本次 source implementation 放寬。

## 2. All confirmed decisions (never ask again without a new counterexample)

| Decision | Binding choice |
| --- | --- |
| INT-01R A | Harness² is a **complete Self-Optimization Engine**, not replacement for Noodle's Production Execution |
| INT-02R B | Harness² changes harness surfaces; product-code changes remain in original Soodles/Noodle authorized execution |
| INT-03R A | Native internal Harness² selection/reflection/library are retained but **isolated from Production Promotion**; only independently verified harnesses may be promoted |
| INT-04R A | **Full, pinned, unmodified Google upstream**, including original features/CLIs and Benchmark implementations; use minimum compatibility adapter outside upstream; no fork as default |
| INT-05R A | First formal target: **Optimization Promotion Safety**, with Model-to-Code synchronization |
| INT-06R (revised) | **NeoWeaver public free standard GitHub Actions**, not a dedicated standalone Linux VM as primary public CI |
| INT-07R B | Restrict experiment network egress; allow only required endpoints under explicit policy and block benchmark rubric leakage |
| INT-08R (superseded) | Historical US$100 API budget suggestion is **not** authorization. Later restriction: **no paid model API key**; manage subscription usage, wall-clock, run counts and genuine limits |
| INT-09R C | Adaptive evidence collection in Validation; **final held-out must remain untouched until candidate/protocol frozen**, otherwise retire contaminated partition |
| INT-10R C (constrained) | Preserve all original upstream model/provider configurations for completeness; support verified subscription CLI providers separately. **Do not use paid API/Vertex fallback** in the authorized integration |
| INT-11R A | Validated Promotion flows through original Soodles PR/Merge/Provider gates and affects **only new, not-yet-frozen stages** |
| INT-12R | Previous fee question superseded by INT-13R B plus no-paid-model-API requirement; no independent approved answer to reuse |
| INT-13R B | **No model subscription tokens in public GitHub Actions**. Local authenticated Codex/Claude; ChatGPT GitHub Connector is control/readback plane, not inference API |
| INT-14R B | Full upstream Benchmarks/CLIs retained, NeoWeaver Native Optimization E2E first; LAB, JobBench, WorkBuddy-Bench individually verified later, unavailable branches marked `BLOCKED` |
| INT-15R B | Public Actions emits an **untrusted bounded experiment proposal**; trusted local **pull-based** dispatcher executes only original-owner admitted requests after verifying source/allowlist, returns sanitized evidence |
| HOF-01 A | This **separate** `docs/handoffs/2026-10-21-harness2/handoff.md`; preserve other handoffs |
| HOF-02 A | Dedicated Soodles branch → commit → PR; **no merge, no Harness² feature implementation in the handoff turn** |

The full upstream includes all eight editable Harness components (system prompt, guardrails, memory, tool guidance, subagents, skills, scripts, plugins), Propose–Probe–Compose in parallel/sequential modes, Experience Library and reflection, native scheduling/selection/resume/ledger, both original OpenCode/Codex substrates, LAB/JobBench/WorkBuddy adapters, judge/report/CLI and their legal source notices. `Full upstream retained` does **not** mean `all model-backed capabilities already passed`.


## 保留的原 A01–A20 Acceptance Matrix

以下是原 Handoff 矩陣，Current bound 為當時的歷史讀回。

## 6. Acceptance Matrix: no false PASS

`NOT_RUN` = not exercised; `BLOCKED` = known unmet prerequisite; `INCONCLUSIVE` = insufficient/mismatched evidence; `VERIFIED` = observed for this exact subject/scope only; `PROMOTED` = fresh original Owner/Provider effects. Keep existing historical local evidence as historical, never inherit to a new head.

| ID | Requirement / differentiating positive and negative control | Current bound |
| --- | --- | --- |
| A01 | Complete Google upstream: pinned whole distribution, license, original modules and CLIs; reject omitted pieces | NeoWeaver `main` not integrated; #22 partial |
| A02 | Eight editable components, load/validate; refuse disallowed path and unsafe edits | NOT_RUN |
| A03 | Actual native parallel recursion, candidate rejection and result receipts | NOT_RUN |
| A04 | Actual native sequential recursion and carry-forward, bounded exit | NOT_RUN |
| A05 | Reflect and domain/mode/seed-isolated library; reject leakage and cross-mode state | NOT_RUN |
| A06 | Resume, identity/fingerprint check, duplicate and crash/unknown outcomes | NOT_RUN |
| A07 | Credential-free public Actions, complete native deterministic demo/preflight, original CLI controls | NOT_RUN |
| A08 | Forged public artifact/wrong actor/stale HEAD must not authorize dispatcher | NOT_RUN |
| A09 | Real Codex CLI subscription Proposer/Selector/Executor + trace; no API fallback | UNKNOWN / NOT_RUN |
| A10 | Real Claude Code subscription equivalent and independent receipts | UNKNOWN / NOT_RUN |
| A11 | LAB original rubric and native judge, matching baseline | BLOCKED: subscription-compatible Judge unverified |
| A12 | JobBench original weighted rubric and original grader; distinguish ungraded from pass | BLOCKED |
| A13 | WorkBuddy Docker/Harbor, native solver and judge/proxy on legal subscription path | BLOCKED |
| A14 | Matched H0/H1 native task, solver/seed/budget/Oracle; reject mismatched/unknown runner | #22/#436 historical narrow evidence only |
| A15 | Validation adaptive; final untouched held-out, complete denominator and no label leakage | Historical narrow pair; new integration NOT_RUN |
| A16 | Formal Promotion Safety, bounded checking, real-code mapping, breaking mutations and drift maintenance | NOT_RUN |
| A17 | No public token, private source/trace, secrets or nonpublic labels in logs/artifacts | NOT_RUN |
| A18 | Exact current source and authorized original Soodles Owner Promotion; refuse stale/no-authority | NOT_RUN for new integration |
| A19 | New only legal Noodle Stage consumes promoted harness; frozen Stage unchanged | NOT_RUN |
| A20 | Demonstrable lower Cost per Verified Task or verified better task outcome without regression; no invented missing cost | NOT_RUN |

**Gate separation:** upstream integrated ≠ subscription native verified ≠ official benchmark judged ≠ independent promotion verified ≠ production promoted ≠ optimization benefit. INT-14R B permits official Benchmarks' subscription-specific paths to remain `BLOCKED` while a narrow native NeoWeaver integration is honestly verified; never label all Benchmark compatibility as PASS. A20 is a measured claim, not a feature-release prerequisite if no improvement is demonstrated.


## 下一個最小單位

第 3 步仍需在原 Owner admission 上建立 bounded data-only proposal 與 pull dispatcher，
先以 forged、duplicate、stale、bad 和 unknown outcomes 辨別信任邊界。
public artifact 本身不能變成 argv 或本機執行權。
原 loop handoff 的 locally_integrated 前置條件保留，不將它當通用 trust adapter。
後續實作沿原 Owner 介面接通，不新增 scheduler、Test Manager 或 Promotion permission。

目前沒有新的合法 Promotion continuation。
模型執行須等相應 subscription transport 和隔離前提成立。
原 Handoff 的最小順序、停止條件與所有 deferred requirements 仍有效。
