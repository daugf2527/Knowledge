#!/usr/bin/env bash
set -euo pipefail

REPO_URL="${1:-}"

read -rsp "New GitHub PAT: " GH_PAT
echo

if [[ -z "${GH_PAT}" ]]; then
  echo "ERROR: PAT is empty."
  exit 1
fi

echo "Validating token with GitHub API..."
USER_JSON="$(curl -fsS -H "Authorization: Bearer ${GH_PAT}" -H "Accept: application/vnd.github+json" https://api.github.com/user 2>/dev/null || true)"
LOGIN="$(printf '%s' "${USER_JSON}" | sed -n 's/.*"login":[[:space:]]*"\([^"]*\)".*/\1/p' | head -n 1)"

if [[ -z "${LOGIN}" ]]; then
  echo "ERROR: Token is invalid or lacks required access."
  echo "Hint: revoke leaked/old token and create a new fine-grained PAT."
  exit 2
fi

git config --global credential.helper store
git config --global credential.useHttpPath true
printf 'https://x-access-token:%s@github.com\n' "${GH_PAT}" > "${HOME}/.git-credentials"
chmod 600 "${HOME}/.git-credentials"
unset GH_PAT

echo "OK: Auth configured for GitHub login=${LOGIN}"

if [[ -n "${REPO_URL}" ]]; then
  echo "Testing remote access: ${REPO_URL}"
  if git ls-remote "${REPO_URL}" >/dev/null 2>&1; then
    echo "OK: Remote access works."
  else
    echo "ERROR: Remote access failed. Check repo permission/scope."
    exit 3
  fi
fi

