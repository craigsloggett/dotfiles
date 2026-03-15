#!/bin/sh
#
# format.sh - auto-format files after Claude edits
#
# Called as a PostToolUse hook. Reads JSON from stdin
# to extract the file path, then runs the appropriate
# formatter based on file extension.

set -u

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

# Determine the file extension.
ext="${file_path##*.}"

case "${ext}" in
  tf | tfvars)
    if command -v terraform >/dev/null 2>&1; then
      terraform fmt "${file_path}" 2>/dev/null
    fi
    ;;
  yaml | yml)
    if command -v yamlfmt >/dev/null 2>&1; then
      yamlfmt "${file_path}" 2>/dev/null
    fi
    ;;
  sh)
    if command -v shfmt >/dev/null 2>&1; then
      shfmt -i 2 -ci -w "${file_path}" 2>/dev/null
    fi
    ;;
esac

exit 0
