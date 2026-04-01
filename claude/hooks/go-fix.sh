#!/bin/sh
#
# go-fix.sh - run Go analysis and auto-fix tools before stopping
#
# Called as a Stop hook. Only runs in Go projects
# (repos with a go.mod file). Blocks the agent from stopping
# if go vet reports issues so it can address them.

set -u

if ! command -v go >/dev/null 2>&1; then
  exit 0
fi

if ! command -v jq >/dev/null 2>&1; then
  exit 0
fi

# Read hook input from stdin.
input="$(cat)"

# Avoid infinite loops: if the agent already continued from a
# previous Stop hook, let it stop this time.
stop_hook_active="$(printf '%s\n' "${input}" | jq -r '.stop_hook_active // false')"
if [ "${stop_hook_active}" = "true" ]; then
  exit 0
fi

# Only run in Go projects.
if [ ! -f "go.mod" ]; then
  exit 0
fi

# Apply automatic fixes silently.
go fix ./... 2>/dev/null

# Check for issues. If go vet finds problems, block so the agent can fix them.
output="$(go vet ./... 2>&1)"

if [ -n "${output}" ]; then
  printf '%s\n' "${output}"
  exit 2
fi

exit 0
