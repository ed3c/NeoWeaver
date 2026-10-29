# NeoWeaver 產品目標與目前工程規格

本頁整理目前已接受的產品工作與實作順序。它補充原十項 logical REQ，不取代原規格、卡片身分或歷史證據。
需求已接受、規格已保存、程式已實作、Native 已驗收、Provider 已發布與 Promotion 是不同結果。

## 目標與優先順序

主線是依完整原規格交付 NeoWeaver 的軟體架構與功能。
在實際產品里程碑間，以完整、固定版本的 Google Harness² 優化 Codex 驅動的 Soodles Outer 與 Noodle Poteto Inner。
受測流程從原始需求開始，包含必要澄清、工程判斷、派工、實作、候選審查與最後驗收。
兩道訓練題或局部 solver 不能代替完整產品交付。

第一輪候選只改指令、skills 與流程設定。模型、CLI、資源政策、隔離與獨立驗收先固定。
必要的基礎程式修正由工程流程完成，成為兩臂共用起點，不算成指令候選的收益。
完整上游的其他可編輯能力仍保留；保留能力不表示本輪有權改憑證、Oracle 或 effect policy。

首要成果是完整任務成功率與減少人工救援。必要產品澄清另計。
重複提問、把可查事實交回人類及人工修復流程，不能藏入必要澄清。
相同固定起點下，候選需滿足原需求與獨立檢查，原成功配對不退步，且至少有未見案例提高自主完成程度或減少額外救援。
只變快、少用工具或少問問題不能抵銷品質下降。小樣本只支持實際觀察案例。

## 原來源與三套獨立記錄

