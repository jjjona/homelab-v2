#!/usr/bin/env bash
set -u

fail=0

check() {
  "$@"
}

ok() { printf 'ok: %s\n' "$1"; }
bad() { printf 'fail: %s\n' "$1" >&2; fail=1; }

repo_root="$(git rev-parse --show-toplevel 2>/dev/null)" || {
  echo 'fail: not inside a git repository' >&2
  exit 1
}
cd "$repo_root" || exit 1

for cmd in git ssh python3 ansible ansible-playbook ansible-galaxy sops age age-keygen; do
  if command -v "$cmd" >/dev/null 2>&1; then
    ok "found $cmd"
  else
    bad "missing $cmd"
  fi
done

if ansible-galaxy collection list 2>/dev/null | grep -q '^community\.sops\>'; then
  ok 'found community.sops collection'
else
  bad 'missing community.sops collection (run: ansible-galaxy collection install -r ansible/requirements.yml)'
fi

if check test -f ansible/inventory/hosts.yml; then
  ok 'found ansible inventory'
else
  bad 'missing ansible/inventory/hosts.yml'
fi

if (cd ansible && ansible-inventory --list >/dev/null); then
  ok 'ansible inventory parses'
else
  bad 'ansible inventory does not parse'
fi

if test -n "${SOPS_AGE_KEY_FILE:-}"; then
  key_file="$SOPS_AGE_KEY_FILE"
else
  key_file="$HOME/.config/sops/age/keys.txt"
fi

if test -f "$key_file"; then
  if sops -d ansible/secrets/users.sops.yml >/dev/null 2>&1; then
    ok 'SOPS decrypt check passed'
  else
    bad 'SOPS decrypt check failed'
  fi
else
  bad "SOPS age key file not found at $key_file"
fi

if git diff --quiet -- .; then
  ok 'no unstaged tracked diffs'
else
  bad 'unstaged tracked diffs present'
fi

exit "$fail"
