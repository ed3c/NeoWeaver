# NeoWeaver

第一個 implementation atom 是純 PatchProposal parser／refusal。Owner 提供固定 references，`neoweaver.patches.parse_proposal` 只回不可變資料或具名拒絕，不執行候選。

資料契約見 [parser contract](docs/parser-contract.md)，本輪實測與原生 Hook 觀察見 [parser verification](docs/parser-verification.json)。執行 `python3 -m unittest discover -s tests -v` 可重跑正反控制。程式只使用 Python standard library。

[A5 Paired Replay Readback](docs/replay-readback-contract.md) 目前只提供原 Runner observations 的 read-only structural comparability gate：匹配 task/environment/Solver/seed/budget/oracle，拒絕重用或缺少 run/sandbox/capture refs，unknown effect 保持 INCONCLUSIVE。它**不是** Snapshot Runner、獨立 Oracle、真實 sandbox 或 replay PASS。

[Hook purpose applicability](docs/hook-purpose-applicability.md)分開 task-review、PR／MR source check 與未來 native transfer，逐步核對推論與必要資料。

[Git Source Materialization](docs/source-materialization-contract.md) stages exact tracked Git blob bytes in two separate filesystem copies, without task execution or sandbox guarantees. Source staging is not native Replay, independent Oracle acceptance, training, or transfer.

[完整規格](docs/specs/learned-harness-coevolution.md)保留十項原需求與其後續驗收。Replay、training、learned artifact 的 native transfer 和 whole Goal 尚未驗收；歷史編譯證據保留原狀。
