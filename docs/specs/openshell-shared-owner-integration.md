# 共用 Host／gateway 統一接線的實作與驗收邊界

本頁記錄已確認方案的實作，不代表整個 NeoWeaver 生命週期完成。
共用 Host 保留 Swap-used 上限 15,000,000,000 bytes、shared quota 4 與原政策 v2。
Gateway resident 也計入原額度。原 R3 request、歷史與 admission binary 沒有改寫。

## 原來源與 runtime

新 Loop／local OpenShell admission 在 task envelope 保存原 CLI 回傳的 host_binding。
Soodles 不繼承 ambient 私有 Host 目的地。既有 request 沿原 owner，不強制遷移 Issue、
Noodle 直接入口或已接受的專用任務。缺少共用能力時拒絕，不 bootstrap 替代 Host。

只修改環境變數不足以修正回讀。原 request 固定 admission binary，pool 可以選相容的新 generation。
Noodle 現從原 pool Original／Current、config、環境摘要與唯一 context receipt 產生 owner_binding。
投影包含 request、兩種 binary、pool 與 generation receipts 的來源引用。
Soodles 驗證完整來源鏈，再使用原 execution binary 的 session reader。
展示和資源操作固定同一 root。無證明的異版本、來源漂移或未知 attach 不得通過或重播。

原 rolling owner 在 OpenShell context 租約存在時保留版本 queue，不搶同一 gateway custody。
正常共用 admission 不要求整台 Host 空閒，仍由原資源採樣及 quota 判定是否允許。
manual context 不因模型退出自動釋放。本任務完成驗收及整合後沿原 cleanup inspect／apply。
最後租約結束後，才由原 owner 進行 native Quiesce／refresh drain／child exit／custody close。

Noodle 實作提交 5563df85 與 2b7b3889。後者只整合原維護來源真正缺少的四個增量，
保留本分支較嚴格的封存及 publication 控制，沒有覆寫其他工作的 checkout。
原必要競態控制、標準建置與 go vet 已通過。Soodles 的六個聚焦模組共 263 項通過。
先前文件保存造成 source drift 的拒絕仍保留；通過結果來自固定來源後的原 Test Manager 新收據。
Code Intel 的六個 Python 來源是官方 SCIP／AST 結構證據，不是 runtime PASS。

## 部署與剩餘前提

新版 binary 已沿既有 host switch 部署到共用 root。原 R3 frontend 已能只讀取得當前 executor。
共用 root 仍使用原 Swap／quota；未建立第二個 gateway、grant 或資源帳。
另一工作仍保留兩個 context 與一個 running gateway resident，當次讀回 worker 為零。
零 worker 不等於合法釋放。該工作仍在處理原 Pi 候選審查，沒有被本次接管或中斷。

因此 R3 原 inspect 仍為 not entered，原準備收據與入口保留。
本輪不執行已知會與另一 owner 衝突的 admission。新增有界只讀並行任務的授權仍保留，
須在合法交接且資源允許後，驗證同 generation／gateway 的真實重疊 worker／exec。
兩個 context 或順序執行不能冒充並行。新 task 仍需獨立 VM、政策與來源。

Grok→outer→原 Poteto→重審、guest Python／Go 工具與 UML IR／metrics、同 Host 中斷讀回
與合法新 attempt，均保持 NOT_RUN。跨 Host 及損壞候選恢復仍不支援。
Noodle／Medium 本機頁、UML 桌面與雙語文章仍保留原交付義務。
不因部署、工具安裝或模型退出宣稱它們已完成，也不退回 process。

## P-class 與 Factory

通用 Neo 模型加入單一租約與停止責任；NeoWeaver profile 加入具體原 owner 接線及等待條件。
獨立 fresh 外層 consumer 的七項決策由 schema-2 feedback 判定 VALID／PASS，
原 next consume_verified_behavior 已由目前 Session 消費。此結果只覆蓋 consumer_report。
它不證明 native OpenShell 執行、並行、Provider 效果或 Parent Goal。
Factory 只更新原 lifecycle SPEC／V，保留原 44 Cards、10 REQs 與其他 42 Cards。
原 Reader 只返回來源支持的診斷，next=null 不授予 admission。
