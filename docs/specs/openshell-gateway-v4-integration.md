# 共用 gateway 的完成後交接與 custody v4

本頁是來源及觀察紀錄。H4／H5 與完整方案已由使用者確認。原十項 REQ、44 Cards、同一 R3、OpenShell 隔離、原 owner 與原驗收保留。

本頁先保留前輪歷史。末節記錄本輪實際交接；前文的未完成狀態不能當成當前讀回。

## 已接受範圍

使用同一 gateway 的受管新入口統一走既有共用 Host。範圍包含 Loop、local task、相關 Issue、已安裝 CLI、Noodle 直接入口與實驗 runner。既有已接納或凍結的完整契約沿原 owner 完成，不由新預設改寫。

原任務依原契約完成必要的結果與資源結算、原 owner 證明清理合法後，才能沿原 maintenance 交易清理。S1／S2 已確認：同修推論與原 CLI，並將 gateway 控制權交接與舊 Host 程序退役分開驗收。活動工作、未結效果或未知狀態都不允許接管、Stop、重播或退回 process。第一次交接與升版可以等待；等待不是強制停止期限。

## 本次來源修正與實際讀回

Noodle source `1aa9f17b` 修正原 CLI 與 runtime：普通 open 仍拒絕 v3，不自動遷移。Schema-2 交接保存原 ledger、來源身分及 empty-resource 證據，取得同一 custody lock 後才升版 v4。原 119036b6 source 在取得鎖後先檢查格式；遇到 v4 即拒絕，尚未進行原生操作。新 client 拒絕其他 control root。這條防止重新取得控制權的路徑不要求 Host 程序退出，新交接也不發程序終止訊號。歷史 schema-1 退出證據及已保存停止交易仍只讀回、不重送停止。

原 journal reader 先前拒絕 writer 保存的 handover phases 與 cleanup-intent，實際破壞恢復。現在兩者使用相同分支狀態集合；handover 仍拒絕其他 maintenance 分支的 pause／checkpoint 階段。原 cleanup 拒絕保留 status／error／讀回失敗，不能從單一 unknown_effect 推成所有任務未完成或所有交接皆不可行。

接收端必須能讀 schema-2 交接收據；能力由原 native binary 回報 `gateway_custody_release=2`。此項相容性檢查只用於新交接，不擴成一般 admission 的新前提。同一交易重入不重寫完成的 ledger。受控的存活程序、鎖競爭及恢復測試不是現有 private Host 已釋放的證明。

原 v3 retained-init 拒絕的特定本機修復仍維持 v3；它不授權升版或原生派工。原 same-root first-migration 契約沒有被放寬成任意版本接受。新增 completed-owner 契約核對實際乾淨的 119036b6 來源。

前輪共用 Host 已沿原 rolling CLI serving custody-v4 binary。原 resources 讀回保留 Swap-used 上限 15,000,000,000 bytes、shared quota 4，並顯示零 context／worker／resident。該版本尚不支援 schema-2 release reader；新版本部署須另讀回。前輪部署不證明原 canonical custody 已升為 v4、private owner 已退出或 R3 已執行。

本輪修正版已沿原 rolling CLI 部署，共用 instance 為 `e935c09cb041d9b90e7046b03d8b4d3c`。原 serving binary 的能力讀回為 `gateway_custody_release=2`，Swap 上限與 quota 不變，context／worker／resident 仍為零。新版只讀交接預檢已實際消費三份原 request，仍拒絕 apply，並保留每份 cleanup 的 unknown_effect 與原 error。沒有執行 private cleanup、custody 升版或 R3 enter。部署完成與 gateway 交接仍是不同結果。

前輪 private Host 快照有三個 contexts、一個 worker、一個 gateway resident，並回報 memory_pressure。補入原 Soodles successor／retry reader 選定的三份 accepted request 後，只讀交接 plan 返回 executable=false、effects=[]。三份原 cleanup 均為 unknown_effect；共用錯誤未區分 Host fault、context fault 或缺少 context，不能據此判定每項產品未完成。這是被查入口的拒絕，不是所有合法續行均不可行的證明。原 sibling request 不是所有 contexts 的現行 request，不能以檔名重建來源。

新 CLI 的來源相容讀回不會替換 private Host 內正在執行的舊 observer。若工作完成後舊 observer 仍拒絕合法清理，必須沿原 owner 補相容性或效果證據。不能把本次共用部署或 fixture PASS 宣稱為該缺口已解決。

Soodles source 要求 native executor 支援 custody v4。已安裝的 Soodles 來自另一個含未提交修正的來源；本次只將 launcher 修正遷移到新的 versioned release，保留其餘已安裝程式。Noodle 的新預設 entry 指向相容的 versioned binary，原 binaries 保留。實際 help／capabilities 已讀回。這不是整個已安裝 Soodles runtime 或 active MCP 已換成本分支的證明。

