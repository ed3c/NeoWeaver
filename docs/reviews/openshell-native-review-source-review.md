# 原生成品審查來源讀回

本次是目前 Session 對原來源及保存結果的審查，不是獨立 reviewer 的驗收。
來源為使用者目前的 OpenShell 接線要求、原 runtime 拒絕、guest trace、
Soodles 的角色／materialization 來源與 Code Intel，以及 Noodle 的原候選 producer。
新增來源保存在 `docs/specs/openshell-native-review.md`。
Factory 原 producer 已固定來源 bytes；外部 readback 核對保存副本與 repo 原文相同。

| 卡片／關係 | 審查結果與反例 |
| --- | --- |
| SPEC-full-lifecycle-boundary，revision 5 | ACCEPT，限來源支持的候選契約。角色 manifest、wrapper、unchanged candidate 與停止證據各有原 producer。缺 wrapper 或 candidate receipt 時，即使模型正常退出仍不能交接。 |
| V-full-lifecycle-discriminating-controls，revision 5 | ACCEPT，限判別控制與局部觀察。更換角色 manifest、來源漂移、非空 patch 與 unknown delivery 應拒絕。實際 native 失敗保留，不能用修正後單元測試改寫成原生通過。 |
| SPEC implements REQ-full-lifecycle | SUPPORTED。這是完整生命週期中的審查交接邊界，不改十項原需求。若刪除原候選及停止條件，正常退出可能被誤當交接授權。 |
| SPEC validated_by V | SUPPORTED。方向仍從行為指向驗證。缺少 V 的來源漂移及 unchanged 負例，無法區分合法唯讀候選與未保存或已漂移的候選。 |
| 原 Parser Scope／PromptDelta | REUSE／NOOP。此次來源更新不新增 Parser 任務，也不改原六張選定卡與本機驗收。已有原 native request 及拒絕續行，不重新建立派發授權。 |

四個顯示槽位為 SPEC UPDATE、V UPDATE、UNUSED、UNUSED。
原十項需求、44 張 stable identity 和歷史證據保持不變。
原 Factory validate、per-type inspect、coverage 與 NeoWeaver consistency 均已執行。
inspect 的結果是 SHAPE_VALID_SEMANTICS_UNVERIFIED；結構工具不認證本表的語義判斷。
原 Delta 仍保存 BLOCKED／original_source_owner_readback_required。
目前 Session 已讀回新增 Source、原始失敗及修正來源；這項 source reconciliation
另行記錄，不把 comparator 的不可變輸出改成 DONE。

工程文字依 Soodles `review-writing/features/ste-reference.md` 的 1.5–1.13、
3.6–3.7、第 4–6 節及 GR-3/GR-4 核對 actor、條件、因果、狀態與否定。
保存後已重新核對文字與原輸出。這不宣稱正式 STE 合規。
P-class 原 native-review protocol 已更新為離線依賴的真實前提，並提交 Schema。
Schema 回 INCONCLUSIVE、六項行為觀察缺失；原 next 為 supply_behavior_evidence。
目前已消費原 native 拒絕並修正 producer；缺共享 Host 部署，尚不能提供審查角色觀察。
本次來源審查不替代獨立語義審查、guest 工具、恢復、Provider 或 Parent Goal 驗收。

## Revision 6：審查工具來源與原 Host 新 attempt

本節記錄本次新增來源，不改寫上方 revision 5 的結果。
目前 Session 已讀回 `openshell-review-tool-payload.md`、Soodles Code Intel、
原 Noodle commit lineage、Test Manager 結果及新 attempt 的原 Host／Loop 控制。
新增 Source 的保存副本與 repository bytes 相同；來源身分由原 Factory producer 產生。

| 卡片／關係 | 本次判定與判別反例 |
| --- | --- |
| SPEC-full-lifecycle-boundary，revision 6 | 接受來源支持的角色工具傳遞契約。普通指引保留原限制；工具沿原角色 producer、transfer、verifier 與 reader。若把工具綁成 Skill，或舊 Host 缺能力，交接必須拒絕。原進度 receipt 不得當成候選完成。 |
| V-full-lifecycle-discriminating-controls，revision 6 | 接受已保存的局部觀察。工具封存大於普通上限、凍結來源讀回、普通指引不變、漂移與 namespace 拒絕已有控制。中斷後有／無檔案差異均只產生進度；完成 reader 必須拒絕。 |
| 原 SPEC／REQ 與 SPEC／V 關係 | 方向與覆蓋保持不變。此修正補完整生命週期的來源、角色與恢復邊界，沒有新增 Parser 驗收或派發授權。 |
| 原 Parser Scope／PromptDelta | REUSE／NOOP。六張選定卡與十項原需求保持原義。新的來源知識不等於原 admission 已消費。 |

