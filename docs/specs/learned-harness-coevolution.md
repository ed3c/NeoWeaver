# NeoWeaver Learned Harness Co-evolution 完整規格

目前產品目標、完整 Harness² 接合、第一輪指令搜尋範圍及 Migration-RL 交互，見[目前產品工程規格](neoweaver-product-program.md)。
原十項 REQ 與本文件的訓練／transfer 義務保留；近期工程先完成固定權重的完整產品接合與獨立驗收，不以此宣稱權重訓練已完成。

本文件重新編譯原 PR #1 的十項 logical REQ。純 parser／refusal 已有第一個局部實作與正反控制，見 [parser contract](../parser-contract.md) 與 [本輪實測摘要](../parser-verification.json)。其餘產品、Trainer、native Frozen Codex transfer 仍為 PROPOSED，尚未實作或執行。FactoryWeaver CLI 的實際驗證只支持本文件的結構、引用與唯讀交接，不支持 RL 成效或 Agent compliance。來源版本、原需求別名與歷史驗證結果見 [編譯入口](../compiled/README.md)。

## 原始 Goal 與成功邊界

NeoWeaver 要訓練一個有界 Harness Patch Proposer，並在有合格資料時選擇性訓練 open-weight Solver。經獨立驗收的 Harness 改動可以轉移至實際支援的 frozen Codex Skill、MCP 或 plugin 介面。Frozen Codex 在此實驗中只接受 inference context／工具環境變更，不宣稱其模型權重已訓練。

Measurement 使用相同 task、environment、Solver、seed policy、資源預算與既有 acceptance 的 paired replay。先核對 hard gates，再比較完成結果、protected regressions、可觀察 decision count、token／tool／latency cost 與 held-out transfer。Whole Goal 的成功必須沒有 hard-gate violation，並有可重複的正向 paired effect。單次改善、可重放 fixture 或 writer 完成都不满足這個 gate。沒有資料時保留 UNKNOWN，不填入目標增益、成本下降或測得基線。

Persistence 保留原 Goal、十項 REQ、完整 source coverage、實驗假設、候選 patch、原始 capture 與原 Producer receipts。失敗修正不得換名重設預算、改 evaluator 或遺失未完成需求。單個 Issue Atom 完成只結束它的局部因果實驗。

Stop／Escalation 遵守原 scope 與授權 effort horizon。Unknown effect 先讀原 Owner 狀態；缺少 trainability／capability／rights 只停止依賴它的操作；regression 拒絕候選並由原 effect Owner rollback；沒有改善證據則 NOOP。沒有既有授權 heartbeat 時，不新增自動 Scheduler、Cron 或背景持續訓練。

## 十項原始需求及可觀察 acceptance

