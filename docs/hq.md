# HQ operations and recovery

## Purpose

`https://hq.jnrm.eu` is the single-user Pi management terminal for this homelab. It runs in unprivileged LXC 206 at `192.168.0.170`. Pi works in `/opt/homelab`, where Forgejo is the canonical Git remote.

Project code does not run in HQ. Isolated project workspaces run in unprivileged Docker LXC 207 at `192.168.0.172`. This separation keeps the Age identity, host-management SSH key, Ansible inventory, and GitHub administration away from project code.

## Access boundary

The public route is:

```text
Cloudflare Tunnel -> Traefik web entrypoint -> Tinyauth/PocketID -> HQ
```

HQ then requires all of these:

- exact `hq.jnrm.eu` Host;
- exact `https://hq.jnrm.eu` Origin;
- the sole enabled PocketID administrator's `Remote-Email` header;
- a Secure, HttpOnly, SameSite=Strict application session.

LXC 206 accepts port `4484` only from Traefik at `192.168.0.159`. Project workspace ports `46000-46999` accept new connections only from Traefik through `DOCKER-USER` conntrack rules. A direct LAN connection is blocked even if it forges the identity header.

Tinyauth is the first gate, not the complete security boundary. Never expose either backend port range directly.

## Repository policy

- Forgejo at `git.jnrm.eu` is canonical.
- GitHub is a one-way SSH push mirror.
- Local and deployed checkouts use Forgejo as `origin`.
- Local GitHub remotes are fetch-only; their push URL is `DISABLED`.
- Forgejo uses a separate writable GitHub deploy key for each mirror. It does not retain the broad GitHub OAuth token.
- GitHub mirrors preserve Git branches and tags. They do not preserve Forgejo issues, pull requests, packages, Actions state, users, or settings.

The versioned registry is [`../hq/projects.json`](../hq/projects.json). It records all managed projects, visibility, archive state, deployment class, mirror target, and allocated workspace port.

## Starting work

Use Pi's `/new` and `/resume` commands inside the HQ terminal for management conversations.

Create a private repository from Project Starter, create its GitHub mirror, and register it:

```sh
hq-project new <slug> --description "<purpose>"
```

Add `--public` only when public source is deliberate.

Create or resume an isolated Pi workspace for any registered project:

```sh
hq-workspace create <slug>
```

The command reports:

```text
Project:     https://git.jnrm.eu/<owner>/<slug>
Workspace:   https://<slug>-code.jnrm.eu
Application: not deployed
```

The project factory deliberately does not invent an application runtime. Once the first useful build defines its process, health check, durable state, and backup needs, add the smallest application deployment to this repository. Staging is disposable; production data needs an explicit backup declaration.

## Host roles

| Host | Role |
|---|---|
| Proxmox | Hypervisor and storage |
| LXC 200 | Core Docker services, Traefik, Forgejo, authentication |
| LXC 205 | Hive only |
| LXC 206 | Privileged HQ management plane |
| LXC 207 | Isolated project-code workspaces |
| Laptop 1 | Existing small production applications |
| Laptop 2 | GPU and Jade workloads |

Do not move project builds into HQ or core LXC 200. Keep Laptop 2 GPU-specific.

## Deployment

Run playbooks from `ansible/` with `SOPS_AGE_KEY_FILE` set explicitly.

```sh
export SOPS_AGE_KEY_FILE="$HOME/.config/sops/age/keys.txt"

ansible-playbook playbooks/18-hq.yml
ansible-playbook playbooks/19-workspaces.yml
ansible-playbook playbooks/20-hq-backups.yml
ansible-playbook playbooks/21-app-terminals.yml
```

`playbooks/21-app-terminals.yml` deploys the Tinyauth-protected Todo and Playlists terminal companions on Laptop 1. Each browser drawer attaches to a persistent Bash tmux session with Pi and the complete `pi-working-discipline` profile. These two terminals are deliberately production-coupled: they can edit their live checkout and app data, but they do not receive the Docker socket or homelab management credentials. Commit and push source changes before the normal application redeploy.

Use `playbooks/17-forgejo-remotes.yml` only to reconverge the existing Writing, Todo, Playlists, and Hive checkout remotes. It does not restart those applications.

The remote-capable Project Starter remains usable locally. Its managed remote mode is documented in its own `README.md` and tests.

## Backups

Three independent recovery layers exist:

1. Forgejo data is in the Proxmox Restic backup path `/mnt/docker-data/docker`.
2. Every managed repository has a GitHub Git mirror.
3. HQ and workspace state back up directly to the same encrypted B2 repository:
   - HQ daily at 05:00;
   - workspaces daily at 05:30.

Workspace containers pause during their snapshot and unpause through a shell trap. The Proxmox and laptop backups remain staggered at their existing times.

## Recovery

Keep the external management laptop as the break-glass path. HQ cannot repair its own hypervisor when Proxmox is unavailable.

### Restore Forgejo

1. Restore `/mnt/docker-data/docker/forgejo/data` from the latest `proxmox` Restic snapshot.
2. Start Forgejo.
3. Run SQLite `PRAGMA integrity_check` on `gitea.db`.
4. Run `git fsck --no-dangling` on every restored bare repository.
5. Run:

   ```sh
   ./scripts/forgejo-projects.py verify --all
   ```

6. Confirm active push mirrors report no `last_error`.

### Recreate HQ

1. Restore the controller Age identity outside the repository.
2. Run `playbooks/18-hq.yml` from the external laptop.
3. The playbook restores Pi and GitHub authentication from the controller without logging their values.
4. Run `playbooks/20-hq-backups.yml`.
5. Verify `https://hq.jnrm.eu` returns Tinyauth's unauthenticated response before login.

### Recreate project workspaces

1. Run `playbooks/19-workspaces.yml`.
2. Run `playbooks/20-hq-backups.yml`.
3. Restore `/srv/workspaces` when uncommitted work or Pi sessions are needed.
4. Otherwise, recreate individual workspaces from Forgejo with `hq-workspace create <slug>`.

### Recreate application terminals

1. Restore `/opt/app-terminals` with the Laptop 1 backup when uncommitted work or Pi sessions are needed.
2. Run `playbooks/21-app-terminals.yml` to rebuild the image, restore missing repository access, and start both terminals.
3. Run `playbooks/11-laptops.yml --limit laptop1` to reconverge the backup job.
4. Verify `todo-terminal.jnrm.eu` and `playlists-terminal.jnrm.eu` return Tinyauth's unauthenticated response.

## Deliberate limits

- Forgejo 9.0.3 was not upgraded during the migration. Upgrade it in a separate maintenance window after a fresh backup and restore test.
- The archived `project-foundation-design` mirror is configured but cannot push while GitHub remains archived. Its imported refs have exact parity.
- The unrelated `niels/katana-mirror` repository is registered as external and was not changed.
- The external laptop's Hive checkout contains pre-existing deleted files and is behind canonical Forgejo. It was intentionally not reset, stashed, or pulled.
- Existing application deployments still use their current mutable-checkout model. Move to immutable image-digest promotion only when a real staging-to-production workflow needs it.
