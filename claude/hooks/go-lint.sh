#!/bin/sh
#
# go-lint.sh - run golangci-lint after Claude edits Go files
#
# Called as a PostToolUse hook. Reads JSON from stdin
# to check the edited file path. Only runs in Go projects
# (repos with a go.mod file). Runs golangci-lint with --fix
# and outputs any remaining violations so the agent can
# address them immediately.

set -u

# Only run in Go projects.
if [ ! -f "go.mod" ]; then
  exit 0
fi

if ! command -v golangci-lint >/dev/null 2>&1; then
  exit 0
fi

if ! command -v jq >/dev/null 2>&1; then
  exit 0
fi

# Read tool context from stdin.
input="$(cat)"

# Extract the file path from tool_input.file_path.
file_path="$(printf '%s\n' "${input}" | jq -r '.tool_input.file_path // empty')"

if [ -z "${file_path}" ]; then
  exit 0
fi

# Only lint Go files.
case "${file_path}" in
  *.go) ;;
  *) exit 0 ;;
esac

# Run golangci-lint with auto-fix, then output any remaining issues.
golangci-lint run --fix ./... 2>&1

exit 0
