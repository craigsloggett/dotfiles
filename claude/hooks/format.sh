#!/bin/sh
#
# format.sh - auto-format files after Claude edits
#
# Called as a PostToolUse hook. Reads JSON from stdin
# to extract the file path, then runs the appropriate
# formatter based on file extension.

set -u

# Read tool context from stdin.
input="$(cat)"

# Extract the file path from tool_input.file_path.
file_path="$(printf '%s\n' "${input}" | sed -n 's/.*"file_path" *: *"\([^"]*\)".*/\1/p' | head -1)"

if [ -z "${file_path}" ]; then
  exit 0
fi

# Determine the file extension.
ext="${file_path##*.}"

case "${ext}" in
  go)
    if command -v gofmt >/dev/null 2>&1; then
      gofmt -w "${file_path}" 2>/dev/null
    fi
    ;;
  tf|tfvars)
    if command -v terraform >/dev/null 2>&1; then
      terraform fmt "${file_path}" 2>/dev/null
    fi
    ;;
  yaml|yml)
    if command -v yamlfmt >/dev/null 2>&1; then
      yamlfmt "${file_path}" 2>/dev/null
    fi
    ;;
esac

exit 0
