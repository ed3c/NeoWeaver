# OpenShell 新版接線與 15 GB Host 的部署界線

使用者要求保留 Neo route、原 owner／CLI、OpenShell 隔離與既有驗收，並換成 15 GB Host。
本輪沒有修改 RAM 配置或選定新的 runtime。15 GB 的對象仍在向使用者釐清。
本機實體 RAM 是 16 GiB。另有名稱含 swap-used-15gb-maintenance 的既有共用 Host；
其原資源讀回明確設定 swap_used_limit_bytes=15000000000，而非 15 GB RAM。

## 原工作與已整合來源

其他 OpenShell 工作已部署 a2e03b6d。其原 Host 有一個 worker／gateway resident；
公開停止測試卡在成果回傳，沒有 ProgressHead，沒有啟動新 attempt。其後下載路徑
修正已提交 7cda770b，但原已執行效果尚未完成維護恢復。這些是另一個原任務，
本輪只讀，沒有接管、停止、重派或修改它。

本任務 Noodle source 匯入原 7c18ec4b、a2e03b6d、7cda770b 的相關 Host／UI／runtime
修正。原 Harness2 adapter 的兩個檔案不在此 target，且不是選定 Host 契約的依賴，
因此不複製或重寫它們。原 StaticPreview 及測試另從固定 7cda770b 來源完整遷移。
它補齊原控制頁缺少的前置元件，不以自製預覽取代來源。

整合保留原 ExpectedVersion、RequiredHostInstanceID、角色工具 payload、輸入驗證及
保存進度能力。下載成果位於原允許的 /sandbox workspace，仍在 repo／session 封存
樹以外。沒有使用 /tmp 路徑冒充可由原下載器回傳。

修正版候選已建置，離線 CLI 同時宣告 openshell_role_tool_payload、
openshell_instruction_materialization、openshell_saved_progress_attempt、
existing_instance_admission 與 openshell_warning_grant。後者存在不是本任務的 grant 授權。
Linux ARM64 verifier 與既有來源 FileRef 相符，未替換 active profile。
這個候選沒有部署，也不宣稱支援 rolling Host／shared quota。

## 15 GB 共用 Host 的實際限制

該既有 Host instance 是 9c26878c94a2c9e8c3a1af9f1308557c。資源快照回 ready、
start_credit=1、Swap 使用約 3.7 GB，Swap 上限 15 GB。其離線能力未宣告原生
OpenShell review/input/tool payload/saved-progress。readiness 不能補上這些能力。

原 host switch --maintenance-plan 對本輪候選明確回
target lacks compatible rolling Host and shared-quota contracts。
因此不能直接把這個 OpenShell branch binary 換上該共用 Host。原維護規劃僅讀回，
沒有執行 switch、改變配額、建立新 Host 或替代 request。

真正採用該 Host 時，部署候選必須同時保留它原 rolling／shared-quota 契約及所需
OpenShell 能力；不能以另一個獨立 budget 或改 RAM 數字解決相容性。
Host 選擇尚未完成，原任務請求與既有失敗均保留。舊任務 Host 已關閉；
本輪原 Loop inspect 仍拒絕 original_request_readback，沒有跨 Host 恢復主張。

## 驗證與剩餘義務

第一次建置／root 測試缺 StaticPreview；遷移原元件後修正建置通過。原始失敗保留。
前端第一次測試遇 ERR_REQUIRE_ESM，明選本機既有 Node 22.23.2 後七項測試通過；
型別檢查與 lint 通過，沒有停用測試或降級相依套件。
聚焦 Go race controls 通過：原 Host 身分／context／角色與 capability；
原 admission／instructionbundle／loopview；原中斷保存、下載路徑及 cleanup。
這些都是本機控制，不是 live guest 或成品品質審查。

四份既有 P-class 指引 bytes 未變，原 Schema inspect 仍為 VALID／PASS，
scope=consumer_report。目前 Session 消費 consume_verified_behavior，保持其限制。
沒有重跑相同 consumer，也沒有把原拒絕改為部署或修復成功。
Grok→outer→原 Poteto→重審、guest 品質／metrics／UML IR 與該任務同 Host
的中斷保存／合法新 attempt 仍未驗收；不退回 process。

完整證據在 host15-readback-nrov399b 目錄；結構與程式來源為原生 Go analyzer、
固定提交 patch、preview-prerequisite-source.json 及 integrated-candidate.json。
這是來源忠實敘述，不是獨立語義審查或 Parent Goal closure。
