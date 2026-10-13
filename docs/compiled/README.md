# NeoWeaver source-grounded compilation

本次重新編譯使用已接受 FactoryWeaver main `a370c271ab6517298306e51c0f5a38c754bd71dd`。前一份 NeoWeaver spec revision `df41167de1d191d890db9bb94cfcc43663d027f7` 的十項 logical REQ 原文與別名均保留；它本來就是 PROPOSED，不是 native Registry acceptance。

## 可審查 artifacts

- [完整工程規格](../specs/learned-harness-coevolution.md)定義 actor、Goal、acceptance、三平面 I/O、policy eligibility、factorial comparison、frozen transfer 與逐步退出條件。
- [Source inventory](source-inventory.json)固定實際讀到的來源 bytes、versions 與 locators。Host 計算其 metadata；源文件真實性與執行效果仍須各自原證據。
- [Whole-source ledger](source-coverage-ledger.json)保留原 document sections、十项 REQ、selected contracts 與未讀 native inputs；顯示四張卡不截斷 inventory。
- [v1 record](specification.json)有十項 requirements、44 張 source-justified Cards；[per-type proposals](card-proposals.json)保存各類型完整語義欄位。
- [Taxonomy selection](taxonomy-selection.json)保留15種 registry，實際選14種。没有当前 unresolved source conflict，故不造X卡。P Practice不是Soodles P-class instruction。
- [Clause inventory](coverage.json)與原十項logicalREQ逐項對應。CLI只證明declared links，不能證明source exhaustiveness。沿用的JD-clause ID namespace是舊coverage CLI的格式要求，本source是工程spec而非職缺。
- [Scope selection](patch-scope-selection.json)與[四個semantic sidecars](semantic-sidecars.json)描述第一個純parser/refusal proposed atom，六張selected cards與全部44卡的applicability。其四個selected parent REQ僅覆蓋明列的parser clauses，其餘六項及selected REQ未覆蓋clauses均保留，沒有native admission或可執行next。
- [Verification](verification.json)是本次真實CLI結果摘要。原stdout/stderr/argv/captures保存在repository外，公開摘要不含private machine paths、consumer code或transcripts。
- [Proposed Patch schema](../../contracts/proposals/patch-proposal.schema.json)只驗證parsed object shape。Original Producer refs、mutation allowlist、duplicate-key parser與authorization不能靠該schema認證。

## 重跑本地契約

從上述exact accepted FactoryWeaver checkout使用原CLI，指定本NeoWeaver artifact路徑。

```text
python scripts/factoryweaver.py validate /path/to/NeoWeaver/docs/compiled/specification.json
python scripts/card_semantic.py inspect /path/to/NeoWeaver/docs/compiled/card-proposals.json
python scripts/requirement_coverage.py /path/to/NeoWeaver/docs/compiled/specification.json /path/to/NeoWeaver/docs/compiled/coverage.json
python scripts/card_delta.py /path/to/NeoWeaver/docs/compiled/specification.json /path/to/NeoWeaver/docs/compiled/specification.json --batch-size 4
python .cursor/skills/verify-factoryweaver/scripts/verify.py doctor
python .cursor/skills/verify-factoryweaver/scripts/verify.py maintain --scope local
python .cursor/skills/verify-factoryweaver/scripts/verify.py maintain
```

Host 選定Scope output後使用 `soodles_handoff.py RECORD SELECTION --output DESTINATION`；只消費該次返回的exact reader_arguments。不要把公開摘要中的digest或argv重建成新runtime command。

## 已觀察與未觀察

v1 validation、44-card per-type shape、十項declared clause links、same-record NOOP、four-slot lossless paging、stale-byte cursor refusal、forged TESTED refusal、wrong verification target refusal、Scope byte replay／conflict refusal與原Soodles Reader transport已實際執行。Paging 的空卡Before是本地fixture，只用來驗證分頁，不是假稱已有accepted Registry。

Local maintain 為 clean，只覆蓋12個CLI features。Full maintain為blocked，保留original source/native prerequisites。Reader回 `next=null`、`effects=[]`、`authorizes_landing=false`，Goal alignment仍UNVERIFIED。Original Issue/admission、Noodle execute、Test/Schema/Hook/Cron、fresh P-class consumer與native Codex transfer均NOT_RUN。Patch schema的positive/negative fixture不表示NeoWeaver parser已實作。

本輪DONE只指specification knowledge artifact交付；不表示Trainer、policy update、model-quality gain、native effects或parent Goal達成。前輪 ae739 artifact 曾取得 scoped source review ACCEPT，但後續逐卡審查發現 parser/replay boundary、V controls、typed-link readback 與 Scope applicability 仍有缺陷；該歷史 ACCEPT 不作本輪驗收。前輪 immutable verification bytes 保留，不改寫其中的 NOT_RUN／UNVERIFIED。此次結果另見 current verification.json。

## Parser Scope correction

本次從 prior compiled revision `ae739ac4514ab7fa23e4c2688d3dae600f972e98` 增量修正。原十項 REQ statement、falsifier、clause inventory 與44張stable identities保留；只對material變更增加revision。SPEC08只回ParsedProposal／DiagnosticRefusal，所有十張V重新分開oracle、固定正反input與expected result。完整lifecycle、replay、learning與native transfer不作parser exit。

`python scripts/check_compiled_contracts.py` 可重跑record／semantic proposals／typed edges／Scope／Continuation的declared consistency；使用`--before`指向prior artifact可另查原需求、coverage與revision保存。它只讀JSON並回報結構一致性，不是PatchProposal parser、semantic judge、native feedback或新CLI狀態機。原FactoryWeaverCLI仍處理v1 shape、delta／advisory invalidation與Bundle。實際語義審查與native證據分開記錄於verification；前輪verification原bytes保留於verification-before-parser-correction.json。

K43只對two-policies／learning-dataset形成必要依賴；K44只對plugin-transfer形成必要依賴。Parser不依賴這些native/training gaps。Material C/G changes經已聲明的typed edges作advisory invalidation；context-only卡不強造依賴。

## New source-level One-Shot card review (does not rewrite history)

[NeoWeaver 44-card / Behavior Scope Review](../reviews/one-shot-card-scope-review.md)
inspects every saved Card with its original applicability, recommends narrower
Roadmap references and Session-specific One-Shot composition, and explicitly
keeps compiled snapshots/old NOT_RUN states unchanged. The proposed R/SPEC/V/S
revisions require the original FactoryWeaver producer and fresh review to land;
this review does not itself create Registry revisions or native execution receipts.
