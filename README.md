# NeoWeaver

第一個 implementation atom 是純 PatchProposal parser／refusal。Owner 提供固定 references，`neoweaver.patches.parse_proposal` 只回不可變資料或具名拒絕，不執行候選。

資料契約見 [parser contract](docs/parser-contract.md)，本輪實測與原生 Hook 觀察見 [parser verification](docs/parser-verification.json)。執行 `python3 -m unittest discover -s tests -v` 可重跑正反控制。程式只使用 Python standard library。

[A5 Paired Replay Readback](docs/replay-readback-contract.md) 目前只提供原 Runner observations 的 read-only structural comparability gate：匹配 task/environment/Solver/seed/budget/oracle，拒絕重用或缺少 run/sandbox/capture refs，unknown effect 保持 INCONCLUSIVE。它**不是** Snapshot Runner、獨立 Oracle、真實 sandbox 或 replay PASS。

[Hook purpose applicability](docs/hook-purpose-applicability.md)分開 task-review、PR／MR source check 與未來 native transfer，逐步核對推論與必要資料。

[Bounded Docker Execution Transport](docs/container-execution-contract.md) executes an original Owner-selected digest-pinned command against a read-only staged source and records the Docker client result. Transport results do not establish native isolation, task completion, independent replay acceptance or training eligibility.

[Git Source Materialization](docs/source-materialization-contract.md) stages exact tracked Git blob bytes in two separate filesystem copies, without task execution or sandbox guarantees. Source staging is not native Replay, independent Oracle acceptance, training, or transfer.

[A6 Training Eligibility](docs/training-eligibility-contract.md) provides a pure, **non-authorizing** check of original Dataset Rights, train/validation/held-out partitions, policy/token lineage and independently declared verification/reward references. A structurally consistent declaration does not start a Trainer or prove real rights/reward data.

The same A6 contract now includes a **source-bound receipt reader** that checks original Host-selected file bytes/digests before relation matching; its output remains non-authenticating and non-authorizing.

[完整規格](docs/specs/learned-harness-coevolution.md)保留十項原需求與其後續驗收。Replay、training、learned artifact 的 native transfer 和 whole Goal 尚未驗收；歷史編譯證據保留原狀。
