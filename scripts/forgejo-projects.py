#!/usr/bin/env python3
"""Migrate and verify the versioned HQ project inventory.

Secrets stay in SOPS and the local gh credential store. This script never prints
or writes either token. Forgejo is canonical; GitHub is a one-way SSH push mirror.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
INVENTORY = ROOT / "hq" / "projects.json"
SECRETS = ROOT / "ansible" / "secrets" / "hq.sops.yml"
API = os.environ.get("FORGEJO_API", "http://192.168.0.159:3001/api/v1").rstrip("/")
os.environ.setdefault(
    "SOPS_AGE_KEY_FILE", str(Path.home() / ".config" / "sops" / "age" / "keys.txt")
)


class ProjectError(RuntimeError):
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
        raise ProjectError(f"{argv[0]} failed with exit {result.returncode}")
    return result.stdout


def load_secrets() -> dict[str, str]:
    raw = run(["sops", "decrypt", "--output-type", "json", str(SECRETS)])
    data = json.loads(raw)
    return {
        "forgejo_token": data["forgejo_api_token"],
        "forgejo_user": data["forgejo_admin_user"],
        "hq_public_key": data["hq_ssh_public_key"],
    }


def github_token() -> str:
    return run(["gh", "auth", "token"]).strip()


def inventory() -> dict[str, Any]:
    return json.loads(INVENTORY.read_text())


def save_inventory(data: dict[str, Any]) -> None:
    INVENTORY.write_text(json.dumps(data, indent=2) + "\n")


def selected_projects(name: str | None, all_projects: bool) -> list[dict[str, Any]]:
    projects = inventory()["projects"]
    if all_projects:
        return projects
    if not name:
        raise ProjectError("pass a project name or --all")
    matches = [project for project in projects if project["slug"] == name]
    if not matches:
        raise ProjectError(f"unknown project: {name}")
    return matches


def api(
    method: str,
    path: str,
    token: str,
    body: dict[str, Any] | None = None,
    *,
    expected: tuple[int, ...] = (200,),
) -> Any:
    data = json.dumps(body).encode() if body is not None else None
    request = urllib.request.Request(
        f"{API}{path}",
        data=data,
        method=method,
        headers={
            "Authorization": f"token {token}",
            "Accept": "application/json",
            **({"Content-Type": "application/json"} if data else {}),
        },
    )
    try:
        with urllib.request.urlopen(request, timeout=180) as response:
            payload = response.read()
            if response.status not in expected:
                raise ProjectError(f"Forgejo {method} {path} returned {response.status}")
            return json.loads(payload) if payload else None
    except urllib.error.HTTPError as error:
        if error.code in expected:
            payload = error.read()
            return json.loads(payload) if payload else None
        raise ProjectError(f"Forgejo {method} {path} returned {error.code}") from None
    except urllib.error.URLError as error:
        raise ProjectError(f"Forgejo API unavailable: {error.reason}") from None


def quote(value: str) -> str:
    return urllib.parse.quote(value, safe="")


def repo_path(project: dict[str, Any]) -> str:
    return f"/repos/{quote(project['forgejo_owner'])}/{quote(project['slug'])}"


def get_repo(project: dict[str, Any], token: str) -> dict[str, Any] | None:
    try:
        return api("GET", repo_path(project), token)
    except ProjectError as error:
        if "returned 404" in str(error):
            return None
        raise


def wait_for_repo(project: dict[str, Any], token: str) -> dict[str, Any]:
    for _ in range(90):
        repo = get_repo(project, token)
        if repo and not repo.get("empty", True):
            return repo
        time.sleep(2)
    raise ProjectError(f"Forgejo import did not finish for {project['slug']}")


def migrate_repo(project: dict[str, Any], forgejo_token: str, gh_token: str) -> dict[str, Any]:
    existing = get_repo(project, forgejo_token)
    source = project["github"]
    if existing is None:
        print(f"{project['slug']}: importing GitHub history and metadata")
        api(
            "POST",
            "/repos/migrate",
            forgejo_token,
            {
                "auth_token": gh_token,
                "clone_addr": source["url"],
                "description": source["description"],
                "issues": source["issues"],
                "labels": source["issues"],
                "lfs": True,
                "milestones": source["issues"],
                "mirror": False,
                "private": source["private"],
                "pull_requests": True,
                "releases": True,
                "repo_name": project["slug"],
                "repo_owner": project["forgejo_owner"],
                "service": "github",
                "wiki": source["wiki"],
            },
            expected=(201,),
        )
        existing = wait_for_repo(project, forgejo_token)
    else:
        print(f"{project['slug']}: Forgejo repository already exists")

    # Archive only after mirror setup and verification. Archived repositories reject pushes.
    api(
        "PATCH",
        repo_path(project),
        forgejo_token,
        {
            "archived": False,
            "default_branch": source["default_branch"],
            "description": source["description"],
            "has_issues": source["issues"],
            "has_projects": source["projects"],
            "has_pull_requests": True,
            "has_releases": True,
            "has_wiki": source["wiki"],
            "private": source["private"],
            "template": project["slug"] == "project-starter" or source["template"],
        },
    )
    return existing


def gh_json(path: str, method: str = "GET", fields: dict[str, Any] | None = None) -> Any:
    argv = ["gh", "api", path, "--method", method]
    input_text = None
    if fields is not None:
        argv += ["--input", "-"]
        input_text = json.dumps(fields)
    output = run(argv, input_text=input_text)
    return json.loads(output) if output.strip() else None


def ensure_github_key(project: dict[str, Any], public_key: str) -> None:
    source = project["github"]
    path = f"repos/{source['owner']}/{source['name']}/keys"
    keys = gh_json(path)
    if any(item.get("key", "").strip() == public_key.strip() for item in keys):
        return
    title = "Forgejo push mirror"
    if any(item.get("title") == title for item in keys):
        title = f"{title} {int(time.time())}"
    gh_json(
        path,
        "POST",
        {"title": title, "key": public_key.strip(), "read_only": False},
    )


def ensure_push_mirror(project: dict[str, Any], token: str) -> dict[str, Any]:
    path = f"{repo_path(project)}/push_mirrors"
    mirrors = api("GET", f"{path}?limit=50", token)
    expected = f"git@github.com:{project['github']['owner']}/{project['github']['name']}.git"
    mirror = next(
        (
            item
            for item in mirrors
            if item.get("remote_address") == expected
            or item.get("remote_address", "").endswith(
                f"/{project['github']['owner']}/{project['github']['name']}.git"
            )
        ),
        None,
    )
    if mirror is None:
        print(f"{project['slug']}: creating one-way GitHub push mirror")
        mirror = api(
            "POST",
            path,
            token,
            {
                "interval": "8h",
                "remote_address": expected,
                "sync_on_commit": True,
                "use_ssh": True,
            },
        )
    public_key = mirror.get("public_key", "").strip()
    if not public_key:
        raise ProjectError(f"Forgejo did not return a mirror SSH key for {project['slug']}")
    ensure_github_key(project, public_key)
    # GitHub rejects pushes to archived repositories. Their imported refs are
    # verified below; the configured mirror becomes usable if they are revived.
    if not project["github"]["archived"]:
        api("POST", f"{repo_path(project)}/push_mirrors-sync", token, expected=(200, 204))
    return mirror


def refs_forgejo(project: dict[str, Any], token: str) -> dict[str, str]:
    data = api("GET", f"{repo_path(project)}/git/refs?limit=1000", token)
    return {
        item["ref"]: item["object"]["sha"]
        for item in data
        if item["ref"].startswith(("refs/heads/", "refs/tags/"))
    }


def refs_github(project: dict[str, Any]) -> dict[str, str]:
    source = project["github"]
    result: dict[str, str] = {}
    for kind in ("heads", "tags"):
        path = f"repos/{source['owner']}/{source['name']}/git/matching-refs/{kind}/"
        try:
            data = gh_json(path)
        except ProjectError:
            data = []
        for item in data:
            result[item["ref"]] = item["object"]["sha"]
    return result


def verify(project: dict[str, Any], token: str) -> None:
    forgejo = refs_forgejo(project, token)
    github = refs_github(project)
    missing = sorted(set(forgejo) - set(github))
    extra = sorted(set(github) - set(forgejo))
    changed = sorted(ref for ref in set(forgejo) & set(github) if forgejo[ref] != github[ref])
    if missing or extra or changed:
        raise ProjectError(
            f"{project['slug']}: ref mismatch "
            f"(missing={len(missing)}, extra={len(extra)}, changed={len(changed)})"
        )
    print(f"{project['slug']}: verified {len(forgejo)} branch/tag refs")


def archive_if_required(project: dict[str, Any], token: str) -> None:
    if project["github"]["archived"]:
        api("PATCH", repo_path(project), token, {"archived": True})


def new_project(name: str, description: str, private: bool, token: str) -> dict[str, Any]:
    if not re.fullmatch(r"[a-z0-9][a-z0-9-]{1,62}", name):
        raise ProjectError("project names must be 2-63 lowercase letters, digits, or hyphens")
    data = inventory()
    existing = next((item for item in data["projects"] if item["slug"] == name), None)
    if existing:
        print(f"{name}: already registered")
        return existing

    project = {
        "slug": name,
        "forgejo_owner": "jjjona",
        "class": "workspace",
        "deployment": "none",
        "github": {
            "owner": "jjjona",
            "name": name,
            "url": f"https://github.com/jjjona/{name}",
            "private": private,
            "archived": False,
            "default_branch": "main",
            "description": description,
            "fork": False,
            "template": False,
            "issues": True,
            "wiki": True,
            "projects": True,
            "disk_kib": 0,
            "updated_at": "",
        },
    }
    if get_repo(project, token) is None:
        print(f"{name}: generating Forgejo repository from project-starter")
        api(
            "POST",
            "/repos/jjjona/project-starter/generate",
            token,
            {
                "default_branch": "main",
                "description": description,
                "git_content": True,
                "labels": True,
                "name": name,
                "owner": "jjjona",
                "private": private,
                "protected_branch": False,
                "topics": True,
                "webhooks": False,
            },
            expected=(201,),
        )
    check = subprocess.run(
        ["gh", "repo", "view", f"jjjona/{name}"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        check=False,
    )
    if check.returncode:
        print(f"{name}: creating empty GitHub mirror repository")
        gh_json(
            "user/repos",
            "POST",
            {"name": name, "description": description, "private": private},
        )
    ensure_push_mirror(project, token)
    last_error: Exception | None = None
    for _ in range(30):
        try:
            verify(project, token)
            last_error = None
            break
        except ProjectError as error:
            last_error = error
            time.sleep(2)
    if last_error:
        raise last_error
    data["projects"].append(project)
    data["projects"].sort(key=lambda item: item["slug"].lower())
    save_inventory(data)
    print(f"{name}: registered; commit {INVENTORY.relative_to(ROOT)} after review")
    return project


def status(project: dict[str, Any], token: str) -> None:
    repo = get_repo(project, token)
    if repo is None:
        print(f"{project['slug']}: pending")
        return
    mirrors = api("GET", f"{repo_path(project)}/push_mirrors?limit=50", token)
    print(
        f"{project['slug']}: forgejo=yes mirror={'yes' if mirrors else 'no'} "
        f"visibility={'private' if repo['private'] else 'public'} archived={repo['archived']}"
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=("status", "migrate", "verify", "new"))
    parser.add_argument("name", nargs="?")
    parser.add_argument("--all", action="store_true")
    parser.add_argument("--description", default="")
    parser.add_argument("--public", action="store_true")
    args = parser.parse_args()
    projects = [] if args.command == "new" else selected_projects(args.name, args.all)
    secrets = load_secrets()
    token = secrets["forgejo_token"]
    # Fail before touching repositories if the stored token or target is wrong.
    user = api("GET", "/user", token)
    if not user.get("is_admin"):
        raise ProjectError("the HQ Forgejo token is not an administrator token")

    if args.command == "new":
        if not args.name:
            raise ProjectError("new requires a project name")
        new_project(args.name, args.description, not args.public, token)
        return 0

    gh_token = github_token() if args.command == "migrate" else ""
    for project in projects:
        if args.command == "status":
            status(project, token)
        elif args.command == "verify":
            verify(project, token)
        else:
            migrate_repo(project, token, gh_token)
            ensure_push_mirror(project, token)
            # Mirror execution is asynchronous; give the first sync a bounded window.
            last_error: Exception | None = None
            for _ in range(30):
                try:
                    verify(project, token)
                    last_error = None
                    break
                except ProjectError as error:
                    last_error = error
                    time.sleep(2)
            if last_error:
                raise last_error
            archive_if_required(project, token)
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except ProjectError as error:
        print(f"Error: {error}", file=sys.stderr)
        raise SystemExit(1)
