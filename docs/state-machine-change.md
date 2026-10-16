# 狀態機修改契約：NeoWeaver 套用

修改 AGENTS.md、P-class、CLI 狀態機或其敘述時，讀取
[狀態機修改契約](../references/soodles/ef828ca0b236d980607299d727f13cda0c290765/state-machine-change.md)。
[來源紀錄](../references/soodles/ef828ca0b236d980607299d727f13cda0c290765/SOURCE.json) 固定 Soodles commit `ef828ca0b236d980607299d727f13cda0c290765` 與原文 digest。
這是未改寫的離線快照，不宣稱該 commit 已發布到遠端，也不需要執行 Soodles 才能讀取。
通用規則只在原來源修正後更新版本；本頁只補本 repo 的接口與效果邊界。

## 獨立使用與原責任

NeoWeaver 保留 parser、harness、PatchProposal 與原 oracle。不得因引用契約改動 frozen acceptance、training eligibility 或將未觀察的效益宣稱完成。原測試及 Schema feedback 要求仍有效。

Session 對照原需求、P-class 條件、CLI 轉移與實際觀察，只修正有證據的落差。
一般設計或本 repo 的獨立修改不因使用契約而建立 Noodle、Issue 或 LoopManager 身分。
既有 AGENTS 指定的 review-writing、Test／Schema feedback 仍按原條件使用。
引用 skill、執行唯讀回饋 CLI 與啟動 worker 是不同能力；不能一律改成必跑所有 Managers。
格式或 digest 通過不證明完整語義正確；沒有新語義問題就消費原有效 next。
未知寫入先原 owner readback，不重播、不從 operation 名稱猜命令。

## 按需委派執行

本機任務明確選用小迴圈時，沿 [Repository Loop 入口](loop-entry.md) 傳遞原 request。
選擇由當前需求決定，不以 repository 名稱固定模式，也不重選已有合法 continuation。
`outer-only` 只回傳來源綁定投影，沒有自動模型推論；Session 按需使用 Thinking Router。
`inner-only` 沿原 admission；`outer-inner` 在必要投影成立後沿原 admission。
需要 inner 時使用共用 Noodle Host、獨立 worktree 與全機資源額度，不另開 daemon。
本機 adapter 不是雲端 capability；既有雲端流程保留原 Host 與權限。
Hook 只對實際原生事件，Cron 只對已授權排程，發布沿原 Provider。

有資料依賴的跨 repo 交接等候必要成果成立，獨立部分才可並行。
只用原入口實際支援的交接種類，不把 local task 介面冒充所有模式的通用交接。
Card、PromptDelta 與 DAG 都不能新增 admission 或改變驗收。

## 更新、安裝與驗證

更新快照時核對原 commit 的 bytes，新增版本並更新本頁連結，不修改快照內容。
這是文件安裝核對，不是每次執行都要查網路或跑的 gate。
安裝保留 repository 相對路徑，從實際安裝位置讀回本頁、原快照與入口。
Adapter 的 request.repository 必須等於該 adapter 所屬 Git checkout；安裝副本不接管另一個 checkout。
要在另一個 worktree 執行，先在該 worktree 採用同一版本的 adapter 與指引。
驗證區分來源／連結、Agent 實際讀取、原生 CLI 轉送、inner 行為與 Provider 效果。
假的 launcher 不能證明原生交接，outer-only 成功不能證明 worker 已執行。
保留未測與 unknown；文件存在不證明既有 chat 已重新載入 AGENTS。
