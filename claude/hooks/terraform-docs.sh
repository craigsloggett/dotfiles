#!/bin/sh
#
# terraform-docs.sh - regenerate README.md after Claude edits Terraform files
#
# Called as a PostToolUse hook. Reads JSON from stdin
# to extract the file path, then runs terraform-docs.
# Only runs in Terraform projects (repos with a .terraform-docs.yml file).

set -u

# Only run in Terraform projects.
if [ ! -f ".terraform-docs.yml" ]; then
  exit 0
fi

if ! command -v terraform-docs >/dev/null 2>&1; then
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

# Only run for Terraform files.
case "${file_path}" in
  *.tf)
    terraform-docs markdown table . --output-file README.md
    ;;
esac

exit 0
