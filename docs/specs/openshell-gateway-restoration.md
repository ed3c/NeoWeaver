# NeoWeaver：原 gateway binary 恢復與交接前置

本輪延續既有 Neo route、15 GB Swap 共用 Host 與原 owner／CLI。沒有調整 RAM、建立獨立 budget、使用 warning grant 或退回 process。原共用 Host 仍為 generation 5cce4469f405f91db62eca479cde4b52；本輪快照為 ready、沒有 allocation，Swap 上限仍為 15,000,000,000 bytes。

## 先讀原進度

其他 OpenShell 工作正在實作同一 request 的派工後維護恢復。其最新公開進度要求固定原 session 的一次性 Stop 紀錄、未完成維護的啟動 fence，以及 gateway／Host 關閉證據鏈。這些尚在實作與審查中，不能當作已部署的能力。本輪沒有修改該 checkout，沒有停止、接管或重派它的任務。

本輪先搜尋原建置成品與收據。原成功 binary 與版本化安裝路徑都缺少檔案，但來源封存、修補檔、prepared.json、原建置收據及 Z3 封存仍存在。這不能推論執行中的 gateway 已退出。

## 以原 producer 恢復相同 bytes

使用原 examples/openshell/native-patches/refresh-drain/build.py。固定 upstream bdb956f2cd65a635f1294fccf1d138d263bf650f、原修補檔與 Rust 1.95.0。原程序核對來源封存、修補檔、完整來源樹及 Z3，採單一 Cargo job、locked／offline 依賴，前後來源樹保持相同。

第一次在本任務獨立目錄建置成功。版本是 0.1.5+noodle.refresh-drain.1，但 binary SHA 為 746020dd9217ef92bd6f65cd7431be5aacb8c672ba8f923ddc2265fd959350dd，與原收據不同。相同版本或來源樹不能證明相同 binary bytes。本輪保留此成品，沒有把它當作原 binary 恢復。

第二次沿同一原 build CLI，在原建置位置執行。原 source inputs 未修改；只有 producer 的建置輸出及新收據新增。成品 SHA 恢復為原 375d1330904e41edc980ce7ecde5a55758938d78eb70fe33f47cc5ce20455c49，來源樹及 pin 與原成功收據相符。

核對相同 SHA 後，使用既有完整 bytes 的一次性發布 primitive，原子補回 profile 指定的缺失版本路徑。有不同內容時拒絕覆寫。本次目的路徑原先不存在；沒有替換執行中程序的映射，也沒有啟動服務、操作 VM 或讀寫真實憑證。這是原 binary 檔案恢復，不是現場任務恢復。

原 LoadOpenShellProfile 現在可讀取原 r09 profile 與本任務準備的 profile。兩者 Gateway Binding 都等於原 custody 的 Binding；task payload 可以不同，但沒有另建 custody root。準備的 Linux ARM64 verifier／supervisor 保留前輪來源，active profile／payload 沒有被修改。

## 實際驗證及原效果讀回

兩個成品各自使用原 native acceptance CLI，通過 issuer-pending、replacement-store-pending、builtin-db-issuer-pending-group-term 三個場景。每個成品的六個 gateway child exits 都已觀察。測試使用真實 gateway binary 與隔離的合成 issuer／credential／compute peers；沒有真實 grant、模型或 VM。它支持關閉／持久化機制，不等於現場關閉或 guest 審查驗收。

現場使用原唯讀工具，只呼叫 ListSandboxes、GetSandbox、GetProvider、GetProviderRefreshStatus。profile Ref 取自原 admission envelope。沒有取回 credential 值、Create、exec、Stop、refresh、import 或 rotate。另用原 custody-summary 讀兩次穩定來源，沒有取得或替換原 custody lock。

本次非原子快照有 19 個 native Get，身分與完整 spec 摘要都對應原 custody 的 19 個紀錄。其中 18 個 Stopped；目前 worker 的 VM 仍為 Ready，沒有 Stop ACK 或 Stopped 證據。原 exec 與 progress-stop exec 都有 native ExitObserved。這不授權釋放 gateway。

原 inventory 工具以靜態 route spec 判定 retained 初始化，對這些歷史／任務化 spec 回 UNKNOWN，沒有產生 retained.json。另做原 custody spec 摘要對照後，19 個均相符；這是來源對照，不改寫原工具結果或發出交接權限。重複的 problem 名稱不是不同 VM 的數量。初次診斷誤用 sandbox_id 取代原 Go schema 的 SandboxID，失敗投影保留；依原欄位更正後才完成對照，沒有重跑或修改 native 效果。

## 原 continuation 與剩餘義務

R3 已接受的歷史關聯新驗收請求，已由原 Loop prepare 保存為 live-request-r3.json，next 為 soodles_loop_enter。這只保存 request，尚未 admission、建立 native task 或派發模型。舊 live-request-02.json 與其失敗保留。準備的第一階段為 Poteto 只讀 investigation；ub-mode 與工具封存仍由候選形成且原必要功能驗收通過後的獨立 review role 載入。

原 gateway custody 仍由另一個 active Host 持有。派工後維護的實作／驗收尚未完成，現場原停止、gateway 釋放及 Host 退出未形成完整交接證據。不能因共用 Host 有額度或 profile 已可讀就另開 Host、custody root、endpoint，或重派同一效果。本輪保留同一準備 request，沒有嘗試已知會衝突的 admission。

因此 Grok→outer→原 Poteto→新候選重審、guest Crapper／Dryer／Mutator、UML IR／metrics 回讀，以及同 Host 中斷保存／合法新 attempt 仍為 NOT_RUN。原生 P-class review case 沒有因 artifact 測試而通過。跨 Host、損壞候選、真實結果網頁／桌面及文章義務保留，Parent Goal 仍 OPEN。

原四份指引 bytes 未變；Schema inspect 為 VALID／PASS，scope 僅 consumer_report。目前 Session 消費 consume_verified_behavior：核對原 bytes 後恢復檔案，保留原效果與 prepared request，不以另一個 carrier 填補觀察。它不證明 native review、恢復或決策成本改善。

完整來源、原失敗、建置／測試收據、安全 native projection、profile 讀回與 request，保存在 gateway-continuation-_9syetd0。只清除本任務獨立建置的中間產物，保留 binary、來源、收據、logs 及 native 測試證據；沒有刪除其他工作的資料或 live binary。
