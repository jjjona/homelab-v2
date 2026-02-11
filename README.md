# homelab-v2

Infrastructure-as-code for my homelab. Proxmox host, Docker Compose on LXC, fully Ansible-managed.

All secrets are SOPS-encrypted with age.

## Stack

- **Host:** Proxmox VE 9.1 on AMD Ryzen 7 7700X / 32GB DDR5 / RTX 4070 Ti
- **Containers:** Docker Compose on unprivileged LXC
- **Reverse proxy:** Traefik (Docker label auto-discovery + Redis provider + file provider)
- **Authentication:** PocketID (OIDC/passkey) + Tinyauth (forwardAuth middleware)
- **Remote access:** Cloudflare Tunnel
- **Storage:** ZFS mirror (NAS), NVMe (Docker volumes)
- **Sharing:** Samba + NFS on Proxmox host
- **Backups:** restic to Backblaze B2 (daily, healthchecks.io monitoring)
- **Secrets:** SOPS + age

## Services

Jellyfin, Plex, Sonarr, Radarr, Prowlarr, Lidarr, Bazarr, Jellyseerr, Autobrr, Linkding, Forgejo, Arcane — all behind SSO via Tinyauth/PocketID.

Gluetun VPN for Prowlarr + Autobrr. traefik-kop on a second LXC syncs remote Docker labels to Traefik via Redis.

## Network

| Host | IP |
|---|---|
| Proxmox | 192.168.0.158 |
| Docker host (LXC) | 192.168.0.159 |
| Claude Code (LXC) | 192.168.0.160 |
| Pandora (LXC) | 192.168.0.161 |

## Structure

```
ansible/          # Host + LXC configuration playbooks
docker/           # Docker Compose stack, Traefik config, app configs
```