| 原 logical REQ | Actor 與結果 | Measurement／positive | Falsifier／negative／non-case | 責任來源 |
| --- | --- | --- | --- | --- |
| REQ-01 Source integrity | Session 保留原 Issue Goal、acceptance、Repo snapshot、訓練資料權利與全需求 inventory | 每個 decision-relevant source unit 對應原 REQ／Card 或具名 K；沒有被四卡顯示截斷的第五需求 | Summary 改了原 acceptance、漏掉 clause、以生成文件授予 merge，均拒絕；資料格式通過不等於語義完整 | 原 User／Source Reader／Issue Owner |
| REQ-02 Three planes | Learning 提案、Execution 隔離 replay、Verification 獨立裁決 | 被允許的候選只進入 disposable replay；驗收 oracle 由獨立來源固定 | Proposer 修改 reward oracle、sandbox 外 effect、自己提交 PASS 都不能取得 acceptance；不以新增 Owner 取代原 Owner | 原 execution 與 verification Owners |
| REQ-03 Trainability | Trainer 只處理有界 mutation surface、有 parser、可重現 task 與 replay 的候選 | 合法 patch 可 parse、通過靜態限制並在固定 snapshot 重放；重播資料由原 runner 提供 | 任意 source rewrite、未固定 environment 或不可回讀 action 不能進訓練；不把所有 repository edits 變成 action space | 原 Patch Validator／Snapshot Runner |
| REQ-04 Two policies | Proposer πθ 學 Harness；open Solver πφ 僅在有效自身 token lineage 下更新；Codex 保持 frozen | batch 的 actor、action、generation token provenance 與 reward 指向同一次原始 observation | 把 Codex transcript 算成 πθ 的 policy-gradient tokens、補造 logprob／tokens／weights 皆拒絕；缺 Solver provenance 不影響獨立 Proposer source preparation | 原 generation／Trainer Owners |
| REQ-05 Causal attribution | Evaluator 分開 Harness、Solver 與 interaction 的影響 | A=H0/φ0、B=H1/φ0、C=H0/φ1、D=H1/φ1 使用匹配條件；frozen Codex 另測 H0/H1；whole Goal需無hard-gate violation且有可重複正向paired effect | 只看 D 或單次改善便宣稱成功、或不匹配預算／task population，均 INCONCLUSIVE；不將 interaction 當單一政策效果 | 原 paired evaluator |
| REQ-06 Scoped patch | Proposer 針對一個被觀察失敗提出一個合法因果目標 | failure ref 指向原 trace；target 在 Owner allowlist 內；原 Goal 與 acceptance 不變 | 只有課程標題或泛稱品質不好、capability 未觀察、越出 path/effect scope，均 REFUSE／NOOP | 原 observation／admission／Patch Validator |
| REQ-07 Plugin transfer | Adapter 將已接受 artifact 映射至目標 Host 真正支援的介面 | probe 證明介面、bytes、load 與 fresh consumer consumption；保留安裝／執行／效果三種 readback | Plugin 被提及或 installer copied files 不證明 native consumption；缺 Hook event 或 trust 時不能宣稱 Hook 已執行；沒有能力不猜 API | 原 target Host／plugin／provider |
| REQ-08 Full lifecycle | Soodles Outer 準備原 Issue／admission；Noodle Poteto 實作 admitted delta；原 Managers／Provider 各自回讀 | actual Stage capture 顯示 consumed task／preselected playbook；必要 Test／Schema next 有真實 consumption；Provider 有 exact-head delivery | Writer Completed、reference CI、Reader next=null 不能閉合 parent Goal；不強迫所有 Managers 跑 | 原 Soodles／Noodle／Test／Schema／Provider |
| REQ-09 Learning dataset | Dataset Owner 固定 train／validation／held-out，保留來源、rights 與 rollout→action→reward 的真實關係 | train samples 有完整合法 lineage；validation 用於 acceptance；held-out 只做封存評估 | 猜 token、混 held-out training、使用權未確認、未裁決 reward 都排除更新；成本缺 capture 不是零 | 原 dataset／generation／verification Owners |
| REQ-10 Lesson lineage | Session 記錄被觀察的 first unsupported premise 與實際 rework DAG | LESSON 每個 Issue／Commit／PR edge 可讀回；正反控制能區分首個因果錯誤與後續症狀 | 補造 Issue ID、SHA、closure 或將歷史 NOT_RUN 改成 PASS，均拒絕；NeoWeaver 尚無 implementation Issue 不補一個 | 原 GitHub／capture／source Owners |

上述原 logical IDs 不改名。首次 v1 materialization 由 Host 產生合法 registry identities，別名映射保存在 compilation sidecar。它不是既有 native Registry 身分、authorization 或 Stage metadata。

## Roadmap-assisted Session One-Shot Prompt — proposed consumer contract

編譯期 Session 從真實 Source/Owner 觀察提出可反駁的 Card-generation feedback，
先修正第一個錯誤的 REQ／SPEC／V 因果前提。它不是下游 Stage `PromptDelta`。
原 44 張 Cards 作為 Knowledge IR 與 source/acceptance ledger 保留。

R Card 僅索引多個候選 Behavior Scope 的 prerequisite、existing Card references
與各自局部 Exit。Session 依原 Goal、最新 Failure、合法 Owner Next 和當前
Consumer 決定最小充分 Scope，將 Card 語意轉換成 One-Shot Prompt；
不可直接串接所有 Card payload、提升 context-only/deferred 接受條款，
也不得把 Roadmap 順序當成實際 issue admission。

Current Parser Scope 的 semantic projection 由 SPEC08/V09/C31/G33/G34/S38
組成：只在固定 `raw bytes + fixed_inputs` 上 parse/refuse；驗收來自原
Parser controls，後續 replay/train/transfer/effects 都在 parent scope。
完整逐卡審查及可直接用於 independent Source Review 的負例見
[44-Card One-Shot Review](../reviews/one-shot-card-scope-review.md)。
這是需求/語意契約，不宣稱 native Stage 已讀取或已有 Agent 行為提升。