四個顯示槽位仍為 SPEC UPDATE、V UPDATE、UNUSED、UNUSED。
本次原 Factory validate、per-type inspect、coverage 與 NeoWeaver consistency 均通過其
結構條件。十項需求與 44 張 stable identity 未變。inspect 仍為
`SHAPE_VALID_SEMANTICS_UNVERIFIED`；獨立語義審查尚未執行。
原 Delta 保持 `BLOCKED`／`original_source_owner_readback_required`。
本次 Session 的 Source reconciliation 另存原始讀回，不把 Delta 改成 DONE。

原 Host 已有 interruption-inspect／new-attempt 原始實作，本次已整合並通過 Host race 控制。
目前運行中的 Host 尚未因本機提交而更新。合法新 attempt 的真實啟動、guest 品質工具、
UML IR／metrics 讀回與恢復驗收仍未通過。鎖定 UML Viewer 缺 Go LanguageGraph，
不得把 Python IR 加 Go metrics 寫成完整 Go 圖形覆蓋。

文字依原 Soodles `review-writing/features/ste-reference.md` 的 1.5–1.13、
3.6–3.7、第 4–6 節及 GR-3/GR-4 核對 actor、條件、因果、否定與狀態。
保存後再讀回，確認沒有把 prepared／queued／local tested 改成 native accepted。
這不宣稱正式 STE 合規。更新後的 P-class Schema 為 `INCONCLUSIVE`，
九項觀察缺失，原 next 是 `supply_behavior_evidence`。
本次已準備原角色可傳遞的依賴並整合原 Host 入口；實際 ub-review consumer 證據仍缺。

## Revision 7：Grok companion 與共用 Go 圖

本次來源為 `docs/specs/grok-shared-review.md`。目前 Session 對照已確認的
R1–R5／G1–G5、實際 Grok export、原 UML IR／mailbox、Go 分析、網頁觀察、
Code Intel 與 Schema readback。這是來源審查，不宣稱獨立 reviewer 驗收。

SPEC 更新保留 final-only、OpenShell、最小來源與原效果 owner。
V 更新分開記錄局部控制、一次 Grok 回覆、網頁展示與仍缺的原生閉環。
若把登入成功推成跨 Repo 審查通過，或把靜態圖推成 runtime trace，兩張卡都應拒絕該主張。
原 SPEC implements REQ 及 SPEC validated_by V 方向不變；缺少未知／拒絕控制，
就無法區分完整審查與只有來源展示。兩張卡在這個限定來源範圍接受更新。

四個槽位為 SPEC UPDATE、V UPDATE、UNUSED、UNUSED。
十項原需求、44 張 stable identity、Parser 六張選定卡及 PromptDelta NOOP 保持不變。
原 Delta 的 BLOCKED 仍保留；新增 Source 的 bytes reconciliation 另行保存。
Factory shape 不認證語義，獨立來源審查仍未執行。

新 protocol 的十欄 consumer_report 回 VALID／PASS。原 next
consume_verified_behavior 已由目前 Session 消費；沒有因此關閉舊九欄缺失 protocol。
沒有 guest、品質門檻、自動回送或恢復通過的主張。
文字沿原 STE reference 的 1.5–1.13、3.6–3.7、第 4–6 節與 GR-3／GR-4
核對術語、actor、條件、否定及狀態；未宣稱正式合規。

## Revision 8：原 Loop companion 與 session archive 讀回

本次來源為 `docs/specs/grok-outer-handoff.md`。目前 Session 讀取原 Loop review、
task role、原 supervisor archive、Grok 真實 stdout、兩個 Repo 的 Code Intel、
原 Test Manager 結果及 Schema readback。來源保存副本與 repository bytes 相同。

SPEC 接受原 candidate → Grok request → Session action → 原 review／role 的限定契約。
V 接受目前的局部控制、結構化原生 Grok 與四份指引的 consumer_report 觀察。
若把 Grok request 當 argv、缺指標當 no_change、raw artifact 當品質 PASS，或把局部
handoff fixture 當真實 Poteto 修正，均違反原來源，必須拒絕該完成主張。
SPEC implements REQ 與 SPEC validated_by V 的原方向及反例保持有效。
十項 REQ、44 張 stable identity 與原 Parser Scope／PromptDelta NOOP 保持不變。
四個槽位為 SPEC UPDATE、V UPDATE、UNUSED、UNUSED。

58 項 Soodles 控制與七項 Noodle 控制通過。新 archive Reader 只證明原始檔案的
來源與 bytes，不驗證工具正確性。Schema 對十二欄回 VALID／PASS，原 next 已消費；
唯讀 consumer 對原 CLI 的嘗試在 cache chmod 處遭拒，沒有因此取得 Host 狀態。
外層原 inspect 的 Host 不可用觀察另行保存。這不是獨立 reviewer 或 native product PASS。
Factory validate／per-type inspect／coverage／consistency 已執行；shape 仍不認證語義。
Delta 保持 BLOCKED，沒有將 Source reconciliation 改寫成工程完成。