| 來源 | 本產品消費的要求 | 保留邊界 |
| --- | --- | --- |
| [原 NeoWeaver 規格](learned-harness-coevolution.md)與[編譯入口](../compiled/README.md) | 原 10 REQ／44 Cards、三平面、兩政策、paired attribution、dataset 與 transfer | 不把固定權重推論當成訓練；原身分及歷史不重建 |
| [完整 Harness² handoff](https://github.com/ed3c/soodles/blob/092dfa94aae6c9888d055102e35479a18f64214d/docs/handoffs/2026-10-21-harness2/handoff.md) | INT-01R～15R、適用 HOF、A01～A20 | 後續已接受的訂閱與費用條件優先；舊 handoff 回合的 docs-only 不限制目前實作授權 |
| [FactoryWeaver 閉環與 MGP handoff](https://github.com/ed3c/soodles/blob/80c75bb65aeada9e9269f3c7e42f6a00ba8eca75/docs/handoffs/2026-10-23-factoryweaver-mgp/handoff.md) | FCL-01～03、MGP-01～03；原閉環 30 REQ／68 Cards | Source→REQ→SPEC/Card→Scope→Consumer 分層驗收；全原始聊天的完整性未證明 |
| [Migration-RL handoff](https://github.com/ed3c/soodles/blob/3d82f0a09f7dbafbdddac2214ac89f9abb89fc8a/docs/handoffs/migration-rl/handoff.md) | MRL-01～10、MRA-01～18、FWC／FWP；原 22 REQ／74 Cards | FactoryWeaver 保有原 Registry；首個 AIFS／SeeCode 寫入目標仍是 medium-compiler #72 |

目前監督 Session 的交接還固定了第一輪較小的候選範圍、成功率優先及減少救援的採用條件。
三套知識記錄不合併身分，也不因文件存在就提供 Admission。
本文沒有重新列舉所有 Card payload；完整要求沿表內原記錄保留。

## 完整上游與外部接合

固定完整 `google-research/harness2` commit `1cfe254e8d25b15f37048c3730134686abe60335`。
保留原 LICENSE、core、substrate、八類 surface、CLI、官方 benchmark、Judge、report、ledger、selection、reflection、Experience Library 與 resume。
八類 surface 是 system prompt、guardrails、memory、tool guidance、subagents、skills、scripts、plugins。
Parallel 與 sequential 都需實際驗證，不能固定成 k=1 或關掉 library 後稱為完整整合。

NeoWeaver 的新 adapter 置於上游之外，呼叫原 core API。
唯讀 ReviewEvidenceAdapter 與可執行 BenchmarkAdapter 保持不同責任。
前者拒絕 execute 的邊界不能被改名成原生執行成功。
原 CLI 只註冊既有 benchmarks；外部 adapter 不會自動加入它的選單。

本機訂閱 Proposer、Selector、Executor、Judge 需分別提供真實 launch、輸入、完成與觀察證據。
Codex 已登入不證明其餘角色可用。保留 Claude 的後續驗證義務。
本輪不使用付費 API 或 Vertex fallback。包含歷史支出的 US$5 上限保留；訂閱美元未知保持 null。
無成功時 Cost per Verified Task／Migration 未定義，不能填零。

## Producer、Consumer 與執行路徑

| 邊界 | Actor、輸入與作用 | 拒絕或未知條件 |
| --- | --- | --- |
| 公開 Actions | 執行 credential-free source／demo controls；必要時輸出有界 data-only proposal | 不帶訂閱憑證、私有任務、原始私有 trace 或 hidden labels；proposal 不能變成 shell 或授權 |
| 本機 pull dispatcher | 讀原 Provider run／commit／artifact，核對原 Admission、來源、allowlist 與固定操作，再交原 owner | 錯 actor、stale source、未知效果或未准入資料不能派工；不另造 scheduler |
| Harness² core | 消費合法 benchmark／substrate／proposer／selector，執行原兩模式、selection、reflection、library 與 resume | domain、mode、substrate、seed、split 不混用；timeout／未知效果先原讀回 |
| 獨立驗證 | 使用固定 baseline、匹配任務／模型／預算、原 Oracle、protected regressions、validation 與 held-out | 候選不能改答案或偷看 final held-out；不匹配或缺證據保持 INCONCLUSIVE |
| 原 Soodles／Noodle | 原 Session 判斷語義；原 Admission 固定 scope；原 Stage 消費 Delta／playbook；原 Test／Schema 分別回饋 | Card、Reader、內部 selection、Writer Completed 均不能自授 Promotion；frozen Stage 不修改 |
| Provider／Promotion | 原 owner 核對 current source、獨立驗收、授權及效果讀回；只讓新的合法未凍結 Stage 消費 | 本次任務未授權自動 merge、部署或正式 Promotion；NO_PROMOTION 是合法結果 |

## Promotion Safety 與官方 benchmark

第一個形式化目標是 Optimization Promotion Safety。
模型須對應真實 Promotion 程式與 owner，涵蓋並行、timeout、stale source、unknown effect 及 frozen Stage。
保留故意破壞的反例與 code/model drift 控制。只有模型、沒有程式對照時屬設計驗證。

先驗證 NeoWeaver native E2E，再分別處理 LAB、JobBench、WorkBuddy 的原生 rubric、grader 與必要 runtime。
未支援的訂閱 Judge、Docker／Harbor 或其他能力保持 BLOCKED，不用替代假 grader。
Harness² 內部 chosen final 不證明優於 baseline；k=1 的 trivial selection 也不證明收益。

## Migration-RL 與卡片回饋

先交付真正可重置的雙 runtime、state/action/observation/reset/reward 與獨立 Evals。
REA／HAR／stateless replay 只能提供觀察或輸入，不能代替真實狀態轉移。
以 mutation→reset→readback 檢查工作樹、程序、瀏覽器及 fixture 污染。
JS／TS AST＋相容 SCIP 需實作及獨立 ground truth；99% 是未量測的 task-level retrieval precision 目標。
同時報 recall、coverage、abstention、母體與 critical misses；未解 critical edge 不得稱 CLOSED。

遵守重用目標→合法保留位元組 vendor→受支援 codemod→薄 adapter→另獲准的必要語義重寫。
以原程式及目標的實際數學、邊界、metamorphic、錯誤、雙向介面、DOM／ARIA、focus、效果次序與持久狀態判定嚴格 parity。
故意改功能是另一項任務。RL-ready、stateful DB/API 擴展及真正政策訓練／checkpoint 比較分階段驗收，後續需求不刪除。

同一監督 Session 保留完整 Goal、剩餘 REQ、卡片版本及原 valid next。
新證據推翻規格前提時，交 FactoryWeaver 原 Producer 修同 stable ID 的 revision 與 typed dependencies。
正確 SPEC 的程式錯誤修程式；錯誤 Oracle 交其原來源修正並保留失敗。
沒有 material change 時 CardDelta／PromptDelta 為 NOOP，繼續原合法 next。
Evals→卡片→下一 Consumer 的實際消費需獨立讀回；CognitiveStop 不等於 HumanGoalClosed。

## 可觀察交付與尚缺證據

本機候選目前提供完整上游 Git submodule、原安裝入口及 credential-free workflow。
本機原 demo 已觀察兩個 deterministic accounting tasks 的 parallel／sequential；相同 output 再讀沒有新 executor／editor 呼叫。
這些例子只驗證上游接線，不是完整 NeoWeaver 任務、訂閱角色證明、官方 benchmark 相容性或優化收益。
公開 workflow 尚需 exact-head Provider run；原 Test Manager 對 submodule 的 bound-source scope 仍需原責任入口處理。

完整 executable adapter、四角色訂閱 transport、可信 dispatcher、獨立驗收、形式化 Promotion、原生 outer＋inner 比較及 Migration-RL 各項仍未完成。
原 R3、指定舊 VM／Host、失敗與未知效果保留。H5 資源等待不能以新 Host 或額外模型進程繞過。
原 lifecycle、Grok 候選、guest 工具、Code Intel／品質指標、UML／呈現及必要文章義務仍沿原選定來源保留；它們不因本頁更新而完成。