## 驗證與保留的缺口

前輪 Test Manager 的一項 launcher 控制及 69 項 admission／readback controls 通過。本輪針對存活程序交接與 journal 續行，先保存修正前失敗，再完成 focused Host／runtime 控制、race、vet 與標準 pnpm 10.30.3 build。Soodles Test Manager 對三份指引選擇 meaning review，未要求重跑未變 Python runtime。先前失敗及本輪第一次編譯缺少 slices import 的紀錄保留。Go metadata 的 modified=true 來自仍保留的未追蹤 evidence；沒有改稱 clean build。

Python code-intel 的 source-bound native 結構已重新讀回。Go 的依據是原 source、build 及選定控制；沒有把它們當 guest Go 圖形或 metrics 的實際輸出。

三份變更 Neo 指引的四案例 P-class protocol 涵蓋拒絕範圍、存活 Host 的已證實交接、只有空閒鎖的反例與中斷恢復。初始 Session 條件審查及 INCONCLUSIVE 紀錄保留。獨立 reviewer 隨後指出一項 Oracle 過強：may_signal_old_host 混入合法退役的權限。修正版改問 requires_signal_for_handover，不改原要求。修正版 16 項條件均有獨立來源審查；三個未變案例保留相同指引／輸入／方法，受影響案例使用另一個 fork_turns=none 的 fresh consumer。

原生 standalone outer consumers 的實際輸出已沿原 Schema 納入；最終 criteria=SUPPORTED、evidence_validity=VALID、behavior.classification=PASS，返回的 consume_verified_behavior 已消費。原版 unsupported 條件與五份 consumer 原始輸出均保留，不用改預期掩蓋失敗。完整模型 transcript、實際 model version 與模型成本未取得，保持 unknown。此結果只支持四個案例的 consumer_report；不是 Noodle Stage、原私有釋放、guest 或 Provider 效果，也不是推論改善的比較實驗。

同一 R3 仍 not entered。真實共用並行、Grok→outer→原 Poteto→重審、guest 品質與 UML IR／metrics 回讀、同 Host 中斷與合法新 attempt 均仍未驗收。原工具 archives、來源控制、已安裝入口及共用部署各自留證，不互相替代。Medium／UML／文章及跨 Host／損壞候選的原義務與限制保留。

原始輸入及收據由 [compiled evidence](../compiled/openshell-gateway-v4-integration-evidence.json) 引用。Cards／Reader 僅提供知識提案，不能建立 admission 或關閉 Parent Goal。

## 交接前的原效果與能力缺口

故障 VM 的原 storage-failure 完成收據記錄 computeStopped=true、workspaceReturnAbandoned=true、taskOutcome=failed，仍有 unresolvedOriginalExecutions=true。原工具明確不改原 Exec outcome 或 live Host 的結算。不能把 VM 已停止推成原 worker allocation、context 或 gateway lease 已釋放。

本輪共用 Host 仍為零任務，原私有 Host 仍有三個 contexts、一個 worker allocation、一個 resident、兩筆 allocations。原 handover plan 仍為 executable=false、effects=[]。進一步的原 bound resident inspect 返回 persistence fault：rename residents.json 時 no space left on device，並保留兩個原租約。當前約 13 GiB 可用空間，不代表舊程序已解除記憶體中的 fault。

原 119 source 的 Residents.persist 會保存 r.failure，Snapshot／release 仍返回該錯誤；已查入口未提供驗證持久化後解除 fault 的能力。原 Quiesce 也保留未觀察退出的 Exec。這是原 live owner 消費故障／停止證據及結算的具名缺口；部署新 shared binary 不會改寫舊 Go 程序的記憶體或關閉原 Session.Done。只增加等待、重跑相同計畫或清鎖都不能當作修復。

同一 R3 保留，未 enter。本輪沒有新程式或 P-class 指引變更，不重跑未變測試或模型；既有 outer consumer_report PASS 也不代替本輪原 owner 的效果證據。這個入口的拒絕不證明所有合法交接皆不可行，仍保留原 CLI／相容恢復的責任邊界。


## B1／B2／B3／B4／C1 實際冷交接

使用者已確認將故障資源恢復分成兩段。退役前核對原 VM 已停止、沒有其他執行中工作、受管入口限制及精確程序世代。這些條件只允許原 CLI 執行已授權的限定退役。退役後才核對實際退出、租約、鎖與資源責任；全部成立後才能交接。不能要求資源先完成結算才允許退役，也不能預填後半段 PASS。普通已完成任務的交接仍不預設 Host 程序退出。未知原 Exec 保留未知，不等於所有基礎設施恢復都不可執行。

