#!/bin/sh

set -u

if ! command -v jq >/dev/null 2>&1; then
  exit 0
fi

input="$(cat)"
cwd="$(printf '%s\n' "${input}" | jq -r '.workspace.current_dir')"
used="$(printf '%s\n' "${input}" | jq -r '.context_window.used_percentage // empty')"
if [ -n "${used}" ]; then
  printf '%s  ctx: %s%%' "${cwd}" "${used}"
else
  printf '%s' "${cwd}"
fi
