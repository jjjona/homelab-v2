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

The 2026-09-15 study completed 72 independent €100 native backtests. Neither fixed hypothesis qualified. For validation in 2023–2024, base friction and €1/month operating allocation produced economic losses of €23.51 for momentum and €24.79 for reversal. Unhalted diagnostics also lost money after trading friction, before operating costs. These are conditional historical results, not forecasts or personal-tax calculations.

- [Reviewed result and evidence](https://hq.jnrm.eu/files/reports/trade-eur100-2026-09-15/REPORT.md).
- Trade source commit: `084cac31e4075a8b250c84b621115cee419854d7`.
- Public-hook risk/non-execution integration passed 31 named native checks. Final checks also passed 16 Python tests and 12 Bun tests/139 assertions, plus formatting, lint, research-module types, shell, TypeScript and build checks.
- The 11,447 absent intervals remain uncertified. Raw completeness is still blocked; the tested grid policy does not invent executable prices. The native lookahead helper yielded no informative verdict, and all exposure-matched primary comparators were below the venue minimum.
- An independently found exposure-statistic timing error was corrected and all 72 trials rerun. Earlier inputs, results and source remain retained. No strategy, threshold, date or seed was retuned.
- The final holdout remains untouched. €1,000/€10,000 account runs and forward-paper execution remain deferred. Do not promote these failed candidates or silently change their rules.

Published report SHA-256: `623a897187e70c8e5d1af3a9042f2d115cd72e8be34a6a6b3e6b462447193c8e`. Its authenticated preview and all nine downloads were verified; unauthenticated public requests remain HTTP 401. HQ backup snapshot `6f7df5fc8a2540d99b68157aff4b57908d55d3c240a2d215a3cc595eac79e48e` contains the byte-verified report. No manual workspace-wide backup was run: that existing job pauses all workspace containers and remains on its normal schedule.

## Working on the project

Read the project's `AGENTS.md`, `README.md`, current `reports/stage2-eur100-v2/REPORT.md`, `research/stage2-policy.json`, and original `docs/research/REPORT.md`. `BUILD.md` describes the earlier implementation slice. The project adopts the shared Agent Guide coding baseline, meaningful behavioral tests, reproducible dependencies, independent review and the existing Project Starter checks. Financial and data-quality claims need their own evidence; passing code checks does not establish profit.

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
