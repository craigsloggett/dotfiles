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

# Extract the file path from tool_input.file_path.
file_path="$(printf '%s\n' "${input}" | jq -r '.tool_input.file_path // empty')"

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

exit 0
