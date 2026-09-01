# Homelab operations

This repository is the source of truth for the Proxmox homelab and related managed hosts. Use Pi directly; do not depend on Hermes, Proxymoxy, or agent-specific skills.

## Authority order

1. Current live inspection.
2. This repository's Ansible and Docker configuration.
3. Git history and repository documentation.
4. Historical notes only as evidence; revalidate before relying on them.

## Safety

- Preserve the existing dirty working tree and unrelated changes. Never reset, clean, stash, or overwrite them without explicit approval.
- Never print, log, commit, or place in chat decrypted SOPS values, Age private keys, SSH private keys, auth stores, `.env` files, or other credentials.
- Never generate a replacement Age key as a substitute for the existing key. A new key cannot decrypt current files; key rotation requires decrypting and re-encrypting every secret deliberately.
- Prefer reproducible IaC changes over live-only changes.
- Inspect live state before changing it and verify live state independently afterward.
- Use the narrowest applicable playbook, tags, limits, and check mode. Treat destructive operations, storage changes, identity/security changes, VM deletion, and persistent-data migration as high risk requiring explicit scope.
- Read target-repository `AGENTS.md` or `CLAUDE.md` before editing application repositories.

## Operator environment

Expected local tools:

- `ansible` / `ansible-playbook`
- `sops`
- `age` / `age-keygen`
- `community.sops` Ansible collection
- SSH alias `proxmox` for `root@192.168.0.158`

The existing SOPS recipient is:

```text
age1hxq9k30age89dnn9z8e5pmsd28936gxvv5tmqur87l2wmeg2qg5qr5x3ws
```

The private key should be restored outside the repository at:

```text
~/.config/sops/age/keys.txt
```

with mode `0600`. Set `SOPS_AGE_KEY_FILE` explicitly when needed. Never reveal the private key while validating it; verify by decrypting an encrypted file to `/dev/null`.

## Live access

- Proxmox: `ssh proxmox '<command>'`
- Docker-host LXC 200 can be inspected through Proxmox: `ssh proxmox "pct exec 200 -- <command>"`
- Hive: `ssh -T -o RemoteCommand=none hive '<command>'`
- Writing/Todo host: `ssh -T -o RemoteCommand=none writing '<command>'` or `todo`

The `hive`, `writing`, and `todo` aliases have interactive `RemoteCommand` settings, so automation must override them as shown.

## Change workflow

1. Run `./scripts/preflight.sh`.
2. Inspect Git status and relevant current files.
3. Inspect the live target and capture a safe baseline without secret output.
4. Make the smallest reproducible IaC change.
5. Run syntax/static checks and `--check` where supported and safe.
6. Review the exact diff for secret exposure and unintended scope.
7. Apply narrowly from `ansible/` only after required key material and access checks pass.
8. Verify live state independently and report exact checks and remaining drift.

Do not commit or push unless explicitly requested. Keep commits small and never mix unrelated pre-existing changes into a commit.
