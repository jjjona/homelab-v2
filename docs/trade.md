# Trade research workspace

## Purpose and boundary

Trade is a private, unfunded research project generated from Project Starter. Its first goal is to test the fixed BTC/EUR momentum and reversal hypotheses in the [research contract](https://hq.jnrm.eu/files/reports/automated-trading-2026-09-14/REPORT.md).

- Canonical repository: `https://git.jnrm.eu/jjjona/trade`.
- GitHub: private one-way mirror, managed by Forgejo.
- Workspace: `https://trade.jnrm.eu`, protected by the existing Tinyauth/PocketID route and Project Starter's exact identity/Host/Origin checks.
- Runtime: `workspace-trade` on workspace LXC 207, host port `46003` restricted to Traefik.
- Persistent project root: `/srv/workspaces/trade/repo`, presented as `/workspace` in the container.

This URL opens the project terminal. It is not a live trading service, public dashboard or claim of profitability. No exchange account, deposit or order is authorized. There is no automatic promotion to paper or live execution.

## Current research result

The bounded 2026-09-16 income batch completed **112 €100 native account attempts with €0 hosting**: 64 corrected accounts for M24/R24/ETHSHOCK and 48 for three new preregistered rules. All 24 primary paths lost money. Validation base results were M24 −€1.88, R24 −€3.78, ETHSHOCK −€1.46, relative strength −€5.21, relative reversal −€2.28 and volume breakout −€3.33. No larger-capital extension qualified; the current ceiling is €1,000. No curve was scaled, holdout opened or trading service deployed.

- [Reviewed income report, broader-market screen and evidence](https://hq.jnrm.eu/files/reports/trade-income-batch1-2026-09-16/REPORT.md).
- Trade report commit: `95a37193528777cd7ac4e5e05ef922b795e97331`; Forgejo push and GitHub mirror verified. Frozen source slices: `09f14022ad8eb954cf5ed357ad71336a470d297b` and `949c178`.
- Checks: 38 Python tests, 12 Bun tests/139 assertions, static/types/build checks and 38 actual native checks. Audits verified all 732 raw pages and 4,127 simulated trades across overlapping scenarios; these are not independent market observations. All 24 matched passive attempts were unexecuted. Data completeness, intragap risk, taxes and individual broker access remain unresolved.
- A conditional current cash offer illustrates €17.50/year on €1,000 after 30% withholding, before applicable fees—not a guaranteed payment or verified personal entitlement. Lower published crypto fees remain research leads, not tested winners. The bounded batch is finished without a deployment candidate.
- Authenticated preview and all 14 downloads passed; missing/wrong identity, Host and Origin were rejected; public unauthenticated access returned HTTP 401. Report SHA-256: `98de79a8688a4785a9c8e11442f09e73cc3a0b33f569aa84c6d9b3be65273f9f`.
- Encrypted HQ snapshot `59035f57ef3e51db2745e8a1092963da0e147fe312cc3c70ddf62e70d553272a` contains the byte-verified report. No workspace-wide manual pause backup ran; scheduled workspace coverage remains unchanged. Previous reports and failed evidence remain preserved.

### Earlier ETH experiment with allocated hosting

The separately registered 2026-09-16 ETH shock-reversal experiment also failed. All 40 €100 account attempts completed; all eight primary paths were rejected. In 2023–2024, the base/€1-month primary returned −€24.06. The unhalted trading component was −€1.22 after friction, before hosting. Only seven eligible signals occurred. This is additional development evidence, not a fresh final holdout or a claim about every short-term strategy.

- [Reviewed ETH result and evidence](https://hq.jnrm.eu/files/reports/trade-eth-shock-2026-09-16/REPORT.md).
- Trade source commit: `c3ceb0924f22c7d2f6d79d8275f1291f15f2e6c8` (Forgejo push and GitHub mirror verified).
- Verification: 36 named native checks; 19 Python tests; 12 Bun tests/139 assertions; static/types/build checks; independent source and result reviews. A separate numerical audit reconciled all 40 accounts and checked 135 active entries. No invalid fills or callback failures occurred.
- ETH raw completeness remains blocked: 27,738 missing five-minute intervals. All exposure-matched comparators were unavailable; primary uncertainty was inconclusive. No parameter retuning, new dependency/service, final-holdout access or trading authorization followed.
- Authenticated preview and all eight downloads passed; public unauthenticated access returned HTTP 401. Report SHA-256: `fdf69a489815f65c7c91cd4e869a28bd5ca6937aa8f45114a4bead26b2ef7766`. Encrypted HQ snapshot `057e27f4ab755d4e115d88b9c47e4dd37696225e5f15b3225ac45091567ab3e2` contains the byte-verified report. Workspace-wide manual backup was not run because it pauses all workspaces; scheduled coverage remains unchanged.

### Earlier BTC experiment

The 2026-09-15 study completed 72 separate €100 native account attempts. Neither fixed hypothesis qualified. For validation in 2023–2024, base friction and €1/month operating allocation produced economic losses of €23.51 for momentum and €24.79 for reversal. Unhalted diagnostics also lost money after trading friction, before operating costs. These are conditional historical results, not forecasts or personal-tax calculations.

- [Reviewed result and evidence](https://hq.jnrm.eu/files/reports/trade-eur100-2026-09-15/REPORT.md).
- Trade source commit: `084cac31e4075a8b250c84b621115cee419854d7`.
- Public-hook risk/non-execution integration passed 31 named native checks. Final checks also passed 16 Python tests and 12 Bun tests/139 assertions, plus formatting, lint, research-module types, shell, TypeScript and build checks.
- The 11,447 absent intervals remain uncertified. Raw completeness is still blocked; the tested grid policy does not invent executable prices. The native lookahead helper yielded no informative verdict, and all exposure-matched primary comparators were below the venue minimum.
- An independently found exposure-statistic timing error was corrected and all 72 trials rerun. Earlier inputs, results and source remain retained. No strategy, threshold, date or seed was retuned.
- The final holdout remains untouched. Larger-account runs and forward-paper execution were deferred in this earlier study. The current authorization caps capital at €1,000; no €10,000 trial is authorized. Do not promote these failed candidates or silently change their rules.

Published report SHA-256: `623a897187e70c8e5d1af3a9042f2d115cd72e8be34a6a6b3e6b462447193c8e`. Its authenticated preview and all nine downloads were verified; unauthenticated public requests remain HTTP 401. HQ backup snapshot `6f7df5fc8a2540d99b68157aff4b57908d55d3c240a2d215a3cc595eac79e48e` contains the byte-verified report. No manual workspace-wide backup was run: that existing job pauses all workspace containers and remains on its normal schedule.

## Working on the project

Read the project's `AGENTS.md`, `README.md`, current `reports/income-batch1-v1/REPORT.md`, `research/discovery-plan-20260916.md` and `research/discovery-clarifications-20260916.md`. Retain the earlier `reports/eth-shock-v1/REPORT.md` and `research/eth-shock-plan.md`, plus `reports/stage2-eur100-v2/REPORT.md`, `research/stage2-policy.json`, and original `docs/research/REPORT.md`. `BUILD.md` describes the earlier implementation slice. The project adopts the shared Agent Guide coding baseline, meaningful behavioral tests, reproducible dependencies, independent review and the existing Project Starter checks. Financial and data-quality claims need their own evidence; passing code checks does not establish profit.

Create or resume the workspace with the existing manager command:

```sh
hq-workspace create trade
```

The short hostname is recorded as `workspace_host` in `hq/projects.json`. The command regenerates its Compose configuration and Traefik route. Do not replace those with live-only edits.

Run every project build, dependency installation and research command inside the isolated project container. Never run project code in HQ or copy HQ's Age/management SSH identities into the workspace. The project has its own repository-scoped Git key. If Pi's seeded subscription login has expired, use Pi's native `/login` in the project terminal; do not copy HQ's auth store to repair it.

## State, recovery and reports

The existing workspace backup includes `/srv/workspaces/trade`: repository, uncommitted work, research state and Pi sessions. Committed source also survives through Forgejo and its GitHub mirror. Public market data should retain dataset hashes and retrieval provenance; never silently replace a dataset after inspecting performance.

To recover, restore workspace state when uncommitted work or research artifacts matter, then run `hq-workspace create trade`. Otherwise recreate the checkout from Forgejo and rerun the documented pinned setup and research commands. Restore files into a temporary location before overwriting current state.

Transfer only reviewed report artifacts through HQ to `/srv/hq-files/reports/`. Keep source reports. Do not grant project code management credentials for publishing.

Deferred: continuous forward simulation, application deployment, dashboards, paid data, runtime agents and all live trading. If a useful build later requires a persistent research process, declare its smallest runtime and durable state here before deployment.
