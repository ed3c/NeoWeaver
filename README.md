# NeoWeaver

第一個 implementation atom 是純 PatchProposal parser／refusal。Owner 提供固定 references，`neoweaver.patches.parse_proposal` 只回不可變資料或具名拒絕，不執行候選。

資料契約見 [parser contract](docs/parser-contract.md)，本輪實測與原生 Hook 觀察見 [parser verification](docs/parser-verification.json)。執行 `python3 -m unittest discover -s tests -v` 可重跑正反控制。程式只使用 Python standard library。

[完整規格](docs/specs/learned-harness-coevolution.md)保留十項原需求與其後續驗收。Replay、training、learned artifact 的 native transfer 和 whole Goal 尚未驗收；歷史編譯證據保留原狀。
