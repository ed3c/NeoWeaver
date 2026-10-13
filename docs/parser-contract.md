# 純 parser／refusal 資料契約

`neoweaver.patches.parse_proposal(raw: bytes, fixed_inputs: Mapping[str, object])`
只回傳 frozen `ParsedProposal` 或 `DiagnosticRefusal`。它不讀取 reference
指向的檔案、不執行 replacement，也不啟動 replay、training、native transfer
或 Provider effects。Parser 沒有 CLI 狀態機。

原 Owner 提供以下固定 mapping；所有 keys 都必須存在，額外 keys 會拒絕。
每個 reference 都是非空 `{"producer": str, "reference": str}`，逐欄精確比對。
Consumer 不把 reference 解讀為 path、URL、digest、權限或 runtime metadata。

| Key | 固定內容 |
| --- | --- |
| `snapshot_ref` | 原 TaskSnapshot reference |
| `failure_ref` | 原 FailureScope reference |
| `allowlist_ref` | 原 mutation allowlist reference |
| `acceptance_ref` | 原 immutable acceptance reference |
| `causal_target_ref` | FailureScope 已固定的單一因果 target |
| `allowlist` | 非空 list；每筆只有 `surface`, `target_ref`, `expected_source_ref` |
| `protected_target_refs` | 必填 list，列出原 Owner 的 protected evaluator／oracle 等 targets；可明示 `[]`，acceptance reference 仍自動受保護 |

Allowlist 的 `surface` 是 `skill_instruction`、`context_policy` 或 `mcp_wrapper`。
同一 `(surface, target_ref)` 重複宣告會得到 `ambiguous_allowlist`，不猜哪一筆
expected source 有效。Protected target 永遠優先於 allowlist。
Parser 不驗證上述 Owner 身分、source 真相、授權或 failure hypothesis；這些
仍由原上游 Owner 負責，也不要求 training rights 或 native metadata。

Raw proposal 的 shape 沿用
[原 PatchProposal schema](../contracts/proposals/patch-proposal.schema.json)。
四個固定 references 必須一致；change 的 target 必須同時符合所選 surface 的
allowlist 和 FailureScope causal target，expected source 必須精確等於固定值。
`replacement` 是非空的完整 replacement 文字。不同 targets 會得到
`multiple_causal_targets`；同 target 多個 replacement 會得到
`ambiguous_replacement_order`，因為現有 shape 沒有可裁決先後、offset 或組合的
operation 語義。即使文字相同也拒絕，不默默合併。

拒絕結果有 `condition` 和 `path`。驗證順序是 raw bytes 型別、固定 inputs、
UTF-8／JSON、proposal shape、固定 reference、change shape、單一 target、
protected target、allowlist、causal target、expected source、replacement 歧義。
因此一次只回第一個具名錯誤，不保證列出所有錯誤。

| Condition | 可區分的拒絕 |
| --- | --- |
| `invalid_raw_type`, `invalid_utf8`, `malformed_json` | 不是 bytes、非法 UTF-8 或 JSON |
| `duplicate_json_key`, `nonfinite_json_number`, `invalid_unicode_string` | 任意層 duplicate key、NaN／Infinity／數值溢位或 surrogate string |
| `invalid_fixed_input_type`, `missing_fixed_input`, `empty_fixed_input`, `extra_fixed_input` | 固定 mapping 或其欄位不完整、型別不符、必要值為空或多餘 |
| `invalid_type`, `missing_field`, `extra_field`, `empty_string`, `empty_changes` | Proposal shape 不符；credential／effect／argv 等多餘欄位同樣拒絕 |
| `unsupported_kind`, `unsupported_surface` | 不支援的版本或 surface |
| `fixed_reference_mismatch`, `stale_expected_source` | 固定 snapshot／failure／allowlist／acceptance 或 expected source 不符 |
| `protected_target`, `target_outside_allowlist`, `causal_target_mismatch` | Protected target、所選 surface 越界或不是固定因果 target |
| `multiple_causal_targets`, `ambiguous_replacement_order`, `ambiguous_allowlist` | 無法由既有資料契約裁決的候選或固定輸入 |

結果保留原 raw bytes；成功轉型的固定 mapping 以 frozen dataclasses／tuples
保存。若固定 input 本身拒絕，`fixed_inputs=None`，不把未通過型別檢查的
mutable data 偽裝成 fixed input。非 bytes 的 raw input 則 `raw=None`。
相同 bytes 與固定 data 可得到相等結果；這只是 parser determinism，並非
TaskSnapshot replay、Agent compliance、訓練成功或 whole Goal closure。

`python3 -m unittest discover -s tests -v` 執行 public API 的正反控制，包含三種
surface、原 references、duplicate keys、stale source、allowlist／protected／causal
target、缺失 input、effects 欄位、immutability 與無 file/process/network effects。
既有十項 REQ、44 張卡和 compiled 歷史證據不被改寫；其 native consumption、
replay、training 與 transfer 的 `NOT_RUN` 維持原本含義。
