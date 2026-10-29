# 固定完整 Harness² 上游

NeoWeaver 以 `third_party/harness2` immutable vendor 保留 Google Harness² 的完整來源。
固定版本為 `1cfe254e8d25b15f37048c3730134686abe60335`。
原 LICENSE、CLI、core、substrate、benchmark、reflection、library 與 resume 均保留。
原 Git blob inventory 保存在 vendor 外的 `third_party/harness2.source.json`。
NeoWeaver 不在此 vendor 修改 prompts、channel 或演算法。
既有 source materializer 只接受一般 Git blob；gitlink 會阻擋原 Native driver。
完整 vendor 保留原檔案及 bytes，並沿用既有 materializer，不擴張其來源邊界。

完整來源必須可讀，因為後續接合需要檢查原 benchmark、CLI 與依賴條件。
只複製 solver 或安裝一個縮減 adapter 無法滿足這個要求。
訂閱 transport 與 NeoWeaver adapter 應在上游之外接合原公開 API。
原 CLI 的 benchmark 選單不會因外部 adapter 存在而自動增加 NeoWeaver。

## 本機安裝與原 demo

使用 Python 3.12 或 3.13。上游不支援 Python 3.14。
在 NeoWeaver checkout 執行：

```sh
python3.13 scripts/check_harness2_source.py
python3.13 -m venv .venv
.venv/bin/python -m pip install -r requirements-harness2.txt
.venv/bin/harness2-demo --output /absolute/external/demo-directory --mode both --k 2
```

以相同 output 再執行原 demo，會經原 schedule 讀取已保存狀態。
不同研究 domain、mode、substrate、seed 或 split 需保留各自身分。
不要將不同研究的狀態目錄混用。

## 證據與未完成範圍

`harness2-upstream-demo` workflow 使用原 CLI 和 deterministic demo。
它先核對完整 vendor 檔案清單及 Git blob bytes；這不認證來源語義或 Native 效果。
它沒有訂閱憑證，也不呼叫付費模型 API。
原 demo 可檢查原遞迴及 library 接線；它不是模型改善實驗。
實際 workflow 結果需讀回對應 commit 的 GitHub run。
設定 workflow 不表示該 run 已執行。

訂閱 Proposer、Selector、Executor、Judge 尚需各自原生證據。
NeoWeaver executable BenchmarkAdapter、可信本機 dispatcher、獨立 Oracle、
Promotion Safety、未見比較及新未凍結 Noodle Stage 的消費仍需後續實作與驗收。
LAB、JobBench、WorkBuddy 的原 grader、依賴與合法訂閱路徑需個別驗證。
Demo、內部 selection 或 source CI 不授權 Promotion，也不關閉十項 NeoWeaver REQ 或 A01–A20。