## 三個平面與資料契約

Learning plane 讀取合格 observations，產生 scoped PatchProposal 或可回滾的模型 update proposal。Execution plane 只在既有允許環境進行 snapshot／replay。Verification plane 使用 writer 不能修改的 acceptance、protected regressions 與 effect readback。這是職責分離，不建立第二個 Soodles lifecycle state machine。

以下型別是 proposed NeoWeaver domain contract。`owner_ref` 是原 Producer 已簽發的 opaque reference。Consumer 不拆出或重建 runtime IDs、SHA、argv、timestamps。完整 provenance 不得靠自由文字補足。

| Proposed record | 必要內容 | Producer → Consumer | 缺口／拒絕 |
| --- | --- | --- | --- |
| TaskSnapshot | original_goal、accepted_requirements、acceptance、source/environment/budget/rights refs、dataset split、protected_oracles ref | Source／Environment Owner → replay runner／Solver | 缺任何必要固定輸入只阻擋 replay；source quote 不能替代 environment receipt |
| RolloutObservation | snapshot ref、actor、policy ref、ordered raw capture ref、observed result、token provenance ref 或明示 UNKNOWN | 實際 generation／runner → Observer／eligibility checker | 無 terminal 或 capture prefix 不完整保留 partial；看過 transcript 不代表完整 action lineage |
| FailureScope | 原 failure evidence、causal hypothesis、one allowed target、parent acceptance、non-cases、stop rule | Observer／Session → Proposer | 無失敗或已有合法 unchanged next 則 NOOP；未觀察 target 成為 K |
| PatchProposal | failure/snapshot/allowlist refs、single mutation surface、bounded operations、expected old source ref、proposed replacement、original acceptance ref | πθ → parser／Patch Validator | duplicate keys、不在固定 allowlist 的 target、原 Owner 固定的 protected target、unsupported surface、額外 effect 都 REFUSE。Refs 是 opaque data；若後續 Runner 將 reference 解碼為 path，原 Runner／Owner 另驗實際來源與 path escape；proposal 無 effect authority |
| PairedReplay | baseline/candidate observations、matched conditions refs、population/exclusions、completion validity、missing observations | 原 Snapshot Runner → independent Verifier | stale baseline、不同預算、漏 negative controls、unknown provider effects 都 INCONCLUSIVE |
| VerificationResult | original oracle ref、hard gates、protected regressions、PASS／FAIL／INCONCLUSIVE、evidence refs、covered scope | 原 Verifier → reward／original Owner | PASS 只覆蓋其 scope；沒有 native effect receipt 不填 goal_closed |
| RewardObservation | actor/action/replay/verifier refs、known／unknown disposition、observed outcome/cost components、eligibility | 原 reward／verification Producer → Trainer | 權限 gate 或資料不足不能以 scalar 權重抵銷；UNKNOWN 不當成零、failure 或正 reward |
| TrainingBatch | 訓練 policy、train partition、eligible samples、原 update method/config refs、rollback checkpoint ref | Dataset／Trainer Owner → update runner | validation／held-out／foreign tokens 不進 gradient；method 選擇不替代 trainability |
| TransferArtifact | accepted patch/ref、target capability evidence、distribution policy、original consumer／effect Owner、rollback ref | accepted artifact Owner → Codex capability adapter | source acceptance 不證明 installer／load／consume／effect；任一步未觀察則該步 NOT_RUN |

[PatchProposal schema](../../contracts/proposals/patch-proposal.schema.json)只驗證 declared shape。它不證明 referenced artifact 真實、path 受允許、模型 token 合法或任何 Owner admission。

## 可變 surface 與不可變邊界

第一版 action space 只容許 Owner 明確選定的 Skill instruction、context selection policy 或 MCP／tool interface wrapper。這些 surface 是 proposed options，不是已安裝能力。每個候選只能改一個因果邊界。Validator 保留原 Goal、acceptance、protected oracles、dataset partitions、authorization、provider effect guards 與 secret handling。

