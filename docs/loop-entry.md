# Repository Loop 入口

修改本入口與指引時，依 [狀態機修改契約套用](state-machine-change.md)。
獨立使用契約不需要這個執行入口。

`scripts/loop.py` 把已選定的語義 request 交給原 Soodles
`loop enter --request-file`。它只核對 request version 與本 repository 綁定，
再原樣傳遞檔案。原 CLI 驗證資料形狀、來源綁定與合法轉移，並回傳原 owner next。
語義判斷與實際效果仍需 Session 及原證據；CLI 不保證完整語義正確。

呼叫形式：

```text
python3 scripts/loop.py --soodles /path/to/installed/soodles --request-file /path/to/request.json
```

`--soodles` 省略時使用 PATH 中的 `soodles`。範例路徑是佔位值，
不證明該機器已安裝 CLI。啟動失敗會回傳具名錯誤；adapter 不安裝替代 runner。

Request 使用 `schema: 1`。`repository` 是此 worktree 的絕對路徑。
`mode` 使用 `outer-inner`、`inner-only` 或 `outer-only`。
`goal` 是原 caller 選定的完整任務。沒有 Issue authorization 的 inner 任務
另需 `selected_skill` 與 `model`；`outer-only` 不要求這兩欄。
`write_paths`、`acceptance`、`source_refs` 是字串陣列。
`source_refs` 指向原 CLI 要讀取的實際檔案。原 caller 明確指定 Host 模型。
`output` 是必填的 repository 外部絕對路徑。`outer-only` 與 `outer-inner`
需要原 Schema 的 `intent_selection`。`authorization` 選用原 Issue 路徑。
`noodle` 可指定已安裝的原生 binary。`knowledge_files` 是選用的唯讀展示資料。
`output` 是必填的 checkout 外絕對路徑。其餘欄位的有效性及所需條件由原 CLI 判定；adapter 不補造 identity、digest 或 receipt。

Adapter 不重選 mode、Skill、模型或測試，不建立 scheduler、重試或執行狀態。
原 CLI 的 stdout、stderr 與 exit code 直接保留。語義 request 不是執行成功證據；
native consumer、scope 驗收與 Provider readback 仍各自保留原結果。

`outer-only` 回傳投影，不自動執行 Thinking Method 或啟動 worker。
Request 必須綁定本 adapter 所屬 checkout；跨 repo 交接沿原 owner 的已支援入口。
