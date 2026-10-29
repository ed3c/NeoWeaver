# 成品審查卡片來源與語義核對

本紀錄是目前 Session 對實際來源的審查，不是獨立 reviewer 或 native runtime receipt。
來源為使用者 U2–U6、F1 與實作確認，保存於 docs/specs/ub-review.md。
Soodles 的通用模型及 NeoWeaver profile、Noodle 選定技能與上游原文均已讀取。
原 Test Manager 與 Formal Lab 的責任保持不變。

- SPEC-full-lifecycle-boundary：ACCEPT，限來源支持的契約。新增成品審查前置、可選能力與回送責任，原 OpenShell 來源接線與未知條件仍保留。`then` 明示尚未觀察原生審查，不把安裝或技能解析稱為自動執行。
- V-full-lifecycle-discriminating-controls：ACCEPT，限判別設計與所列局部觀察。unfinished iteration、CRAP=10、Dryer exit0、mutation timeout、候選漂移及 unknown operation 各對應不同失敗邊界。四個 fresh consumer 的結果不代替 guest tools 或 Provider 效果。
- SPEC implements REQ-full-lifecycle：SUPPORTED。成品審查是既有生命週期的新增已接受條件，不縮小十項原 Requirement。
- SPEC validated_by V：SUPPORTED。V 檢查同一觸發、效果與恢復邊界；移除 V 後，不能由文件與工具安裝推導該行為已遵循。
- 現有 Parser Scope：REUSE。其六張選定卡片、十項父需求與其餘延後義務未改；成品審查不能侵入純 parser 的本機 exit。

原 Factory Validator 與 semantic inspect 分別證明 schema、欄位及連結形狀。
semantic inspect 的 SHAPE_VALID_SEMANTICS_UNVERIFIED 保留原值，不能以本審查回寫工具輸出。
Delta 回 BLOCKED／original_source_owner_readback_required，因新增來源。
目前 Session 已讀取來源文件與綁定 bytes，確認新 Source 對應本修訂；原 Delta 不被改成 DONE。
沒有新的執行 Scope／PromptDelta 派發需求，原 Parser sidecar 保持不變。

工程文字依 Soodles review-writing/features/ste-reference.md 的 1.5–1.13、3.6–3.7、
第4–6節與 GR-3/GR-4 審查 actor、前置、因果、否定、原效果權限及 unknown。
這是實用寫作審查，不宣稱正式 STE 合規。

本次公開局部證據見 docs/compiled/ub-review-evidence.json。
OpenShell 原生審查、自動角色交接、工具效果、Medium 成品與 Parent Goal 仍各自未完成。
