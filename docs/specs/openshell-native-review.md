# OpenShell 原生成品審查：來源修正與驗收邊界

本頁補充既有成品審查規格。原十項需求、完整生命週期及 Parser 的本機驗收不變。
使用者要求沿原 owner 完成角色交接、guest 工具、結果讀回及恢復，不得改用 process。
ub-mode 仍只在候選成品及原必要功能驗收成立後載入。Formal／Test Manager 的原責任不變。

## 原因與修正

Soodles 的原 task admission 現在凍結完整 instruction manifest。
角色 producer 保留原來源 provenance，加入該角色選定的 Skill、支援來源與任務。
原角色 reader 拒絕來源漂移、不同角色的 manifest 與錯誤上下文。
原必要完成及 Stop 證據成立後，候選 owner 才能交接下一角色。
OpenShell 建立新的角色 session，不宣稱原對話續接。

一次真實 OpenShell Poteto 唯讀任務讀到了選定 Skill 和來源，卻沒有讀到生成的
local-task wrapper。原 admission 已修正：wrapper bytes 納入同一 manifest，
不另建平行傳輸。測試核對保存 bytes 與傳輸 bytes 一致。

同一次任務正常退出，但沒有改動產品。原 runtime 只在套用差異後保存候選，
因此未保存 CandidateHead 和 publication receipt，原 completion reader 正確拒絕。
修正沿原 workspaceartifacts producer 保存未變更的原 HEAD。
producer 先檢查空 patch、原 HEAD、index 與工作檔案未漂移，再保存 unchanged receipt。
它不建立空 commit。reader 核對同一 publication、原 native identity 與停止證據。
改動候選仍使用原 publication 路徑；unknown 不會變成未變更候選。

## 證據與未完成範圍

Soodles 的來源／角色控制與 Noodle 的正反控制已通過；Noodle 原建置已完成。
這些結果支持本地修正，不代表新版本已部署。
實際 guest 是 Linux aarch64，缺少 Python 與 Git。
審查專用的離線 CPython、Git 及 Python 品質工具已準備，尚未在 guest 執行。
一般 Poteto、outer 與共用 profile 未加入這些依賴。

共享 Host 仍使用原版本，另一工作仍在使用它。新 binary 不能冒充原 Host client。
原 task、request、原始 trace 和失敗 receipt 保留，不重播已停止的 VM。
原生 ub-review 交接、工具指標、完整結果回讀、修正回送與恢復驗收仍未完成。
跨 Host 的已執行 OpenShell task 恢復與損壞候選恢復仍不支援。
部署後的合法新執行仍須沿原 admission，不能改寫舊 receipt 宣稱已修復。

Schema 的 native-review 結果是 INCONCLUSIVE，缺少真正的審查角色觀察。
原 next 是 supply_behavior_evidence。初始 Poteto trace 不能充當 ub-review consumer。
Factory 的結構、Code Intel、Session 來源審查、native 行為與 Provider 效果分開記錄。
本頁不證明 CRAP／duplication／mutation 達標，也不關閉 Medium 或 Parent Goal。
