# Grok companion 與共用架構圖：契約及觀察

本文件承接已確認的 R1–R5、G1–G5。Neo route 的通用模型與 NeoWeaver profile
保留完整生命週期。ub-mode 只在候選形成且必要功能驗收通過後載入。
一般 outer 與 Poteto 不承擔新增審查工具成本；原 Formal／Test Manager 驗證照常。

## 已確認的交互

UML Viewer 使用本機 Grok CLI companion。Outer 提供來源分析及必要的最小片段。
Grok 不直接掃描或修改產品 Repo。Grok 可提出圖形 policy、補證據、指標刷新及改碼提案。
Outer 核對來源與既有授權後，沿原 Test Manager／Noodle 及 Poteto 執行，再將結果送回審查。
工程執行固定使用 OpenShell。跨 Repo 的首次對象是目前 NeoWeaver 成品涉及的
NeoWeaver、medium-compiler、factoryweaver 與 soodles 版本組合。

既有授權內的往返應自動完成。擴大需求、寫入範圍或未決產品取捨才詢問使用者。
圖上 policy 與提案不改寫來源事實，也不授權候選通過。無缺陷且證據充分才可 NO_CHANGE。
Session 結束後不新增背景喚醒。中斷保存原請求與結果，下次沿原入口續行。

## 原生觀察及限制

本機 Grok CLI 已完成 OAuth 登入。UML Viewer 原桌面已啟動，原 IR reader
接受 Go 的 EDN 投影；原 mailbox 已消費 display 命令。這不等於桌面佈局已目視驗收。
上游 Go LanguageGraph scanner 仍不存在；本次提供的是 Noodle 分析器與相容 EDN 投影。

Grok 原生檔案工具連續三次回傳 workspace session 未綁定，失敗 transcript 保留。
改用已確認的提示詞交互後，一次原生 Grok 回覆成功。它辨認來源分析與成品驗收的差別，
並指出跨 Repo 版本、來源、metrics 及 outer 回送介面缺失。這次沒有產品修改或品質刷新。
提示詞往返不證明自動 policy／刷新／Poteto／重審閉環完成。

本機 companion 使用 macOS kernel 規則限制產品目錄讀取與寫入；正反 probe 已通過。
它允許專用圖形 workspace 與 Grok home，保留必要系統讀取。這不是 OpenShell runtime，
也不取代工程執行的 OpenShell 隔離。Linux companion 尚未支援，不作無隔離 fallback。

## 共用 Go 資料

Noodle 分析器消費明選 package 的 go list／compiler exports、AST 與 go/types。
輸出 package、檔案、型別、函式、可解析直接呼叫、來源行號與原始檔案摘要。
型別大小跟隨目標 GOARCH；介面、函式值與 closure 內部路徑保留未知。
排除的 build 檔案與測試檔不在本次分析。靜態圖不能證明 runtime trace。
檔案摘要固定選定來源；module metadata 與依賴 exports 尚非完整可重現建置快照。

同一 JSON 可投影成原 UML Viewer EDN，亦由 Noodle 與 Medium 共用的唯讀元件顯示。
Medium 本機頁已有真實快照展示、來源鑽取及未知標示。預設建站不附私人快照。
Noodle 元件接在原 Loop artifact 顯示位置；實際 Host 工程頁端到端讀回尚未驗收。
原始 CRAP／coverage／mutation 未附在此圖，頁面明列未知，不從圖推算品質通過。
公開部署及雙語文章仍保留後續義務。

## 回饋及剩餘驗收

Go 直接／動態呼叫與目標架構控制、網頁來源及不可信文字控制、Python 投影與
companion 拒絕控制、Medium 私人資料預設排除控制已通過。Noodle 原建置已完成。
這些是本機局部觀察，不能替代 guest 品質工具與恢復驗收。

本次新 protocol 的 fresh Codex consumer 讀取七份已修改指引。
Schema 對十個案例輸出欄位回 VALID／PASS，原 next 為 consume_verified_behavior。
目前 Session 已讀回並消費結果，範圍只限 consumer_report；條件審查未宣稱獨立 reviewer。
前一輪缺九個 ub-review 觀察的 INCONCLUSIVE protocol 未被取代或升級。

原 Loop 最新回傳 Host unavailable，persisted context 尚未 detached。effects 保持空。
原 Host 相容部署、guest 品質工具、UML IR／metrics 原生回讀、合法新 attempt 與同 Host
真實中斷恢復仍未通過。舊 attempt 不重播，不以 process 或另一 Host 補成成功。
Grok 自動回送、policy 套用、指標刷新與跨 Repo 重審也仍未完成。
