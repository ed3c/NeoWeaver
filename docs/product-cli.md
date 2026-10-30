# Product CLI candidate

此候選提供 Goal 對帳、Owner refresh、原 task continuation 與 A6 typed-fact screen。
唯一業務實作是 `neoweaver/product_cli.py` 的 `OPERATIONS`；CLI 與 MCP 使用同一
schema、validator 與 handler。Guest 缺 Python，編譯、CLI、MCP 及 subprocess
controls 均為 **NOT_RUN**。這份候選尚未取得可用性或 Native 驗收。
實際記錄與 Root 補驗入口見 [本項產物](experiments/neo-product-cli-loop/README.md)。

```sh
python3 scripts/neoweaver.py --help
python3 scripts/neoweaver.py schema
python3 scripts/neoweaver.py goal reconcile --input arguments.json
cat arguments.json | python3 scripts/neoweaver.py goal refresh --stdin
cat arguments.json | python3 scripts/neoweaver.py task continue --stdin --dry-run
cat arguments.json | python3 scripts/neoweaver.py task continue --stdin
cat arguments.json | python3 scripts/neoweaver.py training inspect --stdin
```

每個 operation 的 arguments 以 `schema` 的 `inputSchema` 為準，JSON 檔案與
stdin 使用原 TaskAdapter 的 duplicate-key／nonfinite 拒絕 parser。
業務拒絕、失敗與 unknown 為 exit 2、stderr JSON；needs_input 是正常機械結果，
exit 0、stdout JSON。`schema` 和 `--help` 不呼叫原 Owner。
沒有互動選單或隱含模型。未選擇 input 時立即給具名錯誤與 example。

## 通用資料與責任

`selection` 是 Session 選擇的來源集合，不是新的執行帳本。必要欄位如下。

| 欄位 | 來源與用途 |
| --- | --- |
| `profile` | Session 明選 `generic` 或 `neoweaver` |
| `repository` | Session 明選成品 checkout 的 absolute canonical path，不能由 task 推導 |
| `goal` | 原 Producer 的 `{path, sha256}`，保留完整成品 Goal bytes |
| `requirements` | 原 Producer 的 reference，內容有非空 `requirements` 陣列及唯一 `id` |
| `tasks` | Session 選定的具名原 tasks；每項含原 `request` reference，以及可用的 `readback`／`carrier` |
| `coverage` | Session 選擇的局部 `requirement`、`clause`、`task` 與 `relation`。省略表示尚待語義選擇，空陣列表示明選目前無適用局部映射 |
| `sources` | 可選的原完整來源 references，逐份保留原文，不生成新 evidence identities |
| `baseline` | 可選的前次原 Owner readback references，只用於差異比較，不授權 effect |

`generic` 不限定 REQ 或 Card 數量。目前可執行 task Owner 限於原 TaskAdapter
已支援的 Soodles 操作，沒有任意 shell／argv 或通用 Owner dispatcher。
Goal 與 requirement source 必須屬選定的 product repository。
`relation=product` 的 task repository 必須相同；跨 Repo 依賴只能明選
`dependency`，其局部完成另列，不能算成品局部完成。

沒有 `coverage` 時，`needs_input.name=goal_coverage` 返回原 Goal、完整
requirements、Owner states、原 next，以及包含實際 requirement/task choices 的
`input_schema`。Session 只判斷局部 clause 的適用性，無須重算 hash、ID 或 argv。
CLI 核對形狀、原引用與 repository；不認證該語義選擇正確。

## NeoWeaver profile

`neoweaver` profile 固定選定 checkout 內原有的
`docs/specs/neoweaver-product-program.md` 與 `docs/compiled/specification.json`。
它核對原 10 requirements／44 Cards，並回傳完整 record，沒有以 task 狀態改卡片。
全 Goal 原文保留 Factory／MRL／B／Harness²／四角色／文章及後續義務。
更詳細的原工程規格、source coverage 與 LESSON 仍沿原文件及可選 `sources` 保留。
通用 CLI 方法不繼承這些固定數量。

對帳以原 `TaskAdapter.readback` 解析 actual Owner response。局部狀態如下。