後續唯讀發現 progress Host 正運行，但 effective_limit／start_credit 為 0，
且原 review-capabilities 不含 openshell_role_tool_payload。它不能直接取代原任務 Host。
實際資源與能力結果附於 grok-outer-handoff-evidence.json；未修改其他部署或共享 Swap。
guest 品質、原生 artifact 回讀、同 Host 恢復、policy 套用及四 Repo 閉環仍未完成。
文字按原 STE reference 的 1.5–1.13、3.6–3.7、第 4–6 節與 GR-3／GR-4 檢查，
保存後讀回，保留 actor、前置、否定、來源與狀態。未宣稱正式合規。

## 相容部署整合與 unchanged cleanup 修正

本輪 Source 為 docs/specs/openshell-compatible-deployment.md；SPEC/V 保留原身分並升至 revision 10。
原 owner 六筆 source 提交與本地最小修正分開保存。首次 runtime FAIL 保留，修正後聚焦 race controls
通過；published 與 unchanged、ProgressHead 與 candidate acceptance、離線能力與 running Host
維持獨立語義。Schema 只重用相同四份指引的 consumer_report，沒有新增原生效果 PASS。

目前 Session 核對來源、actor、否定、因果與退出／恢復條件，並讀回保存文字及原 Cards。
這是來源忠實審查，不宣稱獨立 semantic reviewer；原 shape 結果仍未驗證 semantics。
詳細 runtime、build、Source-bound Go 結構與原 Host 讀回見 compiled/openshell-compatible-deployment-evidence.json。
相容部署仍因原能力／資源條件未成立而未執行。Parent Goal 不因局部通過關閉。

## 新版 OpenShell 與 15 GB Host（revision 11）

原 7c18ec4b／a2e03b6d／7cda770b 與 StaticPreview 前置已整合到本任務來源。
Factory source 是 docs/specs/openshell-host15-integration.md。schema consumer_report 與
本機 build/race/UI controls 保持獨立；沒有以它們宣稱 guest／部署／恢復 PASS。
15 GB 的原資料是 Swap 使用量上限；RAM／Host 選擇仍待澄清。原 maintenance-plan 的
rolling/shared-quota 拒絕保留，沒有改入口或另一份 budget 繞過。
目前 Session 已核對來源、actor、條件、因果、失敗及恢復邊界，並讀回保存檔。
獨立語義審查保持 NOT_RUN，原 Parent Goal 仍未關閉。

## Rolling Host 與 15 GB Swap 本輪讀回

原來源合併為 ee774bf3，原 rolling 換版已讀回 active／ready，Swap 上限與共用 quota 保留。原 owner 身分、狀態與歷史未變；原序列化新增 39 個空 admission_refusal 欄位，故 JSON 形狀並非全等。真實 guest、Grok／Poteto 與恢復仍受原 gateway executable 缺失及原工作保留效果阻擋。兩張 lifecycle Cards 11→12；其餘 Cards／REQ 不變。Factory 原 validator、semantic shape、coverage、consistency 與新 lifecycle Reader 通過；Reader 為 source_bound_proposal、next=null、effects=[]，不授權 admission。Schema 重用範圍僅四份 bytes 未變的指引；Session 已消費原 next。來源忠實審查由目前 Session 完成，獨立語義 reviewer 保留 NOT_RUN。詳見 docs/compiled/openshell-rolling-host-integration-evidence.json。


## Revision 24：修正 Grok companion 的過度禁止

原 SPEC-full-lifecycle-boundary 的 forbidden 寫成「Do not start UML Viewer Grok」。
此前提把早期「不啟用預設 companion」擴成所有 Grok 交互均禁止。
`docs/specs/ub-review.md` 的展示邊界只禁止預設 Grok companion；後續已確認的
`docs/specs/grok-shared-review.md`「已確認的交互」明確要求本機 Grok CLI，
由 Outer 提供來源分析及必要片段。Grok 提出 policy、補證據、刷新及改碼請求，
Outer 核對來源與既有授權，原 Test Manager／Noodle／Poteto 承擔工程效果。
因此「所有 UML Viewer Grok 均不得啟動」不成立，也不能作為這條路徑的拒絕依據。

本次只修正原 SPEC 的 forbidden，revision 23→24。禁止自動啟用上游預設自主
Grok executor，並禁止 Grok 直接檢視或修改產品 Repo。已授權的提示詞 companion
請求保留由 Outer 與原 owners 處理。原 frozen Oracle、timeout／invalid mutants、
exit 0 不等於品質通過，以及必要功能／Formal 驗證的時機均保持原限制。
這項來源修正不授權現在啟動 companion，不重播 R3，不改原 request 或效果收據。

V 卡與其餘 43 張卡、十項原需求、原 Parser Scope／PromptDelta 均保留原值。
原 Factory producer 固定此修正來源，重跑結構、delta 與 Reader 讀回。
Delta 的 source reconciliation 與獨立語義審查仍未完成；Reader 只提供知識提案，
不提供 admission、可執行 next 或 Provider 效果。原 Grok／Poteto 閉環、guest 品質、
同 Host 恢復及 Parent Goal 的未完成義務不因本次修正改變。
