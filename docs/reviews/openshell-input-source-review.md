# OpenShell local input 接線來源審查

本次更新只覆蓋 local task 的來源傳遞與原 admission/Stage 邊界。原十項 REQ、44 張 Cards、parser Scope、未決 K 與歷史 verification 均保留。僅 `SPEC-full-lifecycle-boundary`、`V-full-lifecycle-discriminating-controls` 從 revision 2 更新為 3。

## 原落差與選擇

原 local task 固定 process，Stage 指向 Host 的 Skill/source 絕對路徑。設定 OpenShell 並不能讓 guest 讀到這些檔案。此修改沿原 owner 的 `runtime/provider/profile` 契約；不另建調度、授權或來源 Reader。

Soodles 凍結明列來源、適用 AGENTS、selected/support Skill 完整檔案與模式。原 config 綁定單一 admitted order 和 manifest。Stage producer 將讀取路徑投影到 guest，Host provenance 仍保留。Noodle 在 Create 前驗證完整輸入與唯讀政策；原 transfer 上傳後，由同一 owned exec 驗證 bytes/modes，再啟動原模型命令。

只傳文字或列出 Host 路徑不能滿足這個要求：Skill 可能引用同子樹的腳本、二進位資料與其他 Markdown。完整檔案傳遞保留相對引用，也避免 prompt 截斷。特殊檔案、symlink 祖先、來源漂移與不支援能力明確拒絕。

## 證據及其上限

[來源與原 Owner 結果摘要](../compiled/openshell-input-evidence.json) 保存 Code Intel 的實際 source bytes/symbols、Noodle commit、Test Manager 收據摘要、原生拒絕和 Schema 結果。Code Intel 只提供結構定位，不能證明 runtime 行為。

歷史 29 項 admission、7 項 Stage/interruption、4 項 profile 修正控制通過。後續 seam 修正 13 項控制與最後 existing-envelope effort 拒絕/合法 Stage 鄰例 2 項通過。這些集合重疊，不相加為獨立驗收數。兩次失敗保留於摘要；修正了具名能力拒絕處理和測試 fixture/欄位，不降低產品 Oracle。Noodle config/runtime/loop/root 的 focused controls 為 PASS_SCOPED。

兩個 fresh outer consumers 的 8 個 reported fields 通過原 Schema feedback；目前 Session 已消費 `consume_verified_behavior`。這不是 guest consumer，也不代表工作流程選擇數、全 trace coverage 或 Parent Goal 通過。

實際 public Loop enter 在 Host attach 前回傳 `task.native_host.openshell_local_task_review=unsupported`，`effects=[]`。所選 Noodle input candidate 提供 `openshell_task_inputs=1`，但原 review capability 尚未提供。缺件時沒有啟動 VM、沒有替換共享 Host、沒有退回 process。

曾有 OpenShell attempt 的 Host adoption 仍缺可供原 CLI 消費的 native stopped readback。此版本保留具名拒絕，不製造 process PID。OpenShell reasoning effort 也尚未接到原生 carrier；新 admission 與原 new-effect boundary 明確拒絕指定值。這兩項限制不能寫成恢復或模型設定已完成。

## Source reconciliation 與 Factory 邊界

目前 Session 已讀回原來源與收據，核對 evidence summary 的來源摘要、兩張 Card 引用、per-type proposals、父義務和反例。新增 source 只支持本頁範圍，不能關閉任何未觀察的 native 義務。

原 Factory Validator 通過；semantic inspector 只回傳 SHAPE_VALID_SEMANTICS_UNVERIFIED；NeoWeaver artifact consistency 通過。獨立語義審查另存於本次工作證據。`card_delta` 因新增 sources 仍回傳 BLOCKED/original_source_owner_readback_required。本頁記錄 Session 完成的來源讀回，不改寫該 CLI 結果，也不把它變成 DONE 或執行授權。

## 剩餘驗收與接續

原 Noodle owner 完成 local-task review capability 後，先核對合併後 binary/profile/config 和來源傳遞介面，再沿原 request/admission 驗證。不得拿 input-only binary 假裝支援 review；後繼 Host 同樣重驗必要能力和原 profile。

Fresh guest instruction/source consumption、真實唯讀 enforcement、output retrieval、同 ID Stop/Stopped、恢復與 NeoWeaver 產品 acceptance 均未完成。未知效果先讀原 owner，不重送。兩種 provider 路徑、Issue 路徑、學習成果遷移、H0/H1、training、Medium 發布與 Parent Goal 保持各自的原要求。