| 原觀察 | 輸出 |
| --- | --- |
| locally_integrated + integrated acceptance PASS + 可讀原 record/head | `locally_completed`，僅限 Session 所選局部 clause，證據上限是 Owner readback |
| integrated 或 Writer completed，缺 integrated acceptance | `pending_verification` |
| 原 blocked／needs_scope／refused／failed | `blocked`，保留原 result 與 next |
| 原 unknown 或沒有 readback | `unknown` 與具名原讀回需求 |
| 原 review_input／session_judgment | `needs_input`，保留原候選與 review schema |
| 只有頂層 PASS／ACTIVE 或其餘進行中觀察 | `pending`，不能推成完成 |

`remaining_requirements` 永遠保留完整原 requirements；`uncovered_requirements`
列出目前未有局部映射者。局部映射不刪除 parent clauses。
`whole_goal=OPEN` 是此局部投影的權限上限，此入口沒有 whole-Goal closure 操作。
Owner 的 PASS、讀回檔 hash 或 test fixture 不證明獨立性、真實性或 Native effect。
A6 沿原 `inspect_training_candidate` 與 typed facts，不新增 authenticity／FileRef pipeline，
輸出始終不授權 training。

## 恢復、驗收與交付

`goal refresh` 要求原選定 carrier 及 fresh external `capture` directory。
它只呼叫原 inspect，再對帳新的 Owner 觀察。回傳 `selection` 已帶原 adapter
產生的 readback references，並自動以先前 readbacks 比較 `changes`。
Session 可沿此返回資料續行，不重建 references。

`task continue` 需明選 task、原 readback 與 carrier、fresh external capture。
Carrier 完整沿 [原接合器](task-adapter.md) 的 pins、timeout、environment、existing
instance guard。`--dry-run` 只讀原 references／next，不建 capture、不呼叫 carrier。
真正 continuation 直接使用原 `TaskAdapter.advance`，每步先 inspect，拒絕舊候選／
request／source 漂移。原 review 由 Session 提供，沒有預設 approve／PASS。

同一次 call 在已變更且機械確定的 next 間自動接續，直到原 review、unknown、
blocked、相同 continuation／inspect wait、原其他 boundary，或有界 `max_steps`
（預設 16，最多 64）。同一 action 不因工具回應成功而反覆重送。
原 Owner 的 delivery、retirement 或 acceptance 結果原樣保留；此工具不創建它們。

Capture 使用 atomic mkdir 排除同 capture 的並行／重送。
既有 capture 只回 `unknown/capture_exists_read_original_owner`，要求 fresh capture
經 `goal refresh` 讀回，絕不把目錄存在當成功或再次寫入。
這是 capture reservation，不是第二份 operation ledger，也不是跨任意外部 effect 的
exactly-once。不同 capture 的相同 request 去重仍由原 Owner 負責。
中斷後不能僅換 capture 直接重做 continuation；先 refresh。
未知 transport 結果不回傳可用的舊 readback 作新 continuation。
完整原 request、Frozen 與驗收資料始終由原 Owner 保有。
原 archive 能力不足時只停止依賴它的 effect；offline 對帳與拒絕可獨立使用。

## 薄 MCP stdio

```sh
python3 scripts/neoweaver.py mcp
```

僅接 initialize／initialized notification／ping／tools/list／tools/call。
具名工具 `goal_reconcile`、`goal_refresh`、`task_continue`、`training_inspect`
從同一 registry 列出並直接執行相同 handler；沒有另外的業務 dispatcher。
每行一個 UTF-8 JSON-RPC，stdout 僅有協定訊息，診斷到 stderr。
依官方 [2025-11-25 lifecycle](https://modelcontextprotocol.io/specification/2025-11-25/basic/lifecycle)、
[stdio transport](https://modelcontextprotocol.io/specification/2025-11-25/basic/transports) 與
[tools](https://modelcontextprotocol.io/specification/2025-11-25/server/tools) 處理初始化、通知及錯誤。
未知 tool 為 protocol error；已知 tool 的業務拒絕使用 `isError` 和同一 structuredContent。
不支援 HTTP、background tasks 或外部 shell。

[project-local 設定例子](../examples/agent-cli-mcp.json) 需從選定 checkout root 啟動。
若 Host 的 cwd 不同，由 Root 將 script argument 換成明選的 absolute project path。
這是可攜例子，沒有修改全域設定或啟新 Host。
Source 已存在、stdio probe 可通、Host 已安裝、實際 Host tools/list/call、fresh Agent
遵循與 Native effect 是各別驗收；本 Guest 沒有執行後五項。
