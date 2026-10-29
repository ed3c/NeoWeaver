# OpenShell 相容部署準備與原驗收界線

本輪先只讀檢查原 OpenShell 工作及 Host。原聊天已交接至新的 App worktree，仍在使用
progress Host。本任務沒有向這些聊天發訊息，也沒有修改它們的 checkout、Host 或請求。
原 closure.json 回 original_owner_closed。舊任務仍保留失敗與原 persisted context；
本輪原 Loop inspect 回 Host unavailable 與 original_request_readback，不宣稱舊 attempt 已恢復。

## 程式與建置

本任務 Noodle source 已有 manifest v2 tool_files、原 transfer／guest verifier、角色與
保存進度能力。為避免部署較舊的恢復及清理邏輯，本輪從原 owner 匯入六個原提交：
e20c1d10、2803a8cf、8f80bec2、70354e34、4f92a123、eadc56ab。
它們保留已保存 revision 的合法新 attempt、未知 merge、原執行證據及每個歷史 attempt
的原生停止讀回。清理不把 failed／cancelled 改成 completed，也不授權重試。

原 pnpm build 已通過。新 binary 的離線 review-capabilities 同時回
openshell_role_tool_payload=1、openshell_saved_progress_attempt=1、
openshell_instruction_materialization=1 與 local_task_roles=1。
對應 Linux ARM64 manifest v2 verifier 已依原 build:instructions 建置。
原 Go source 與嵌入網頁 bytes 已凍結，另保留原提交 lineage、整合 patch、建置輸出及 FileRefs。
來源 base 為 5ebbca7f 加未提交整合，build info 明確保留 vcs.modified=true。
這是待部署的成品，不是乾淨 revision、運行中 Host handshake 或 guest 成功主張。

## 原生阻斷與續行

本輪新鮮 resources 仍顯示 progress Host memory pressure=warning、effective_limit=0、
start_credit=0；其運行 binary 沒有工具 payload 能力。新 binary 與 verifier 都未部署，
沒有熱換 binary、修改 active profile、使用 warning grant、另啟 Host 或派發模型。
新版 CLI 的離線能力不能冒充舊 Host 已支援該能力。原請求完整保留。

相容部署及原資源 admission 尚未成立，故目前沒有建立替代 task。已接受的後續範圍仍是
沿原 admission 建立有歷史關聯的新驗收任務，再於該任務的同一 Host 驗證中斷、保存與合法
新 attempt。它不會採用舊 VM，也不構成跨 Host 或 native conversation resume。
Grok→outer→原 Poteto→新候選重審、guest 品質工具、metrics／UML IR 真實回讀均未通過。

## P-class 與驗收證據

本輪四份既有 P-class 指引的 bytes 未變，未重新啟動相同 native consumer。原 Schema
inspect 重讀仍為 VALID／PASS，scope=consumer_report；目前 Session 消費
consume_verified_behavior，保留原結果及限制。這不新增 native 工程效果或恢復 PASS。
新 runtime 程式整合由對應 Go 控制另行驗證；完整結果保存在同輪部署證據紀錄。
Medium 展示與文章／公開部署義務保持原範圍，沒有用本輪準備結果關閉 Parent Goal。

證據根目錄：/Users/neon/neo-route-evidence/grok-review-integration/deployment-compatibility。
主要讀回為 original-loop.json、resources.json、capabilities.json、compatible-binary.json、
guest-verifier-prepared.json、build-source-snapshot.json 及 schema-readback.json。

## 整合驗證找到的未變更成果缺陷

首次四套件驗證中，Loop、instructionbundle 與 workspaceartifacts 通過，runtime 失敗。
原 TestOpenShellRuntimeStopPreservesProgressAfterBothNativeExits 的 unchanged=true
回 retained publication identity is incomplete。這是新 cleanup Reader 只接受 published／
Applied 與本任務原 unchanged publication 的相容性缺陷，不能當成 fixture 問題。

修正保留原 producer 的兩種結果：published 必須是原 baseline 的直接 child commit；
unchanged 必須 Applied=false、head=baseline.Head 且原 patch 為空。兩者仍以同一 Reader
核對原 baseline、returned 副本及 Git tree bytes。未知結果、偽造 HEAD、非空 patch 或
changed bytes 都拒絕。原 runtime 測試仍要求 cancelled 與 ProgressHead，並拒絕將其當
completed。沒有建立空 commit、改寫歷史 FAIL 或放寬原生停止及部署條件。

第一版建置及來源快照保留為修正前證據，不能用來部署已知缺陷。修正後 binary 與
聚焦 race controls 另行保存，最終結果見同輪 compiled evidence；原 guest／恢復驗收仍未執行。

修正後聚焦 race controls 已通過：原 retained publication 正／反例、unchanged publication、
OpenShell 中斷保存與 cleanup。新的六個子案例涵蓋乾淨結果、錯誤 HEAD、非空 patch、
錯誤 Applied、兩份同時變動的 return bytes 及 unknown state。它們不會操作真實 VM。