Noodle source a349538e8b970087feabb4d29fef41bf05a0f2f0 已完成必要控制、vet 與標準 pnpm build。共用接收端已沿原 rolling CLI 部署，原生能力回報 custody v4、gateway_custody_release=3，Swap-used 上限 15,000,000,000 bytes、quota 4。先前 schema-2 reader 的部署記錄保留為歷史，不代表目前仍停在 schema 2。

本輪原 CLI 的 maintenance 交易已返回 handover-completed。原 Host 已自然退出，沒有向該 Host 發控制。原 CLI 對通過前置檢查的專屬 gateway 與 driver 使用 kernel audit-token 綁定程序世代，並讀回實際退出。32 筆 custody Records 在 v3→v4 前後完全相同。原 canonical ControlRoot 已交共用 Host。舊非零資源帳目、storage-failure、failed task 與未知 Exec 保存於原交易，沒有改寫成成功，也沒有重播 Stop。程序已自然消失與同程序世代換 executable 分開判斷；後者保持 unknown。

同一 R3 原始 bytes 未變。C1 仍要求它沿原 Loop 入口真正 admission，啟動唯讀 OpenShell Stage，讀回原輸入、Poteto Skill 與來源。實際呼叫已被 App 的原資源 PreToolUse Hook 擋在 admission 前：目前已載入的 Soodles immutable snapshot 缺少 runtime／provider／profile 欄位。這是已觀察的 schema 相容斷點，不是 gateway 尚未交接，也不是任務已啟動。不得改寫 R3、略過 Hook、另走 process 或宣稱 Stage PASS。

相容整合保留已安裝版本的新 native carrier／Host switch 修正及新請求的 codex-app-server 預設；R3 明確選定 OpenShell。歷史未含 runtime 的 frozen local_task envelope 保留原 process 意義，不受新預設改寫；這是歷史讀回相容，並非本任務退回 process。原設定更新若要求已 entered request，會形成 admission bootstrap 的循環前提；本輪在原 configure／inspect 修正為可讀已驗證原 request，已有 entry 仍必須相同。它只更新已驗證安裝的 MCP／Hook 設定，不建立 entry，不授權 dispatch。原生信任、目前聊天載入及真正 admission 分開驗收。

三份 Neo 指引已更新上述兩段契約。四個具名案例、16 個判定欄位已由獨立條件審查及 fresh standalone consumer 支持，原 Schema feedback 為 VALID／consumer_report PASS，返回的 consume_verified_behavior 已消費。最初缺少 S2 原問答及不符合原始 bytes 的 quote 拒絕保留；修正來源與 quote，沒有改預期配合答案。此結果不代替 R3 Stage、Provider、guest 或整體模型品質驗收，也不把欄位數當成 Agent 決策數。

交接效果已完成；C1、共用並行、Grok→outer→原 Poteto→重審、guest 品質與 UML IR／metrics、同 Host 中斷與合法新 attempt 仍分別保留未驗收。Medium／UML／文章、跨 Host 與損壞候選的原義務及限制保留。Factory 的結構驗證、Reader、來源獨立性與語義審查仍分開記錄，不因本輪交接或 standalone consumer PASS 而關閉 Parent Goal。


相容 Soodles source 8e7066b7b32ca292707a66b65800e6278d72f362 已提交。不可變安裝保留原版全部 2,047 個檔案，完整 manifest 共 2,089 檔。原 configure 已完成 config.toml 與 hooks.json 的 journaled 更新。原 inspect 讀回 configuration=configured，fresh configured runtime 指向新安裝。使用者回報已完成本聊天 reload／Hook 確認，但隨後原工具回報的 MCP connection instance 仍為舊版，fresh 原生 Hook 讀回中六項 command Hook 為 modified、四項 MCP observer 為 trusted。因此目前聊天載入與新版 command Hook 信任尚未驗收；不以使用者回覆或 fresh server 啟動替代當前載入效果。

本輪 original Test Manager 的歷史失敗、來源修正及 scoped PASS 全數保存。最終修正的 35 項 admission、25 項 lifecycle、21 項 session readback、10 項 guest capture、15 項 configuration 與必要 directory／alias 控制已通過。原生同一 R3 仍未 admission。Code Intel 只對合併來源的三個 Python 模組完成原 source-bound native refresh；結構 ready 不等於 Stage 或資源效果 PASS。


## 同一 R3 的實際啟動與讀回斷點（2026-10-29）

本節取代前文「R3 未接納」的當前狀態；前文保留歷史。原 cold handover 已完成，32 筆 custody Records 保持原 bytes，舊失敗與 unknown Exec 未改寫。新工作仍使用既有共用 Host，Swap-used 上限 15,000,000,000 bytes、quota 4，未退回 process。

