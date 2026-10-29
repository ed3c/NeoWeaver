# NeoWeaver 成品審查：已接受的修訂

使用者確認將 ub-mode 與依賴放入 Noodle 可切換 skills set，只用於成品審查。
此決策取代先前 Soodles outer 跨 route 共用 ub-mode 的草案。
原十項 Requirement、44 張 Card、第一個 H0／H1 切片與全部 Parent Goal 保留。

## 生命週期

Poteto 完成原 task 當前交付範圍，原必要功能驗收通過，候選待接受時，
目前 Session 才沿原候選入口選用 ub-review。一般 outer、實作和修正迭代
不載入 ub-mode，不初始化、執行或等待它新增的工具。
原必要 Formal／Test Manager 驗證仍照常進行；最後審查優先沿用適用證據。
審查者提出 findings，產品修正回 Poteto；新候選形成後只重審受影響部分。
不同角色沿原 admission 使用獨立上下文，不覆寫 frozen inputs。

## 品質與驗收

品質範圍為本次修改函式與相關重複片段，既有問題保留基線。
修改函式 CRAP 必須 < 10；Dryer >= 0.8 候選與 Mutator 未覆蓋／存活變異須處理。
獨立來源或行為證據能證明誤報或等價變異時可排除，但保留原始結果與理由。
無法證明、timeout、不能編譯、缺工具、部分掃描與執行失敗不算通過。
工具彙總分數不證明行為正確，不得為分數改動 frozen Oracle。

Formal 方法幫助 Session 判別獨立需求、Oracle、反例與替代覆蓋；不固定跑 solver。
原 Test Manager 選必要控制；target 的原 runner 執行，Schema 保存原證據與 next。
工具預設測試與並行不能繞過原 scope 或 Host 資源限制。
變異與 coverage 寫入限定在授權隔離副本及結果區，不能直接改受審 candidate。
原驗收與 Provider 保留接受、發布及整合責任。

NeoWeaver 固定 Noodle OpenShell。套件安裝、Host resolver 可讀、guest 載入、
工具執行、結果取回與恢復是不同驗收。沒有原生讀回的部分保持 NOT_RUN，
不得以 process 補驗收。未知效果先原 readback，不重播；候選漂移保留舊結果為歷史。

## 知識與展示

Factory 沿原 lifecycle SPEC／V 更新此修訂，保留穩定身分與歷史。
Code Intel 僅支持選定來源結構；來源存在不證明已部署或原生審查通過。
真正架構矛盾回 Thinking／More；機械缺件回原 producer，不能每次重跑所有 routes。
Medium 第一版只展示候選依賴圖、品質結果、來源、前後差異及排除，支援篩選與鑽取。
不從圖上派發修改，不啟用 UML Viewer 預設 Grok companion。
工具自有範例的 IR 只證明安裝能力，不能當 NeoWeaver runtime 視覺化成品。
雙語文章、網站、H0／H1 改善與 Parent Goal 仍依各自原驗收成立。

本文件記錄需求及設計，不是原生審查收據。當前局部證據另見
[成品審查證據](../compiled/ub-review-evidence.json)。歷史 verification 不回寫。
