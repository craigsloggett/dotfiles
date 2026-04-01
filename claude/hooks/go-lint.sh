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

# Find the module root by walking up from the edited file.
dir="$(dirname "${file_path}")"
while [ "${dir}" != "/" ]; do
  if [ -f "${dir}/go.mod" ]; then
    break
  fi
  dir="$(dirname "${dir}")"
done

if [ ! -f "${dir}/go.mod" ]; then
  exit 0
fi

# Run golangci-lint with auto-fix, then output any remaining issues.
cd "${dir}" && golangci-lint run --fix ./... 2>&1

exit 0
