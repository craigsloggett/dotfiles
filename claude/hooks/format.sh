#!/bin/sh
#
# format.sh - auto-format files after Claude edits
#
# Called as a PostToolUse hook. Reads JSON from stdin
# to extract the file path, then runs the appropriate
# formatter based on file extension. Tracks formatted
# files to a per-session state file for the lint Stop hook.

set -u

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

# Determine the file extension.
ext="${file_path##*.}"
formatted=false

case "${ext}" in
  tf | tfvars)
    if command -v terraform >/dev/null 2>&1; then
      terraform fmt "${file_path}" 2>/dev/null
      formatted=true
    fi
    ;;
  yaml | yml)
    if command -v yamlfmt >/dev/null 2>&1; then
      yamlfmt "${file_path}" 2>/dev/null
      formatted=true
    fi
    ;;
  go)
    if command -v gofmt >/dev/null 2>&1; then
      gofmt -w "${file_path}" 2>/dev/null
      formatted=true
    fi
    # Run golangci-lint --fix silently from the module root.
    if command -v golangci-lint >/dev/null 2>&1; then
      dir="$(dirname "${file_path}")"
      while [ "${dir}" != "/" ]; do
        if [ -f "${dir}/go.mod" ]; then
          break
        fi
        dir="$(dirname "${dir}")"
      done
      if [ -f "${dir}/go.mod" ]; then
        cd "${dir}" && golangci-lint run --fix ./... >/dev/null 2>&1
        formatted=true
      fi
    fi
    ;;
  sh)
    if command -v shfmt >/dev/null 2>&1; then
      shfmt -i 2 -ci -w "${file_path}" 2>/dev/null
      formatted=true
    fi
    ;;
esac

# Track formatted files for the lint Stop hook.
if [ "${formatted}" = "true" ] && [ -n "${session_id}" ]; then
  state_dir="${XDG_STATE_HOME:-${HOME}/.local/state}/claude"
  mkdir -p "${state_dir}"
  printf '%s\n' "${file_path}" >>"${state_dir}/edited-${session_id}"
fi

exit 0
