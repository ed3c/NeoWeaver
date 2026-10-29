# 原租約等待期間的審查清理與 guest 資產續行

本次先只讀核對其他 OpenShell 工作。原 Pi 候選已完成整合，但原 Host 仍有租約。
原聊天回報後續已啟動新 solver。另一次原生資源快照顯示三個 context、零 worker、一個 running gateway resident。
聊天回報與 context 增加是不同證據層；兩者不建立該 solver 的 native 驗收或 R3 執行證明。
這些觀察只屬於另一項工作，不算 R3 的執行或驗收。零 worker 與 task completed 都不證明租約已釋放。

## 新觀察到的清理斷點

原 Host 的只讀 cleanup inspect 回傳 unknown_effect。它把一個被要求修改的舊 attempt
當作 saved interrupted progress。實際原來源顯示：canonical attempt 為 failed，
但同一 session 的 OpenShell dispatch outcome 是 completed、exit 0，並有已發布候選。
這兩種狀態分屬審查處置與 runtime 結果，不應互相改寫。

本任務 Noodle 分支的 b2e9391d 修正原 cleanup observer。對 OpenShell local task 的
request-changes 舊 attempt，原 typed StageFailed／OrderFailed 事件、同 order 的合法
requeue 與後續 attempt 必須配對。驗證成立後，observer 按 completed candidate 讀原 runtime。
原 runtime 仍核對 session、來源、封存、publication、Stop ACK 與同 ID Stopped。
缺事件、身分／理由不符、未 requeue、來源漂移或 native unknown 仍拒絕。
canonical failed 歷史保持不變。這個讀回不批准重試或候選。

原 CLI 的失敗是 pre-fix 真實觀察。修正版通過 focused race controls、標準 pnpm build
與 go vet，並已透過原 rolling switch 部署到既有共用 Host。
它沒有部署到另一項工作的私有 Host，也沒有替該工作 cleanup、Stop 或接管 gateway。
因此不能把本分支的 source PASS 當成原私有租約已修復或釋放。

## 只供成品審查的 Linux Go 圖形資產

Noodle 可切換審查 set 的 ignored runtime/linux-aarch64-review-v3，保存新 Go 圖形封存。
它包含 Linux／ARM64 ELF 的 noodle-review-graph 與原 EDN projection script。
原 build:review-graph 在固定來源副本交叉建置，沒有執行圖形分析或品質工具。
原 InstructionInputs 驗證六個既有依賴封存加新封存，共七項、182,694,982 bytes，
仍在原 tool-input 限制內。原 v2 資產與正常 Poteto／default profile 不變。

這只完成資產準備。尚未建立 review role，也沒有捏造 order 或 candidate。
guest bootstrap、執行、Go 圖、Python IR、品質指標與結果回讀仍為 NOT_RUN。
原 UML Viewer 沒有新增 Go scanner；EDN 是共用 Go 資料的投影。

## 同一 R3 的來源與交接

Soodles 的 c3b59af6 保存本 Session 已驗證的 shared owner、companion、artifact reader 與 Neo 指引。
原 admission 要求的 clean source 與 named integration branch 已在本 managed worktree 滿足，
主 working tree 沒有切 branch。R3 request bytes、SHA、model／effort、profile、原 binary 引用及
原入口 next 均保留；原 Loop inspect 仍是 not entered，effects 為空。
舊 frontend 可讀新版共用 Host 的 root、generation 與 execution reader，不等於 admission。

既有六模組的 263 項 source controls 保留為相同程式 bytes 的 pre-commit 證據。
本輪新增讀回原 Test Manager 選出的五項 companion transport controls，均通過。
這些結果不冒充新 HEAD 的 CI 或任何 native candidate acceptance。

本輪對六份已保存 Neo／companion 指引取得 fresh outer consumer。
獨立審查支持十五項條件，原 schema-2 feedback 為 VALID／PASS，原 next 已消費。
其範圍僅 consumer_report。完整模型 transcript、成本及決策總數仍未知。

## 保留的原生義務

同一 R3、額外有界只讀並行、逐 context 政策／清理、Grok→outer→Poteto→重審、
guest Python／Go 品質與 UML IR／metrics、同 Host 中斷與合法新 attempt，均未因此通過。
它們仍等待原租約與未知清理效果依法解決。沒有第二個 gateway、額度繞路或 process fallback。
跨 Host 與損壞候選恢復仍不支援。Noodle／Medium／UML 與雙語文章各保留原交付義務。

本頁限定前版對新 solver 的來源歸屬。前版、原始快照與獨立審查的 incomplete 結果仍保留。
