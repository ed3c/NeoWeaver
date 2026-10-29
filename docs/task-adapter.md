# 原任務可執行接合器

NeoWeaver 的 `TaskAdapter` 讓目前 Session 讀取已准入的原 Soodles／Noodle
任務，再消費一次原 continuation。接合器不建立任務、准入、排程器或新的
完成狀態來源。原 Owner 仍保存候選、審查、整合、驗收與未知效果。

資料形狀為 `TaskState`。`status` 分開 waiting、needs_review、integrated、
unknown、refused、failed；`owner_acceptance` 與原整合 `commit` 分開讀回。
integrated 不證明獨立驗收，原 source-bound Session PASS 也不自行證明驗收者
獨立。訂閱美元未知保持 null，`authorizes_landing` 保持 false。

## 在同一 Session 使用

原 Producer 返回的 request FileRef 與選定 carrier 設定放在私有 selection，
不提交 Repo、不上傳 Actions。carrier 沿用原 Python、entrypoint、完整 source
FileRefs、source_commit、environment、timeout_s 及 require_existing_instance。
這些 pins 檢查 bytes，不能證明真實性或建立執行權限。

selection 的 `request` 消費原 `{path, sha256}`，`carrier` 消費原已選設定。
先讀取原任務，capture 必須是 Repo 外不存在的新目錄。

```text
python scripts/run_task_adapter.py /absolute/private/selection.json inspect /absolute/external/capture-1
```

入口回傳原 readback 的 FileRef。要消費 continuation 時，將該 reference
原樣放在同一私有 selection 的 `readback` 欄位。

```text
python scripts/run_task_adapter.py /absolute/private/selection.json advance /absolute/external/capture-2
```

每次 advance 先重新 inspect。原 action／candidate 改變時拒絕沿用舊審查。
需要 Session 語義判斷且沒有 review 時，僅返回原 review_input。
Session 必須實際讀候選與獨立測試，再提供原格式 decision、feedback 和適用的
acceptance_review；接合器沒有預設 approve 或 PASS。

```text
python scripts/run_task_adapter.py /absolute/private/selection.json advance /absolute/external/capture-3 --review /absolute/private/actual-review.json
```

request-changes 交原 revision 路徑。候選審查後的 integrated acceptance
仍由原 Owner 消費實際 observation。原 delivery／retirement 結果與 next
保留在 result，不合併成產品成功。

## 等待與拒絕

未識別的工具或 argv 不執行。原 enter 必須帶選定 existing-instance guard。
接合器不建立另一個 Host，不繞過原資源政策。timeout、無法解析的回應或
呼叫後來源漂移均返回 unknown。unknown 之後的 advance 只 inspect；
不在同次呼叫重送作用。原 Owner 讀回仍是後續恢復的依據。

原 Harness² core 會把一般 execute 例外記成失敗 rollout。此 API 因此在 core
外讓 Session 處理原任務，不用 PendingError 假裝核心可暫停續跑。它不是
完整 BenchmarkAdapter，也不把完成結果投影冒充實際執行。
完整動態 Harness² 接合、四角色訂閱、流程比較與完整 handoff 義務仍保留。

## 驗收邊界

測試中的 fake carrier 只驗證無自動 approve、一次原 next、來源／candidate
漂移拒絕、unknown 後讀回及 named CLI transport。A 完成仍需真實程式任務的
launch、實際 diff、原 candidate／review、獨立 Test／Oracle、原驗收與提交讀回。
原 Migration-RL 文件 request 不提供這項證據，文件或 fixture PASS 不關閉 A。