Native lifecycle Hook 只有在 target Host 已支援、使用者已 review/trust 目前 definition、實際 event 與 scope 都符合時才可選。不得因卡片提到 Hook 自動建立它。Cron 只沿既有授權 heartbeat。Patch proposal 不攜帶執行 argv 或 credential，也不能把 validator、held-out oracle、admission 或 landing owner 放進 mutation allowlist。

Expected old source 不符代表 stale proposal。原 Producer 取得 fresh readback；Consumer 不猜新 head 或自動 rebase semantics。已提交但 effect outcome 不明先讀回同一 Owner，不以相同 patch 重播寫入。

## Trainability、credit assignment 與更新方法

πθ 的 action 是本次 bounded Harness proposal，不是下游 Solver 的全部 transcript。只在原 generation、action、paired replay 與 independently verified reward 可一致連結時才形成 eligible sample。Open Solver 更新還需其自己的有效 generation tokens／policy provenance。Frozen Codex trace 可供 failure analysis 或 inference replay；它不構成對 Codex 權重做 gradient update 的證據。

SFT warm start、policy-gradient／group-relative 更新都只是可選設計。首次 runnable slice 不要求同時訓練兩個政策，也不預選 framework、模型、learning rate、reward weights 或樣本數。原 Trainer／Dataset Owner 依有權且可重放的資料固定方法、budget 與 checkpoint。沒有 on-policy token／action provenance 時停用依賴它的 gradient 路徑，而不是重建 logprob。

Hard gates 先於 soft outcome/cost。任何 acceptance、權限、privacy、protected regression 或資料 split gate 不成立，候選不可被接受。沒有 gate observation 時使用 INCONCLUSIVE，不能用低成本 bonus 抵銷。通過 hard gates 之後，原 measurement producer 才可提供同 population 下的 outcome/cost components；Session 不能自己補 scalar reward 或成功比例。

## A6 實作精簡：不建立 Provider Authenticity／FileRef 管線

A6.0 的唯一現行 Source API 是 `inspect_training_candidate(TrainingCandidate)`，
直接使用 Session／原 Runtime 已知的 task/evaluation facts（actor、method、
partition、rights、acceptance、protected regressions、effect status、
lineage、token provenance、replay、verifier、reward）。
此前 A6.1–A6.3 額外製造的 FileRef、OwnerRef、SHA-256 與目錄型 Evidence Readback
既沒有原生 Producer 的可信真相，也沒有 Trainer Consumer，已刪除。
不可為了讓機械檢查 PASS 再要求 Agent 猜出或輸入這些資料。

這是 **實作資料流精簡**，不是放棄原十項父需求或授予新的訓練權限。
原完整規格中 TaskSnapshot／Rollout／TrainingBatch 的來源與證據敘述
仍是未來真正執行時的正確性責任，不應誤作現行 A6 CLI 的先備驗收。
Hard Gates 優先：Rights Denied、held-out／validation、acceptance／
protected regression FAIL、wrong lineage、自簽 Verifier 與 frozen Codex
均拒絕；未知保留 INCONCLUSIVE。所有結構篩選輸出仍
`eligible_for_training=false`，真正的 source observations、train/checkpoint
與 paired effect 必須等 Runtime 實際存在才能驗收。

## 因果實驗與 held-out transfer

| Arm | Harness | Open Solver | 可回答的問題 |
| --- | --- | --- | --- |
| A | H0 | φ0 | 匹配條件下的 baseline |
| B | H1 | φ0 | 固定 Solver 時 Harness 改動的 scoped difference |
| C | H0 | φ1 | 固定 Harness 時 Solver 改動的 scoped difference |
| D | H1 | φ1 | 聯合結果與 interaction；不能只憑 D 辨識原因 |

有可比較 measurement 時，Harness difference 是 B−A，Solver difference 是 C−A，interaction 是 D−B−C+A。這是對四組 matched measurements 的定義，不是宣稱已取得四組資料。只有 frozen Solver 可用時，B/A 仍可測 Harness；C/D 保留 NOT_RUN，不能生成替代值。

Frozen Codex transfer 使用相同 task、允許工具、source、environment 與 resource policy 的 H0/H1 paired inference。Train、validation、held-out 各自保留 inventory；相同 repository、patch family 或近重複 task 的 leakage 由 Dataset Owner 審查。只對預先固定的 held-out population 報告結果、排除理由與 uncertainty。看過 held-out outcome 後再用它選 patch 屬污染，不能當外推成功。

