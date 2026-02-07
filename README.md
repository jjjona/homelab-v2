# homelab-v2

Infrastructure-as-code for my homelab. Proxmox host, Docker Compose on LXC, Ansible-managed.

All secrets are SOPS-encrypted with age. See the repo for details.

## Stack

- **Host:** Proxmox VE on AMD Ryzen 7 7700X / 32GB DDR5 / RTX 4070 Ti
- **Containers:** Docker Compose on unprivileged LXC
- **Reverse proxy:** Caddy (automatic HTTPS)
- **Remote access:** Cloudflare Tunnel
- **Storage:** ZFS mirror (NAS), NVMe (Docker volumes)
- **Sharing:** Samba + NFS on Proxmox host
- **Backups:** restic to Backblaze B2
- **Secrets:** SOPS + age

## Structure

```
install/          # Proxmox automated installer config
ansible/          # Host + LXC configuration playbooks
docker/           # Docker Compose stack, Caddyfile, app configs
backups/          # Backup scripts
scripts/          # Utility scripts (GPU switch, rebuild)
docs/             # Documentation
```
