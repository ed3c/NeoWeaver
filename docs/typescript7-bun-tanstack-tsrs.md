# External JS/TS environment consumer profile

This Harness/spec consumer repository has no TypeScript frontend package or TanStack app at its inspected main revision. It should not claim that installing nothing updated a runtime. The goal is to consume a reviewed environment contract **only when** its real task selects a JS/TS application.

The user-selected stack combines [Microsoft TypeScript 7.0 Stable](https://devblogs.microsoft.com/typescript/announcing-typescript-7-0/) (Go-native stable CLI), [Bun](https://bun.com/docs/runtime/check) (secondary runtime and TS7 checker), [TanStack Start](https://tanstack.com/start/latest/docs/framework/react/guide/hosting) (React full-stack target when such an app exists), and [tsrs](https://github.com/oxc-project/tsrs) (Rust compiler port tracking TypeScript 7.1-dev, not a TS7.0-stable oracle).

**Existing real Consumers:**
- [Noodle PR #122](https://github.com/ed3c/noodle/pull/122) — original Go Host and React/TanStack Router UI, official TypeScript 7 native CLI; Bun secondary verification; *not* TanStack Start.
- [medium-compiler PR #72](https://github.com/ed3c/medium-compiler/pull/72) — original Python site generator and isolated TanStack Start preview; TypeScript 7/6 JS API bridge, Bun and isolated tsrs WASM.
- [Soodles migrate-class PR #444](https://github.com/ed3c/soodles/pull/444) — the original source-bound migration method, not a new runtime scheduler.

**Selection rules:** Only the original Session/Task may select a new actual frontend Consumer. First AST/code-intel on source+target, pin source and package versions, then copy original modules/codemod/adapt minimally, measure source→target observable parity (outputs, errors, effects) and original Test Manager results. TypeScript 7's Go CLI does **not** expose the prior JavaScript Compiler API; retain TS6 API compatibility only when source calls it. tsrs 7.1-dev diagnostic comparison against TS7.0 stable cannot establish matching-revision parity. Cloudflare Workers hosting is not automatically Bun Server hosting.

No package.json, fake tsconfig, Bun lockfile, npm downloads, Native Task/Provider effects, Production deployment or PR merge in this source-only proposal. Native acceptance remains NOT_RUN. The original Python and card/knowledge producers retain authority. Do not turn this design into a mandatory new P-class gate.
