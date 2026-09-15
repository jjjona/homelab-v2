# Trade research workspace

## Purpose and boundary

Trade is a private, unfunded research project generated from Project Starter. Its first goal is to test the fixed BTC/EUR momentum and reversal hypotheses in the [research contract](https://hq.jnrm.eu/files/reports/automated-trading-2026-09-14/REPORT.md).

- Canonical repository: `https://git.jnrm.eu/jjjona/trade`.
- GitHub: private one-way mirror, managed by Forgejo.
- Workspace: `https://trade.jnrm.eu`, protected by the existing Tinyauth/PocketID route and Project Starter's exact identity/Host/Origin checks.
- Runtime: `workspace-trade` on workspace LXC 207, host port `46003` restricted to Traefik.
- Persistent project root: `/srv/workspaces/trade/repo`, presented as `/workspace` in the container.

This URL opens the project terminal. It is not a live trading service, public dashboard or claim of profitability. No exchange account, deposit or order is authorized. There is no automatic promotion to paper or live execution.

## Working on the project

Read the project's `AGENTS.md`, `README.md`, `BUILD.md` when present, and `docs/research/REPORT.md`. The project adopts the shared Agent Guide coding baseline, meaningful behavioral tests, reproducible dependencies, independent review and the existing Project Starter checks. Financial and data-quality claims need their own evidence; passing code checks does not establish profit.

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
