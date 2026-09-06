# Opportunity Miner operations

## Purpose and boundaries

`https://opportunities.jnrm.eu` provides private, read-only procurement reports. The backend fetches recent Belgian-buyer TED notices, retains source data, extracts evidence, and tests possible spending patterns with Pi/Codex. It proposes experiments but never performs outreach, spends money on experiments, or publishes reports publicly.

The application extends Project Starter. Its inherited development terminal remains separate from the production report process.

- Canonical repository: `https://git.jnrm.eu/jjjona/opportunities`
- Development workspace: `https://opportunities-code.jnrm.eu`
- Production host: Laptop 1, `192.168.0.165`
- Container: `opportunities`
- Private route: Cloudflare Tunnel → Traefik authenticated `web` entrypoint → `192.168.0.165:4715`
- Deployment: `ansible/playbooks/22-opportunities.yml`

The backend requires the exact public Host and the configured `Remote-Email` identity. Host firewall rules admit new connections to port 4715 only from Traefik at `192.168.0.159`. The health endpoint contains no report data. Do not expose the backend port directly or route it through `web-noauth`.

## Verified deployment — 2026-09-06

- Application revision: `591773fe855057090a59ceffedab859f408f0f31`.
- Clean install and application checks passed; 35 tests pass, including the inherited Starter checks.
- Production completed a live TED run: 20 notices, 25 evidence records, zero stage failures. No supported pattern or hypothesis was produced.
- All 25 production evidence records passed provenance validation; SQLite integrity and foreign keys passed. Five source notices were also inspected manually during the development audit (`docs/live-verification.md` in the application repository).
- Repeating the production pipeline and restarting its container did not duplicate evidence or model calls.
- The authenticated viewer returns reports with clickable TED sources. Unauthenticated and forged-identity public requests return HTTP 401; direct HQ-to-backend connections are blocked.
- First production run: 20 subscription model calls; EUR 0.041115 estimated API-equivalent usage, not a cash invoice.
- Daily backup inclusion is installed. An initial production Restic snapshot has not been verified; the existing backup schedule runs at 04:00 UTC.

## Daily operation

One Bun process serves reports and runs the full pipeline daily at **06:00 UTC** (`MINER_UTC_HOUR=6`). Startup catches up when today's run has not completed. Failed runs remain visible and retry without duplicating evidence or completed analysis.

The application uses the existing ChatGPT/Codex subscription through native Pi. Authentication lives outside the source tree in `/opt/opportunities/pi`, mounted at `/home/bun/.pi/agent`. Pi manages refreshes. Deployment seeds this directory only when authentication is absent; it does not overwrite an existing login.

`DAILY_LLM_BUDGET_EUR=1.00` controls pre-request estimated API-equivalent usage. This is not a per-call subscription invoice. Keep reported token usage and estimates separate from recorded cash costs. Read the application README for provider limit details. Authentication or subscription-limit failures appear as failed runs; they do not trigger a paid API fallback.

## Deploy a verified revision

First run the application checks in its isolated workspace, including its live source audit. Never execute application tests or build scripts in HQ.

From the homelab repository:

```sh
./scripts/preflight.sh
git status --short
cd ansible
export SOPS_AGE_KEY_FILE="$HOME/.config/sops/age/keys.txt"
REVISION=<tested-40-character-Forgejo-commit>
ansible-playbook playbooks/22-opportunities.yml --syntax-check
ansible-playbook playbooks/22-opportunities.yml --check -e opportunities_revision="$REVISION"
ansible-playbook playbooks/22-opportunities.yml -e opportunities_revision="$REVISION"
ansible-playbook playbooks/11-laptops.yml --limit laptop1 --tags opportunities_backup
```

The playbook downloads the immutable source archive from Forgejo, builds a revision-tagged image on Laptop 1, and installs a small Compose manifest. It does not give the running application a Git administration token, management SSH key, Age key, or Docker socket. The existing Cloudflare wildcard ingress and Traefik file watcher require no proxy restart.

## Inspect and rerun

```sh
ssh -T -o RemoteCommand=none root@192.168.0.165 \
  'docker inspect --format "{{.State.Status}} {{.RestartCount}}" opportunities'

ssh -T -o RemoteCommand=none root@192.168.0.165 \
  'docker exec opportunities bun run miner run'
```

The CLI uses the same run lock as the scheduler. If a run is active, wait for it rather than deleting its lock. `bun run miner report` regenerates Markdown from SQLite without network or model calls. Other stage commands are documented in the application README.

Do not print the Compose environment, Pi authentication store, or raw container inspection output. Inspect only explicit non-secret fields.

## Durable state and recovery

| Host path | Contents |
|---|---|
| `/opt/opportunities/data` | SQLite database, retained raw TED notices, pipeline state |
| `/opt/opportunities/reports` | Daily Markdown reports |
| `/opt/opportunities/pi` | Existing native Pi authentication and refresh state |
| `/opt/opportunities/compose.yml` | Deployed revision and runtime configuration |
| `/opt/opportunities/releases/<commit>` | Rebuildable source archive contents |

The existing Laptop 1 Restic backup includes the first four paths and pauses `opportunities` during its consistent snapshot. Releases and image layers are reproducible from Forgejo and are not backed up.

To recover, restore data, reports, Pi state, and the manifest with their original permissions, then deploy the recorded source revision. Restore the SQLite database with its WAL files as one snapshot. Do not replace Pi authentication with a new API key. If subscription authentication cannot refresh, complete native Pi `/login` for the application account.

Do not roll back application code across an incompatible database migration without restoring a matching backup. Preserve the failed state before any recovery operation that replaces persistent data.
