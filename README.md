# NeoWeaver

[完整 Harness² 上游](docs/harness2-upstream.md) 以保留原 bytes 的固定 vendor 保留。
原 credential-free demo 與 CLI 有獨立 workflow；訂閱模型接合及 Promotion 尚待實作與原生驗收。

第一個 implementation atom 是純 PatchProposal parser／refusal。Owner 提供固定 references，`neoweaver.patches.parse_proposal` 只回不可變資料或具名拒絕，不執行候選。

資料契約見 [parser contract](docs/parser-contract.md)，本輪實測與原生 Hook 觀察見 [parser verification](docs/parser-verification.json)。執行 `python3 -m unittest discover -s tests -v` 可重跑正反控制。程式只使用 Python standard library。

[A5 Paired Replay Readback](docs/replay-readback-contract.md) 目前只提供原 Runner observations 的 read-only structural comparability gate：匹配 task/environment/Solver/seed/budget/oracle，拒絕重用或缺少 run/sandbox/capture refs，unknown effect 保持 INCONCLUSIVE。它**不是** Snapshot Runner、獨立 Oracle、真實 sandbox 或 replay PASS。

[Native capture and fixed Oracle](docs/native-replay-contract.md) 現在提供 `run_native_arm` 與 `inspect_native_pair`，將實際 Codex 完成事件、固定 parser-response Oracle 和原 pair API 接通。每個 capture 保留自己的 launch selection，明列 task/model/schema/budget/source 差異。缺少 sandbox／effect 證據時，兩個 scoped match 仍只得到 pair INCONCLUSIVE。這是 validation-only H0/H0 接線範圍；逐 REQ 進度與未完成證據見 native contract。

[Hook purpose applicability](docs/hook-purpose-applicability.md)分開 task-review、PR／MR source check 與未來 native transfer，逐步核對推論與必要資料。

[Bounded Docker Execution Transport](docs/container-execution-contract.md) executes an original Owner-selected digest-pinned command against a read-only staged source and records the Docker client result. Transport results do not establish native isolation, task completion, independent replay acceptance or training eligibility.

[Git Source Materialization](docs/source-materialization-contract.md) stages exact tracked Git blob bytes in two separate filesystem copies. [Candidate treatment](docs/candidate-treatment-contract.md) consumes a parsed single-target proposal and an original caller-fixed source binding, preserves H0, and records only the permitted H1 replacement. Existing transport and inspection check both fixed arm manifests before using the selected arm. These source and mocked transport controls do not establish native Replay, independent Oracle acceptance, training, or transfer.

[A6 Training Eligibility](docs/training-eligibility-contract.md) accepts direct typed task/evaluation facts and checks partition, rights, token lineage and hard gates. The unused A6 FileRef / Provider Authenticity layers have been removed. This screening does not start a Trainer, verify model data or authorize a policy update.

[完整規格](docs/specs/learned-harness-coevolution.md)保留十項原需求與其後續驗收。Replay、training、learned artifact 的 native transfer 和 whole Goal 尚未驗收；歷史編譯證據保留原狀。
