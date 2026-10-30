# soodles-task-2db8482d62c660a6bbac candidate handoff

目標是原完整 NeoWeaver Goal 與實際 Owner 證據的增量對帳，再沿原 TaskAdapter
恢復／驗收／交付。此交回是程式候選與補驗材料；**acceptance_observed=false**。
沒有真實 task advance、Host 安裝、worker、Provider／merge／部署或訓練。

第一個來源斷點來自 admitted `product-independent-review-01.md`。
原 product_projection 固定空完成／阻塞，雖然避免 false PASS，仍不能隨 Owner
觀察更新。修正落在 NeoWeaver 的 read-only reconciliation producer 與共用
operation registry。原 `TaskAdapter`、`run_task_adapter.py`、`scripts/loop.py`
都未修改；沒有替換 Task Owner 或重寫原執行帳本。

已讀 local-task、poteto-mode、statechart、create-formal-verification-skill、
pele-render、cli-for-agents-source、control-cli。方法以 local-task 與本 admission
為準。未載入缺少的 pstack leaf skills，不聲稱其已使用，也未啟動新 worker。
先讀原兩組 CLI 與 compiled v1、product Goal、learning typed facts 之後才選資料形狀。

本項 checkpoint 如下。

- Blocking first steps：讀原契約、四項已接受決定與原實作；確認 Guest runtime。
- Independent workstreams：共用 schema／operations 與 transport code 相依，單 owner 順序實作。
- Shared mutable state：不新增 Goal 執行狀態；沿原 Owner，capture mkdir 只做已有 transport 的 reservation。
- Smallest safe decomposition：一個作者保存一致的語義邊界，透過獨立的 subprocess cases 與 fault mutants 準備驗證；未把自己審閱稱為獨立 Owner 驗收。

## 實際結果

[observations.json](observations.json) 保存 Node probe 的實際 commands、ENOENT、
退出結果與 source digests。原規格 10 REQ／44 Cards 的 Node inventory read 是
SOURCE_ONLY。原 goal/spec 的 digests 與 materialized source 相同。
Guest 找不到 python／python3、Java、TLC、Bun 或 mise。
Python compiler／AST、CLI、MCP、unit/subprocess/PTY controls、fault replay 全部 NOT_RUN。
沒有安裝替代 runtime 或用 Node source read 假稱 Python 編譯。

已實際用原 pele-render 的 Node 入口產生 [chart.svg](chart.svg)，renderer=Pele 1.9.0，
exit 0。圖是 authored projection，**不是 TLC 產圖**。原 [chart.mmd](chart.mmd) 保留。
Pele render 不提供模型或產品正確性證明。

## Root 補驗

在具 Python 3.10+ 的同候選 checkout，執行以下入口。

```sh
node docs/experiments/neo-product-cli-loop/control-cli-probe.mjs
```

它只編譯改動 Python、執行本項四組 controls 與原 TaskAdapter 回歸、CLI help／
stdio EOF smoke 及 scratch fault replays，將真實結果另存本項 observations。
實際 control-cli 方法的 PTY help、機器 stdin/stdout、SIGTERM 中斷與原讀回、
同 capture 並行／重送，位於 `tests/test_agent_cli_harness.py`。
CLI/MCP 正負例與 parity 位於 `tests/test_product_cli.py`、`tests/test_mcp_cli.py`。
新增測試中的 original-owner script 是 **synthetic test transport**，並非 Native Owner。
它確實經原 PinnedLoopCLI subprocess 與 TaskAdapter，仍不能升為真實 Owner receipts。

