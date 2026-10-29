# NeoWeaver：15 GB Swap 共用 Host 與 OpenShell 接線

使用者已確認採用既有共用 Host。15 GB 指 Swap 使用量上限 15,000,000,000 bytes，沒有調整 RAM。這是 NeoWeaver 本次部署的選擇，不是通用 Neo route 的固定硬體要求。原失敗任務與歷史仍保留；新版驗收任務尚未建立。

## 來源與整合理由

先只讀其他 OpenShell 工作、實際 Host 與原封存來源。另一個工作仍保有原 worker 與 gateway，沒有新的 ProgressHead；本輪沒有修改、停止、接管或重派它。原 OpenShell checkout 仍為 7cda770b，沒有本輪寫入。

本任務原來源保存為 97433d91。既有 15 GB Host 的原來源為 8b8eda20 加原 sealed full patch；重建快照 a8e68c93 的 32 個變更檔案與來源逐一相符。整合提交 ee774bf313e1a1d9721bc6f2753e684658cc65f6 同時保留這兩條來源。這些是本機來源提交，沒有 push 或 Provider landing。

只換 OpenShell branch binary 會失去原 rolling／shared-quota 契約。因此本輪合併原 Host owner，而沒有新增 Host、獨立 budget 或替代執行器。Loop 派發前核對一般與 legacy admission；實際 runtime override 也受檢查。兩份非空限制同時存在時，兩者都必須接受。Legacy 綁定的失敗歷史保留；這項 retention 不授權執行。

指定既有 Host 的請求在 bootstrap 前就受限制。原 Host 不存在時，不啟動替代 Host。停止時，原 runtime 與 resident owner 確認資源效果，再保存收據及更新原 pool。Pool 寫入失敗時，context 與鎖保留，持久收據為 failed，不留下成功 detach。OpenShell 與 Codex native 都沒有 process fallback。

原共用配額的 exclusive 單任務租約不能表示 gateway 加 worker 的兩階段 warning grant。Rolling Host 因此在產生這種權限前明確拒絕；本次沒有使用 grant。一般 v2 admission 仍會計算 gateway 與 worker 的兩個 allocation，保留共用上限、啟動窗口、Swap、critical 與 unknown 限制。

## 已觀察的部署與測試

原正常建置已通過。正式 binary SHA 為 77d1b34274e329496f524616fa31eb896536008af57d66dc418e2fb79a3983c9，同時宣告 rolling、shared quota、OpenShell review、input materialization、tool payload 及 saved progress 能力。

原 host switch 接受請求 57504dcc60f29cbb19fde5e52ea0fad5，從 queued 轉為 active。新 generation 是 5cce4469f405f91db62eca479cde4b52，PID 87678。原 generation 9c26878c94a2c9e8c3a1af9f1308557c 已由原 owner 正常退出，原 PID 不再存在。沒有強制停止其他程序。

換版後原資源讀回為 ready。共用 quota 仍為 schema 2、maximum 4、Swap 上限 15,000,000,000 bytes，leases 為空。沒有 task dispatch。原 owner 的身分、狀態、歷史及維護 hold 保留。原 pool 重新序列化時，在 39 個 receipt 位置增加空的 admission_refusal 欄位；不能宣稱 JSON 形狀或 bytes 完全未變。第一個全等斷言失敗已保存，逐欄讀回後確認只有這項空欄位差異。

已完成的 race 控制涵蓋 admission、config、dispatcher、OpenShell runtime、Host 換版／停止／來源綁定，以及本輪受影響的 Loop 行為。較廣測試的失敗與後續修正分開保存，沒有把初次失敗標成通過。舊測試的 unsupported sampling、warning 全阻擋與無限啟動 credit 前提不符合 v2；修正 fixture 後保留原停止、配額、未知效果與歷史驗收。5 秒採樣間隔需要約 15 秒穩定窗口；原 12 秒測試期限錯誤已重新評估後修正。磁碟不足與誤選 pnpm 的原始失敗也保留。使用專案指定、本機已有的 pnpm 10.30.3 後完成建置。

原 Noodle Go analyzer 已對整合提交的 admission package 產生 source hashes、結構與直接呼叫資料。這是靜態 Code Intel，不是執行 trace、品質通過或 guest 輸出。

## Guest 與真實驗收的缺口

本輪透過原 build:instructions 與 build:progress 建置 Linux ARM64 verifier／supervisor。元件已放入本任務自己的 payload 副本；active profile 與其他工作的 payload 沒有修改。準備資料不是安裝生效或 guest execution。

原 LoadOpenShellProfile 對原 profile 與準備的 profile 均拒絕：它們引用的 0.1.5+noodle.refresh-drain.1/openshell-gateway 路徑不存在。另一個 Host 仍有原 gateway 程序與兩個 allocation。檔案缺失不證明程序退出，也不授權接管、重啟或以本機上游 0.1.5 binary 替代。這項原 gateway 來源／部署前置仍未滿足。

因此 Grok→outer→原 Poteto→新候選重審、guest Crapper／Dryer／Mutator、UML IR／metrics 真實回讀，以及新版歷史關聯任務的同 Host 中斷保存與合法新 attempt 都保持 NOT_RUN。跨 Host 與損壞候選恢復仍不在本輪通過範圍。Noodle／Medium 的真實結果展示、桌面與雙語文章義務保留。

## P-class、Schema 與證據界線

既有四份成品審查指引 bytes 未變。原 Schema inspect 仍為 VALID／PASS，範圍僅是 consumer_report。目前 Session 消費 consume_verified_behavior，沿原 owner 完成部署與來源更新，保持原生審查及恢復主張為 unknown。十二個輸出欄位不是十二次獨立流程決策；舊九項缺觀察 protocol 沒有被升級。

完整命令、原失敗、來源快照、部署讀回及元件在 rolling-openshell-t0zhi58c 證據目錄。Factory 應保留原 44 Cards／10 REQ、兩張 lifecycle 卡的穩定身分及 Parser Scope 的 NOOP。來源讀回及結構驗證不能關閉 Parent Goal、原生驗收或獨立語義審查。