本聊天原生 MCP 已實際讀回相容版 8e7066b7。原 R3 之後被同一共用 generation 接納。Soodles 最初錯把固定 frontend 當成真正 admission binary，並要求 frontend 出現在該任務執行歷史。Noodle 原 pool CLI 允許同一 pool 的 frontend 轉送到當前 generation；原接納 binary 與執行 binary 各有回執。修正保留 request、設定、環境、原 pool 家族、binary bytes、generation 和 context 核對，外來來源仍拒絕。初次同 generation 轉送與跨 Host attempt recovery 分開；後者沒有因本次修正取得新能力。

控制程式修正保存在原隔離 controller worktree，提交 57f287e8、e3c56653、8a7882c2、31513884。R3 目標的原接納 base_head 8e7066b7 保留。曾把前兩個 controller 提交放進目標而觸發 task.base_head=changed；提交已完整保留到 controller，目標回到原 base。未改 request、envelope、來源或 native context。Host 建立 worktree 時新增的 .worktrees/ ignore 與原生 aliases 保留，未冒充 guest 改碼。

原 native order 為 soodles-task-9a255c1d680488a34695。唯一 attempt 為 soodles-task-9a255c1d680488a34695-0-attempt-0。其 runtime=openshell、provider=codex、model=gpt-5.6-sol、reasoning effort=low。canonical Stage 已從 pending 進入 running，現在為 review；attempt=completed。原 dispatch 記錄 Phase=settled、Exec exit 0 已觀察、Worker Boundary=stopped、Delivery=unchanged。這些事實不等於完整 native completion proof 或 candidate acceptance。

原 input、spawn、instruction mapping、五個成功命令、真實 raw trace 和 stage report 已保存。Session 對照命令的實際輸出，確認 10 份 materialized 來源，以及五份 selected/supporting Skill 的 SHA-256；其中包含 poteto-mode 與 investigation playbook。Guest 是 Linux aarch64，Python、Git、Go 不可用。Guest 的 0 B swap 不能推翻 Host 的 Swap-used 計帳。Stage 未跑品質工具、ub-mode、測試、發布、其他 worker 或 recovery。六個允許寫入檔案的前後 hash 相同。

候選與完整完成證明仍未通過。當前執行 binary 的 candidate-readback 只讀舊 runtime.process.admitted_orders，因此拒絕原 OpenShell runtime.admitted_orders。原 Noodle CLI 的最小修正已提交 4b2ad273；六個 admission 正反 table cases、routing 鄰例及 pinned pnpm build 通過，未替換正在承擔 R3 的 Host。新版唯讀 CLI 再讀原候選時，揭露新建立 durable worker 缺少 migration-only worktree binding。原 session-readback 另拒絕 successful settled result；來源顯示 dispatch.Target 保留 logical path，而 loop readback 將同一目錄 canonicalize 為 physical path後作字串比對。這是有來源支持的路徑綁定原因，未宣稱已完成 runtime 修正。明確請求的原 capture 保留拒絕並返回 UNKNOWN，具名缺口為 cost.session.path_escape。沒有刪除 path-escape、custody 或 native completion 驗證。

以上斷點位於 shared storage aliases 的 producer／consumer 對照，不是目前 gateway 租約未釋放，也不表示必須重送 R3。原 request 與已完成 attempt 保留，不盲目重播。下一個工程單位應沿原 storage、candidate、session 和 capture owners 統一路徑綁定及新 worker custody；先核對真正需要的來源條件，再作相容部署與讀回，不能只移除拒絕條件。

修正版控制程式已作 immutable 安裝，預設 CLI 與原 MCP／Hook 設定已沿原 configure 更新。本聊天已原生讀回 31513884 的新 MCP connection。設定、實際載入、Hook 確認及 R3 候選驗收各自保留；使用者的確認不代替原生效果證據。

P-class 三份 Neo 指引未因本次機械修正改字。原獨立 criteria、fresh standalone consumer_report PASS 及已消費的 Schema next 持續保留，只覆蓋其原四案例。新增程式控制由 Test Manager 分別記錄 33、3、39、1 個通過控制；測試 fixture 的一次 TypeError 失敗保留，重驗已通過。這些次數有重疊，不能相加成唯一案例或 Agent 決策數。完整 native stage feedback 仍受完成證明缺口影響；不能把 model 自報 acceptance_observed=true 提升為全生命週期 PASS。

C1 的原 R3 admission、真實唯讀 Stage 與 input／Skill／來源觀察已成立。候選接受、Grok→outer→Poteto→重審、guest 品質與 Go IR／metrics、共用並行、同 Host 合法新 attempt 恢復仍未驗收。Medium／UML／雙語文章與原 Parent Goal 保留。Factory Reader 只提供 source-bound 知識提案；原獨立語義與來源完整性條件不因本次狀態更新豁免。
