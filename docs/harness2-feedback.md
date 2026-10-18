# Harness2 原生軌跡與獎勵接口

本接口套用[狀態機修改契約](state-machine-change.md)。模型權重保持不變。
上游為 [Google Research Harness2](https://github.com/google-research/harness2)，
固定版本 `1cfe254e8d25b15f37048c3730134686abe60335`。
Python 3.12 環境用 `requirements-harness2.txt` 安裝可選依賴。
一般 NeoWeaver 模組不載入此依賴；整合控制需要它，不以跳過測試掩蓋缺件。

## 責任與限制

Soodles `loop_behavior_prepare` 從原 LoopManager 投影取得不可變 trajectory FileRef。
`ReviewEvidenceAdapter` 讀取該快照與原來源。Harness2 `context.build` 可使用原 task、
trace 與 deliverable。context 不附加裁決標籤；原 trace 仍可能含過去回饋。
歷史 trace 不因此成為 held-out 資料。

`python -m neoweaver.behavior_tools` 從 stdin 接收 JSON，輸出 JSON。
必填 `snapshot` 是上述原 FileRef；可選 `review` 是裁決檔案的 FileRef。
裁決內容為 `schema: 1`、相同 `snapshot`、具名 `reviewer` 及 `cases`。
每個 case 使用 `BehaviorLabel` 欄位：`case_id`、`partition`、`outcome`、
`criteria_supported`、`independent_review`、`native_observed`、`hard_gates`。
partition 為 train、validation 或 held_out；outcome 為 pass、fail 或 unknown。
Session／原裁決者對語義與獨立性聲明負責。CLI 核對格式與來源，不認證聲明為真。
FileRef 應由原 producer 返回，不要求 Session 手算摘要。

預設核對目前來源。JSON 可明確提供 `historical: true`，讀取新 Soodles snapshot
當時保存且摘要相符的來源 bytes。結果標示 `retained_historical_bytes`。
歷史讀回不證明目前來源、目前指引的行為或 next 仍有效；舊快照缺保存 bytes 時拒絕。

沒有裁決時，原 Harness2 judge 返回未計分，fraction 保持 null。
條件、獨立性與原生觀察的聲明齊備時，案例可列為 `golden_eligible`。
這只表示提供的裁決事實滿足條件，不是認證黃金集完成。
通過且 hard gates 成立為 1，已裁決的失敗為 0，缺件為 null。
負例保留；不以 RSS、耗時或工具成功補成行為通過。
來源漂移拒絕或未計分；相同讀回不產生新效果。

`paired_feedback` 消費原 `inspect_pair` 結果與兩臂標籤。
人口／分區不符、未知或不具可比性時保留 baseline。
held-out 不能驅動選擇。任一受保護案例退步或 hard gate 失敗時拒絕候選。
平手是 NOOP。單對改善只要求 outer 審查，不能宣稱重複實驗或跨任務轉移收益。
原 pair reader 的證據上限仍為 `DECLARED_RUNNER_READBACKS_ONLY`。

## 尚未接通的執行能力

此 adapter 接通上游 context 與事後 judge，並非完整 BenchmarkAdapter runner。
`execute` 明確拒絕。上游 Propose–Probe–Compose 遞迴與 selector 尚未接到 Noodle Host。
不使用上游預設排除 baseline 的選擇池；原 Soodles 審查保留拒絕與 NOOP。
原 Noodle Host 管理 admission、worker、worktree、租約與 Swap；原 outer 管理審查續行。
本接口不啟動模型、不修改模型權重、不建立 scheduler、不授權 landing。
真實 Harness 改進仍需固定條件的原生配對、獨立 Oracle 與必要未見任務驗證。
