# homelab-v2

Infrastructure-as-code for my homelab. Proxmox host, Talos Kubernetes cluster, GitOps with ArgoCD.

All secrets are SOPS-encrypted with age. See the repo for details.

## Stack

- **Host:** Proxmox VE on AMD Ryzen 7 7700X / 32GB DDR5 / RTX 4070 Ti
- **Kubernetes:** Talos Linux
- **GitOps:** ArgoCD
- **Networking:** Cilium CNI, MetalLB, Nginx Ingress, Cloudflare Tunnel
- **Storage:** ZFS (NAS), Longhorn (k8s PVs)
- **Auth:** Keycloak SSO
- **Monitoring:** Prometheus + Grafana
- **Backups:** restic to Backblaze B2

## Structure

```
install/          # Proxmox automated installer config
ansible/          # Host configuration playbooks
talos/            # Talos machine configs
kubernetes/       # k8s manifests (ArgoCD apps)
  bootstrap/      # ArgoCD itself
  infrastructure/ # Ingress, cert-manager, storage, etc.
  apps/           # Jellyfin, arr suite, Linkwarden, etc.
backups/          # Backup configuration
scripts/          # Utility scripts
```
