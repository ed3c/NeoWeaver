# NeoWeaver 的 Hook 用途與來源 check

NeoWeaver 使用原 Soodles Hook Manager，沒有第二個 Manager。第一個 atom 的 parser 不啟動 Hook；工程續作與 learned native transfer 分開。

| 用途 | 時機與資料交接 | 必要資料與限制 |
| --- | --- | --- |
| Parser PR／MR source check | Exact candidate／diff／原 acceptance → `outer-review`／Waza `check` → findings validation | 需要精確 head、source、正反測試與必要 CI；不要求 Noodle Stage、Session、tokens 或 training／transfer receipts |
| 普通 task-review | 原 requirements／observations／FileRefs → `schema task-review` → 工程 next | 資料檢查不需要原生 Session metadata，也不證明 native 事件 |
| 專用任務的原生 Stop task-review | Actual Codex event → trusted Hook Manager → 原 task-review next → consumer | 保留真實 Session／cwd、固定需求與 `stop_hook_active`；一次續作和 exact next 消費另驗收 |
| 未來 learned Hook patch／transfer | 只有另行接受此 surface 的 scope 才進原 Host adapter | Capability、授權、trust、load、invoke、consume／effect各自驗收；首 parser atom 不依賴這些未來資料 |

`pull_request`／`merge_request` 是 provider 事件名稱，不能當成 Codex native Stop。若要聲稱 PR 事件自動啟動 check，需觀察 event → 已註冊 adapter → exact candidate request → reviewer capture → findings consumption。本輪沒有這個 bridge 的啟動證據；來源 review 可以在當前授權 Session 完成。

推論先在 Goal → 用途檢查。把 PR source review 填成 native `hook_need` 是 Producer 分類錯誤。其後每一步分開驗收：request 不代表 invocation；advisory UNKNOWN 不代表 native PASS；report／CI 不代表全部 acceptance；scoped ACCEPT 不代表 effect authority、merge、training 或 whole Goal closure。

Owner-fixed references 與 provider head 是來源 check 的必要身分。不能以排除 runtime metadata 為由移除它們。來源與 runtime 有各自的 proof scope：修改 native behavior 的候選仍需相應 native evidence，缺口只限制該 claim，不能卡住不依賴它的 parser source check。

本輪原 Soodles `outer-review` 在 NeoWeaver `17224a3fb9adacd477e742503795193cd4ba8f15` 的實際 diff、task／source FileRefs 下回 `pending_capture`／`check`，沒有輸入 Stage／Session／token 欄位。這證明來源請求不依賴這些欄位，沒有證明 native Waza invocation。新鮮 Codex Consumer 對四個用途案例的 12 個 boolean fields 經原 `schema pclass-feedback` 回報 VALID／PASS，Session 消費原 `consume_verified_behavior`；這僅支持 consumer_report 的分類結果。

此前原生 Stop 的兩次 event、bounded continuation、實際讀檔與撤除紀錄見 [parser verification](parser-verification.json)。它沒有安裝 learned artifact，也不支持 native transfer。選定 Soodles checkout 有 Hook Manager，不等於有 `knowledge inspect` Reader；實際 command catalog 缺 Reader 時保留 capability gap，不能改稱 metadata 缺失或阻擋來源 PR。

十項原需求、44 張卡、原 parser Scope 與歷史 compiled bytes 保留。Replay、training、learned transfer 與 whole Goal 的驗收繼續開放。

此用途分類的原 Producer 修正為 [FactoryWeaver PR #27](https://github.com/ed3c/factoryweaver/pull/27)，候選 commit 為 `cd8898bc7163d74288cf62cd0f78315e02904ba1`。它修改 Compile／Verify／v7.2 指引與既有驗證 feature，沒有新增 Manager、產品 CLI 狀態機或 MR event adapter；PR 尚未合併。