原 paired evaluator 還須依已接受的 measurement rule 核對效果可重複，而非只核對資料可重放。重複方法、population 與budget從原Owner取得；缺少這些輸入或只有一次結果時whole Goal仍開放。不得補造replicate數量、significance threshold或正向結果。

## Frozen Codex adapter 能力邊界

官方文件說明 plugin 可帶 Skills／MCP，manual desktop plugins 可支援 lifecycle hooks；有 hooks 的 plugin 不進 public directory，安裝也不自動 trust hook definition。這些是文件層能力，不是本次 target Host 已啟用或消費的證據。[OpenAI plugin 文件](https://developers.openai.com/plugins/build/plugins#bundled-mcp-servers-and-lifecycle-hooks)

Adapter 先讀真實 Host capability 和原 authorization，再選最小合法 mapping。Skill text 可表達條件式 instructions；MCP wrapper 可提供明確 typed tool boundary；Hook 只用已支援且已 trusted 的 event。不能宣稱任意 pre-action interception、model weights access 或 remote script deployment。Probe 缺失時保留 K，繼續不依賴 native transfer 的 parser／fixture 工作。

App Server 的 migration detection/import 是可讀回的外部 config 路徑；它不等於某個 learned patch 被 fresh Agent 讀取或符合 acceptance。[官方 import 契約](https://learn.chatgpt.com/docs/app-server#detect-and-import-external-agent-config)

## Soodles Outer Loop 與 Noodle Poteto Inner Loop

Session 從原 REQ、真正 failure 與 Owner readback 選一個 causal Scope。已有合法 unchanged continuation 時原樣消費，不重選 Thinking Method 或 Poteto playbook。真實 unresolved architecture／Goal／evaluator 問題才走原 Thinking Router；已觀察 CLI bug 直接交原 code owner。卡型沒有觸發權限。

啟動 native Stage 時，Outer Loop 透過既有 Issue Contract／admission 固定 write/effect boundary、required inputs、independent oracles 與後续交付責任。Native Inner worker 在原 admitted `execute` stage 消費 semantic bullet Prompt Delta 和已選 playbook，可自由選 implementation details。它不改 acceptance、重新選 judge、重設 effort horizon 或自簽 parent Goal closure。已授權的 local parser 工作使用原 user/task 授權與必要固定輸入，不依賴尚未啟動的 native Stage。

Test Manager 一次選最小 discriminating controls；Schema Manager 消費真實 feedback，回傳 next 且需觀察它被消費。Hook 只用 actual native event；Cron 只用既有 authorized heartbeat；Provider 獨立裁決 publication／landing。這次 FactoryWeaver 工程以 source update、真實 CLI、independent reviews 與 GitHub receipts 完成；它不是 native Noodle Stage／Manager invocation receipt。

## 第一個 implementation Scope：純 parser／refusal

第一個 proposed atom 僅修 raw PatchProposal parser 與固定 mutation／acceptance boundary。原 Owner 提供 TaskSnapshot、FailureScope、allowlist、expected-source 和 immutable acceptance references；parser 不替它們判定來源真相、授權或因果效益。

局部 Goal 是合法、current、single-surface candidate 只得到 `ParsedProposal`；duplicate keys、stale expected source、越界／protected target、missing fixed input、extra credential/effect fields 得到具名 `DiagnosticRefusal`。兩種輸出都不啟動 replay、training、native transfer 或 provider write。相同 raw input 與 fixed boundary 重讀的 determinism，不等於 TaskSnapshot replay。

Measurement 使用原 fixed input/result parser controls。本輪 public API controls 已執行；編譯時保存的 proposed controls 與 NOT_RUN 保留在原 artifact，specification consistency check 不升級它。新的實作證據分開記錄於 parser verification，不把局部 parse acceptance 改稱完整 Trainability 或 replay PASS。Persistence 保留原十項需求、未覆蓋 clauses 與 whole Goal。Stop 是需要的原資料缺失或 scope 不符；未知先前 write outcome 回原 Owner，不能重送。

Scope 只選 SPEC-trainability 的 parser contract、對應 V control、三張必要 C/G 約束與 S38 proposed strategy。全 44 卡在 semantic-sidecars 中逐張標 local exit/control、constraint、strategy、context-only 或 deferred。Source integrity、Three planes、Trainability 與 Scoped patch 只覆蓋明列的局部 clauses；其完整 source review、Execution／Verification、replay 與 causal benefit 仍保留。Full lifecycle 的 native Stage／Provider acceptance 是父層後續義務，不能加入 parser exit。

Prompt Delta 是 proposed requirements，不能授予 native 權限或生成 executable next。原 admission／runtime playbook 尚未觀察，只限制依賴它們的 native Stage；原 user/task 已授權且必要 fixed inputs 可用的 local parser 工作可繼續。

- Parse raw single-surface proposal against original fixed inputs，回 `ParsedProposal` 或具名 `DiagnosticRefusal`。
- 拒絕 duplicate keys、stale expected source、越界或 protected target、missing fixed inputs、extra credentials/effects；保存 immutable references。
- 不執行 replay、training、native transfer 或 provider effects；保留全十项需求與後續驗收。
- 在實際授權 scope 與已選 playbook 內自主選 implementation；不重建原 next，不 retry unknown write。

Parser callers 是提供 raw data 的 Proposer；下一個 Consumer 是另行授權的原 Runner。Parser 不接受 self-signed VerifierResult。Implementation rollback 由原 source owner 回復 parser change；沒有本 atom 產生的 provider/replay state。Landing 仍由原 repository/provider owner處理，parser PASS 不等於交付或 whole Goal closure。

可持有的 module boundary 是 `domain`（資料與純函式）、`patches`（boundary parser/validator）、`replay`（原 runner adapter）、`verification`（原 oracle reader）、`learning`（eligibility/batch/update adapter）、`transfer`（capability-bound mapping）、`evidence`（原 references reader）。只有 patches/domain 的純 parser slice 屬首 atom；其餘為後續責任草圖，不宣稱已存在。

## 逐步交付與驗證矩陣

| Unit | 可驗收 exit | Positive／negative／unknown／replay | 後續仍開放 |
| --- | --- | --- | --- |
| Parser／immutable acceptance | 合法 proposal 解析；非法 input diagnostic refusal 且無 effects | single allowed edit／duplicate key 或 oracle edit／missing owner input／同 bytes 同判斷 | replay、training、transfer |
| Frozen task replay | 兩個 isolated copies 的 matched observations 可讀回 | 同 task/budget／changed baseline 或 scope escape／unknown external effect／固定fixture穩定 | native provider與cost claims |
| Independent gates／reward eligibility | 原 verifier result 與 actor/action lineage 匹配 | 原 oracle PASS且negative有效／self PASS或reward swap／INCONCLUSIVE／原 next reuse | policy update |
| Proposer update | eligible train-only samples 進固定方法；checkpoint 可 rollback | 自身 tokens／Codex transcript或held-out／missing provenance／固定batch可重放 | held-out effect、Solver update |
| Optional Solver update | 自身 policy provenance與 counterpart固定 | C/A／D-only推因果／缺模型權利／原checkpoint重放 | 完整factorial |
| Codex transfer | capability、install、load、consume、effect 分別有原 readback | 受支持 Skill/MCP／untrusted hook或猜API／缺 native trace／原owner讀回後才可重試 | whole Goal closure |
| Delivery／LESSON | Provider exact-head與parent acceptance讀回；DAG每edge可追溯 | 真實merge receipt／CI等於Goal／unknown effects／相同next NOOP | 無原closure不得closed |

## Completion Contract

歷史 knowledge compilation 的 DONE 僅表示已讀來源的 inventory、REQ mapping、source-justified Cards、typed links、Scope proposal與已執行 CLI驗證交付完成。NeoWeaver產品 implementation、RL experiments、fresh P-class consumer、admitted Outer/Inner Stage、必要 Managers、native Codex transfer與whole Goal仍需各自原 receipts。它們沒有執行時一律 NOT_RUN／UNKNOWN。

Whole Goal closure還須原Owner證明無hard-gate violation與可重複正向paired effect；局部parser驗收或可重放fixture不能替代它。

該編譯驗證的FactoryWeaver doctor與local maintain已在真實checkout執行。其完整maintain可讀到Soodles Reader transport，仍因native source/Agent/Issue/Manager/Provider證據缺口而blocked。不要用local clean改寫該結果，也不要為填滿卡型或四個visual slots制造內容。