| 要求 | 補驗辨別 | Guest |
| --- | --- | --- |
| 正常／局部完成／新觀察增量 | 原 readback changes、local clause completed、10/44及完整 Goal 仍在 | NOT_RUN |
| 真實 Owner 阻塞／unknown | 原 typed result 與 next 保留；目前只有 synthetic controls | Native NOT_RUN |
| 缺證據／偽造頂層 PASS／Writer Completed | unknown／pending／pending_verification 分開 | NOT_RUN |
| 錯 Goal／Repo／source/acceptance drift | 來源或綁定具名拒絕 | NOT_RUN |
| 語義選擇／review | 返回原證據與 schema，無自動批准 | NOT_RUN |
| 機械多步／dry-run | 原 next 自動接至邊界；dry-run無capture/effect | NOT_RUN |
| 重送／並行 | CLI及stdio同capture只一個synthetic effect，重送unknown需原讀回 | NOT_RUN |
| 中斷／timeout | CLI及stdio中斷保留capture，refresh只inspect不重播 | NOT_RUN |
| 舊request/Frozen | 原request bytes不變；未接觸任何原真實request/Frozen | synthetic assertion NOT_RUN |
| 一致性 | 相同case共用schema、CLI JSON與MCP structuredContent相同，effects另比decision | NOT_RUN |
| Host安裝／實際call／fresh consumer與Schema | Root沿原合法入口分開讀回 | NOT_RUN |

同 request 不同 capture 的 effect 去重由原 Owner 決定，不主張此 wrapper 可替任意
外部 Owner 做 exactly-once。Guest 並未讀取 live archive，也未修該依賴。
Root 在原 archive／Host 能力恢復且授權有效時，先沿合法 inspect 取得真實 selection，
再驗收 `goal refresh` 與 dry-run；需真實 advance 時沿原 admission。本候選未授權或執行它。

## 模型、反例與 code replay

[ProductLoop.tla](ProductLoop.tla)／[config](ProductLoop.cfg)／[view](view.mjs)
綁定本項 admission。模型把每次原 Owner 結果視為一個觀察，涵蓋 admission、
局部 coverage、原 next、missing response、readback、scoped acceptance、delivery交Outer。
不變式分別禁止未准入 effect、改 Frozen request、unknown直接重播、局部關全Goal。

| 模型動作 | Code/control |
| --- | --- |
| NeedScope／SelectScope | product_goal.reconcile、coverage_schema／load_selection |
| ConsumeNext | product_cli.task_continue → 原 TaskAdapter.advance |
| Interrupt／ReadOriginal | 原 PinnedLoopCLI／TaskAdapter；goal_refresh，capture collision拒重送 |
| AcceptLocal／Deliver | product_goal.local_status；原 state/result/action 交回，whole_goal保持OPEN |
| FrozenPreserved | 所有產品入口只 `_read` 原 request，寫入僅 external capture |

故障 configs `ProductLoop-forged.cfg`、`ProductLoop-unknown.cfg`、
`ProductLoop-frozen.cfg` 各預期打破一個上述 invariant。它們尚未執行，沒有真實 TLC
counterexample，不能宣稱故障路徑已發現 bug。
Root 有已安裝 TLC/Java 時，沿已選 `/statechart` skill 讀模型，指定各 config、
本 view 及新的 out directory；不要把本手繪 mmd 當 checker output。
此 Guest 沒有呼叫會自動安裝 runtime 的入口。

[故障回放](fault_replay.py) 在 scratch copy 改三個對應 code 邊界，先驗 baseline，
再要求 discriminating real CLI tests 能失敗，最後回原檔重驗。
分別模擬局部關全Goal、capture重送直接effect、寫原request。
這些是故意故障變體，不是已觀察產品bug。目前 code replay NOT_RUN。
模型省略完整分散時序、Host／Provider內部驗收、鎖被外部刪除、path TOCTOU、任意外部
Owner 的去重／授權、排程公平性、performance與Whole Goal closure判定。
只隱藏終點self-loop。Model不提供真實authorizations或額外操作帳本。

## 來源與未完成義務

原來源使用 runtime materialization mapping。四項接受決定、MCP摘要、獨立審查、
archive邊界與canonical契約均唯讀。Repo套用契約解析至既有固定版本snapshot；
較新admitted canonical來源也已讀，不覆寫任一版本。
官方 MCP 2025-11-25 lifecycle／transports／tools 原文已透過唯讀 web 工具讀取，
連結在 [product-cli.md](../../product-cli.md)。
通用 Neo Route 留給 Outer 的 S worktree；本項只新增必要 AGENTS 入口引用。

完整 10REQ／44Cards、Factory/MRL、B、Harness²、四角色、文章、learning／native
transfer／Provider等義務仍在原source。即使 Root synthetic controls PASS，
仍需實際原 Owner continuation、Native獨立驗收、fresh consumer／Schema與delivery。
本項不將 partial Source candidate 寫成 whole Goal closed。
