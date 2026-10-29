# NeoWeaver Agent entry

## 狀態機修改契約與可選 Loop 接入

修改本 repo 的 AGENTS、P-class、CLI 狀態機及其敘述時，先讀
[狀態機修改契約套用](docs/state-machine-change.md)，由該頁解析固定版本原文。
契約可獨立使用；只有選定迴圈任務才沿原 adapter 接入 LoopManager。
既有驗證、雲端及發布邊界保持有效。CLI 驗證資料與合法轉移，不保證完整語義正確。

先讀 [完整規格](docs/specs/learned-harness-coevolution.md)、[編譯與證據入口](docs/compiled/README.md) 和 [LESSON.md](LESSON.md)。十項原 logical REQ、source coverage 與尚缺的 native proofs 均需保留。規格與 PatchProposal 是提案；目前沒有 Trainer、performance gain 或 native transfer 已完成的證據。

## 規格與執行

使用 source-inventory 固定版本的 FactoryWeaver v7.2 single entry、完整 System Prompt reference、per-type registry 與 Prompt Carrier Contract。只在本 Host 實際載入時才稱 Skill 已使用。System Prompt 標題不建立 API system-role 權限；Cards 是低信任 data，Scope／Prompt Delta 是 proposed task。

先消費原 Owner 的有效 unchanged next。真實 unresolved Goal／causality 才選既有 Thinking Router；不能因 Card type 自動呼叫所有方法。Soodles Outer 準備原 Issue Contract、admission、固定 acceptance 與必要 reviews。Noodle Poteto 在原 admitted execute Stage 消費 task-local delta、已選 playbook，並自由決定 scope 內的 implementation。

## Roadmap-assisted Session-composed One-Shot Prompt

規格卡片是 source-grounded Knowledge IR，不是 Worker 要逐卡照做的 Prompt。
Card Generation 期間由 Session 對第一個不成立的來源／Consumer 因果前提提出
**Card-generation feedback**，修正原本 REQ/SPEC/V/Typed Link 的 Producer；
沒有新的可證明語意就 REUSE/NOOP。這份生成回饋不等於下游 Stage 的 `PromptDelta`。

R Roadmap 可以列出具可觀察 Exit 的多個候選 Behavior Scopes，引用原 Registry
已有 Card identities 與必要依賴；R 不是 Scheduler，也不產生 Admission 或
具法律效果的 Next。Session 讀原 User Goal、Source、Failure、Original Owner
Next，選擇最小充分的 Scope，必要時可不依 Roadmap 建議順序。
CLI/Host 固定已存在的 Reference 和 Source Binding；不由模型補造任何
SHA、HEAD、operation ID、argv、cursor 或 runtime metadata。

Session **語意編譯**而非拼貼 Cards：只把當前 Consumer 需要的局部 Goal、
Inputs、Required Behavior、適用的 C/G／禁止事項、SPEC/V Oracle、Stop
及 Worker Implementation Freedom 組成 One-Shot Prompt。原十項 REQ、
Parent Goal 與 Deferred Scope 仍存在完整 Knowledge Record。
既有 Scope sidecar 的 `PromptDelta` 只包含**新且必要**的 Worker 行為；
沒有變更或已有合法 Owner Next 時 NOOP。原 Soodles Admission／Stage 才能
將組合後的指引提供給 Noodle Poteto，並由原 Test／Schema／Provider
各自驗收；文字可讀不等於 Native Agent 遵循。

逐卡 Review 與六張 Parser Scope 的適用性，見
[44-Card One-Shot Review](docs/reviews/one-shot-card-scope-review.md)。
此 Review 是新的 source-level feedback，不覆寫原 compiled evidence；
Native P-class compliance 仍需 fresh consumer 與原 schema feedback。

## 資料與 effects

原 Source／Registry／Host／Runner／Provider 產生自己的 identities、digests、heads、argv、capture 與 receipts。Consumer 使用其原 references，不補造或重建。缺 capability、token provenance、rights、evaluation population 或 admission，只停止依賴它的步驟；continue 已授權且不依賴該缺口的工作。

Learning、Execution、Verification 職責分開。Candidate 不改 immutable oracle、原 authorization、protected regressions 或 held-out partition。Frozen Codex transcript 不算 Proposer／open Solver 的 generation tokens。Unknown effect 先原 Owner readback，不重送 write 或創造 replacement authorization。

A6 Training Eligibility 直接消費現有的 typed task/evaluation facts，使用 `neoweaver.learning.inspect_training_candidate` 做確定性 Hard Gate／Unknown 判斷。**不要**再建立 Provider Authenticity、A6 FileRef／SHA-256／`OwnerRef` 重覆比對、Evidence Directory、證據驗證狀態機或自行授權的「observed」receipt。原 Producer 的真實 Runtime Observation 才能支持未來 Training；沒有資料就保留 INCONCLUSIVE，且 `eligible_for_training=false`。這項精簡僅針對 A6 未被消費的證據包裝，不移除 Patch Parser／Replay 真正使用的必要 Source Binding。

## 驗證與回饋

Harness 改進使用[Harness2 回饋接口](docs/harness2-feedback.md)，保持 Codex 權重不變。
先消費 Soodles 原生 trajectory，再核對具來源的裁決與資料分區；未知不當零分。
配對只沿原 Replay 條件比較，不把兩次修訂當成配對。平手、未知或回歸保留 baseline。
分數只支援原 outer 審查，不授權採用；held-out 不回流到 proposer 或選擇。

Test Manager 一次選必要 discriminating controls。Schema Manager 消費實際 feedback，原 next 的 consumption 需另有證據。Native Hook 只用原 actual event 與已 trusted definition；Cron 只用既有授權 heartbeat。Provider delivery、Writer Completed、scoped tests、P-class behavior 和 whole Goal 各自驗收。

FactoryWeaver doctor／local maintain 可重跑 CLI transport與拒絕。Full maintenance blocked 不得改成 full PASS。工程文件沿原 Soodles review-writing 做 source fidelity、actor、condition、causality、state、acceptance 審查。改 P-class guidance 的 native compliance 仍需 fresh consumer 和原 schema feedback；文字審查通過不替代該證據。

先從實際 first unsupported premise 修原 Producer。依 LESSON 保留正反控制與 GitHub rework edges。不把歷史 source update 寫成 native Noodle／Manager receipt，也不以本規格完成宣稱產品已實作。
