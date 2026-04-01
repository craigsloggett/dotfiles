#!/bin/sh
#
# go-fmt.sh - format edited Go file after Claude edits
#
# Called as a PostToolUse hook. Reads JSON from stdin
# to extract the file path, then runs gofmt on it.
# Only runs in Go projects (repos with a go.mod file).

set -u

if ! command -v gofmt >/dev/null 2>&1; then
  exit 0
fi

if ! command -v jq >/dev/null 2>&1; then
  exit 0
fi

# Read tool context from stdin.
input="$(cat)"

# Extract the file path and session ID from the hook input.
file_path="$(printf '%s\n' "${input}" | jq -r '.tool_input.file_path // empty')"
session_id="$(printf '%s\n' "${input}" | jq -r '.session_id // empty')"

if [ -z "${file_path}" ]; then
  exit 0
fi

# Only format Go files.
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

gofmt -w "${file_path}"

# Track edited Go files for the go-fix Stop hook.
if [ -n "${session_id}" ]; then
  state_dir="${XDG_STATE_HOME:-${HOME}/.local/state}/claude"
  mkdir -p "${state_dir}"
  printf '%s\n' "${file_path}" >>"${state_dir}/edited-go-${session_id}"
fi

exit 0
