# OpenShell 審查工具來源與原 Host 恢復範圍

本輪承接原生成品審查接線。使用者確認恢復先限原 Host 可讀回的中斷處理與合法新 attempt。
跨 Host 與損壞候選恢復保留缺口，不算通過。品質範圍包含本次 Soodles Python 與 Noodle Go
接線修改；匯入原 owner 的變更保留基線，整合影響仍需功能驗證。
OpenShell 內應產生可取回的 UML IR／metrics。Medium 網站與雙語文章仍是後續義務。

## 來源傳遞

普通 instruction 的每檔上限不足以攜帶 Linux Go／Java 封存。直接提高所有指引的上限
會改變一般 Poteto 成本。因此 Soodles 原角色 producer 接受明列的 `tool_sources`，
固定原來源並沿同一 materialization producer 產生 manifest v2 的 `tool_files`。
普通指引保持 v1 與原限制；角色未選工具時沒有工具傳輸。

工具的 namespace 是 `tools/`，binding kind 是 `tool`，不能充當 Skill 或一般 source。
角色工具上限是 32 檔、每檔 256 MiB、合計 512 MiB；普通指引仍是 4096 檔、
每檔 16 MiB、合計 64 MiB。原 transfer、Linux verifier 與完成 reader 核對同一份 bytes／mode。
來源與凍結副本漂移、錯誤 namespace／kind、超量與不相容版本會拒絕。

原候選 owner 在交接前核對 `openshell_role_tool_payload=1`。能力不足時不派發審查 control。
capability 與本機建置不證明 guest verifier 已部署。工具只有在原授權審查副本內執行；
一般 outer、Poteto 與共用 profile 沒有加入 ub-mode 或這些依賴。

## 本機觀察與原生缺口

角色 manifest、來源漂移、普通指引限制、工具 namespace 及舊 Host 拒絕已有正反控制。
Soodles 原 Test Manager 的 121 項控制通過；後續角色工具的四項選定控制亦通過。
後者保留兩次 fixture 修正歷史，不把這些 fixture 失敗當成原生模型行為。
原完成 reader 新增 supervisor receipt 來源核對；18 項完成讀回控制通過。
Noodle 原 instructionbundle、verifier 與 capability 控制通過，原建置完成。

審查專用 Linux ARM64 Python、Git、Go、Java、Clojure 與原品質工具已離線準備。
官方 Go／Temurin 封存摘要相符；選定 Go package 的離線 dependency discovery 通過。
這些是 Host 安裝／來源證據，guest 工具執行與品質達標仍未驗收。
鎖定 UML Viewer 的原 IR generator 支援 Python，但沒有 Go LanguageGraph。
Python IR 和 Go 品質 metrics 的覆蓋分開，Go 圖形缺口保留。

原 owner 已提交進度 supervisor、先保存再 Stop，以及原進度讀回。整合保留原 commit lineage，
並保留未變更候選的原 HEAD／unchanged publication。進度讀回不轉成成功候選。
原 Loop 已提供保存進度 inspection 與一次性新 attempt queue。原 Host CLI 以原 request、
configuration、binary 及 inspection version 核對授權，分別提供 interruption-inspect 與 new-attempt。
整合保留原能力與本次工具傳遞能力。Loop 控制及 Host race 控制通過，原建置完成。
這些本機控制不能證明目前舊 Host 已部署，也不能證明新 attempt 已啟動或真實恢復通過。
沒有跨 Host、損壞候選或 conversation resume 的完成主張。

最新原 Loop 唯讀仍拒絕完成讀回：原 dispatch 缺少完整成功候選證據。
既有 request、trace 及 receipt 保留，不改寫或重播。共享 Host 的部署與相容 profile／guest
supervisor／verifier 仍是原生驗收前提。其他聊天的進行中工作只讀，不被本次修改替代。

## 回饋與驗收

修改函式的 CRAP < 10、Dryer >= 0.8 候選、Mutator uncovered／surviving 仍按原政策處理。
誤報與等價變異需獨立證據。timeout、不能編譯、缺 coverage、部分掃描及工具失敗不能算 PASS。
原 Formal／Test Manager 驗證不因 ub-mode 延後而取消。

更新後的 P-class protocol 要求如實報告 Python／Go 範圍、品質、UML 與恢復邊界，
不預設品質通過或失敗。Schema 回 INCONCLUSIVE，九個觀察欄位缺失。
原 next 是 supply_behavior_evidence。初始 Poteto trace、unit test 與安裝摘要均不能代替 ub-review consumer。
Factory 只更新原 lifecycle SPEC／V，保留十項需求、44 張 stable identities 與原 Parser Scope。
Cards、來源審查、原生效果及 Parent Goal 各自驗收。
