#!/usr/bin/env python3
"""Create or resume an isolated browser-hosted Pi project workspace."""

from __future__ import annotations

import argparse
import json
import os
import re
import shlex
import subprocess
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
INVENTORY = ROOT / "hq" / "projects.json"
SECRETS = ROOT / "ansible" / "secrets" / "hq.sops.yml"
FORGEJO_API = os.environ.get("FORGEJO_API", "http://192.168.0.159:3001/api/v1").rstrip("/")
os.environ.setdefault(
    "SOPS_AGE_KEY_FILE", str(Path.home() / ".config" / "sops" / "age" / "keys.txt")
)


class WorkspaceError(RuntimeError):
    pass


def run(argv: list[str], *, input_text: str | None = None) -> str:
    result = subprocess.run(
        argv,
        input=input_text,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    if result.returncode:
        raise WorkspaceError(f"{argv[0]} failed with exit {result.returncode}")
    return result.stdout


def remote(command: str, *, input_text: str | None = None) -> str:
    return run(["ssh", "-o", "BatchMode=yes", "workspaces", command], input_text=input_text)


def secrets() -> dict[str, str]:
    value = json.loads(run(["sops", "decrypt", "--output-type", "json", str(SECRETS)]))
    return {
        "token": value["forgejo_api_token"],
        "identity": value["hq_allowed_email"],
    }


def api(method: str, path: str, token: str, body: dict[str, Any] | None = None) -> Any:
    data = json.dumps(body).encode() if body is not None else None
    request = urllib.request.Request(
        f"{FORGEJO_API}{path}",
        data=data,
        method=method,
        headers={
            "Authorization": f"token {token}",
            "Content-Type": "application/json",
            "Accept": "application/json",
        },
    )
    try:
        with urllib.request.urlopen(request, timeout=60) as response:
            payload = response.read()
            return json.loads(payload) if payload else None
    except urllib.error.HTTPError as error:
        raise WorkspaceError(f"Forgejo {method} {path} returned {error.code}") from None


def load_inventory() -> dict[str, Any]:
    return json.loads(INVENTORY.read_text())


def save_inventory(data: dict[str, Any]) -> None:
    INVENTORY.write_text(json.dumps(data, indent=2) + "\n")


def project_record(data: dict[str, Any], slug: str) -> tuple[dict[str, Any], bool]:
    project = next((item for item in data["projects"] if item["slug"] == slug), None)
    if project:
        return project, True
    existing = next(
        (
            item
            for item in data.get("forgejo_existing_projects", [])
            if item["slug"] == slug and item.get("managed_by_hq")
        ),
        None,
    )
    if existing:
        return {"slug": slug, "forgejo_owner": existing["owner"], **existing}, False
    raise WorkspaceError(f"unknown or externally managed project: {slug}")


def allocate_port(data: dict[str, Any], project: dict[str, Any], persistent: bool) -> int:
    if project.get("workspace_port"):
        return int(project["workspace_port"])
    used = {
        int(item["workspace_port"])
        for item in data["projects"] + data.get("forgejo_existing_projects", [])
        if item.get("workspace_port")
    }
    port = next(value for value in range(46000, 47000) if value not in used)
    project["workspace_port"] = port
    if not persistent:
        for item in data["forgejo_existing_projects"]:
            if item["owner"] == project["owner"] and item["slug"] == project["slug"]:
                item["workspace_port"] = port
                break
    save_inventory(data)
    return port


def ensure_workspace_key(owner: str, slug: str, token: str) -> None:
    root = f"/srv/workspaces/{slug}"
    key = f"{root}/ssh/id_ed25519"
    remote(
        f"install -d -o 1000 -g 1000 -m 0700 {shlex.quote(root + '/ssh')} && "
        f"test -f {shlex.quote(key)} || runuser -u workspace -- ssh-keygen -q -t ed25519 -N '' "
        f"-C {shlex.quote('hq-workspace-' + slug)} -f {shlex.quote(key)}"
    )
    public = remote(f"cat {shlex.quote(key + '.pub')}").strip()
    keys = api("GET", f"/repos/{owner}/{slug}/keys", token)
    comparable = public.split()[:2]
    if not any(item.get("key", "").split()[:2] == comparable for item in keys):
        api(
            "POST",
            f"/repos/{owner}/{slug}/keys",
            token,
            {"title": f"hq-workspace-{slug}", "key": public, "read_only": False},
        )


def ensure_checkout(owner: str, slug: str) -> None:
    root = f"/srv/workspaces/{slug}"
    repo = f"{root}/repo"
    ssh = f"{root}/ssh"
    url = f"ssh://git@192.168.0.159:2222/{owner}/{slug}.git"
    command = f"ssh -i {ssh}/id_ed25519 -o IdentitiesOnly=yes -o UserKnownHostsFile={ssh}/known_hosts -o StrictHostKeyChecking=yes"
    remote(
        f"install -d -o 1000 -g 1000 -m 0755 {shlex.quote(root)} && "
        f"cp /srv/workspaces/forgejo_known_hosts {shlex.quote(ssh + '/known_hosts')} && "
        f"chown 1000:1000 {shlex.quote(ssh + '/known_hosts')} && chmod 0644 {shlex.quote(ssh + '/known_hosts')} && "
        f"if test ! -d {shlex.quote(repo + '/.git')}; then "
        f"runuser -u workspace -- env GIT_SSH_COMMAND={shlex.quote(command)} git clone {shlex.quote(url)} {shlex.quote(repo)}; "
        f"else test \"$(runuser -u workspace -- git -C {shlex.quote(repo)} remote get-url origin)\" = {shlex.quote(url)}; fi"
    )
    config = f"""Host 192.168.0.159
    HostName 192.168.0.159
    Port 2222
    User git
    IdentityFile /home/workspace/.ssh/id_ed25519
    IdentitiesOnly yes
    UserKnownHostsFile /home/workspace/.ssh/known_hosts
    StrictHostKeyChecking yes
"""
    remote(
        f"install -o 1000 -g 1000 -m 0600 /dev/stdin {shlex.quote(ssh + '/config')}",
        input_text=config,
    )


def deploy(slug: str, owner: str, port: int, identity: str) -> None:
    root = f"/srv/workspaces/{slug}"
    origin = f"https://{slug}-code.jnrm.eu"
    compose = f"""services:
  workspace:
    image: hq-workspace:0.1
    container_name: workspace-{slug}
    restart: unless-stopped
    environment:
      PROJECT_WORKSPACE_ROOT: /workspace
      PROJECT_PUBLIC_ORIGIN: {json.dumps(origin)}
      PROJECT_AUTH_IDENTITY: {json.dumps(identity)}
      PROJECT_BIND_HOST: 0.0.0.0
      PROJECT_PORT: 4484
      PROJECT_NO_OPEN: 1
    ports:
      - "192.168.0.172:{port}:4484"
    volumes:
      - {root}/repo:/workspace
      - {root}/ssh:/home/workspace/.ssh:ro
      - {root}/pi-auth.json:/home/workspace/.pi/agent/auth.json
      - {root}/sessions:/home/workspace/.pi/agent/sessions
      - {root}/runtime:/opt/project-starter/.project-runtime
"""
    remote(
        f"install -d -o 1000 -g 1000 -m 0700 {root}/sessions {root}/runtime && "
        f"test -f {root}/pi-auth.json || install -o 1000 -g 1000 -m 0600 /srv/workspaces/pi-auth-seed.json {root}/pi-auth.json && "
        f"install -o root -g root -m 0600 /dev/stdin {root}/compose.yml",
        input_text=compose,
    )
    remote(f"docker compose -f {root}/compose.yml up -d")
    route = f"""http:
  routers:
    workspace-{slug}:
      rule: "Host(`{slug}-code.jnrm.eu`)"
      entryPoints: [web]
      service: workspace-{slug}
      middlewares: [workspace-{slug}-nocache]
  services:
    workspace-{slug}:
      loadBalancer:
        servers:
          - url: "http://192.168.0.172:{port}"
  middlewares:
    workspace-{slug}-nocache:
      headers:
        customResponseHeaders:
          Cache-Control: "no-store"
"""
    run(
        [
            "ssh",
            "-o",
            "BatchMode=yes",
            "docker-host",
            f"install -o root -g root -m 0644 /dev/stdin /mnt/data/docker/core/traefik/dynamic/workspace-{slug}.yml",
        ],
        input_text=route,
    )
    curl = shlex.join(
        [
            "curl",
            "-fsS",
            "-H",
            f"Host: {slug}-code.jnrm.eu",
            "-H",
            f"Origin: {origin}",
            "-H",
            f"Remote-Email: {identity}",
            f"http://192.168.0.172:{port}/",
        ]
    )
    for _ in range(60):
        result = subprocess.run(
            ["ssh", "docker-host", curl],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            check=False,
        )
        if result.returncode == 0:
            break
        time.sleep(2)
    else:
        raise WorkspaceError(f"workspace backend did not become ready: {slug}")


def create(slug: str) -> None:
    if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._-]{1,100}", slug):
        raise WorkspaceError("invalid project slug")
    data = load_inventory()
    project, persistent = project_record(data, slug)
    if project.get("github", {}).get("archived"):
        raise WorkspaceError("archived projects must be unarchived before opening a workspace")
    values = secrets()
    owner = project.get("forgejo_owner", project.get("owner"))
    port = allocate_port(data, project, persistent)
    ensure_workspace_key(owner, slug, values["token"])
    ensure_checkout(owner, slug)
    deploy(slug, owner, port, values["identity"])
    print(f"Project:   https://git.jnrm.eu/{owner}/{slug}")
    print(f"Workspace: https://{slug}-code.jnrm.eu")
    print("Application: not deployed; define its runtime with HQ after the first useful build")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=("create",))
    parser.add_argument("slug")
    args = parser.parse_args()
    create(args.slug)
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except WorkspaceError as error:
        print(f"Error: {error}", file=sys.stderr)
        raise SystemExit(1)
