#!/bin/sh
#
# terraform-docs.sh - regenerate README.md after Claude edits Terraform files
#
# Called as a PostToolUse hook. Reads JSON from stdin
# to extract the file path, then runs terraform-docs.
# Only runs in Terraform projects (repos with a .terraform-docs.yml file).

set -u

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
  *.tf) ;;
  *) exit 0 ;;
esac

# Find the project root by walking up from the edited file.
dir="$(dirname "${file_path}")"
while [ "${dir}" != "/" ]; do
  if [ -f "${dir}/.terraform-docs.yml" ]; then
    break
  fi
  dir="$(dirname "${dir}")"
done

if [ ! -f "${dir}/.terraform-docs.yml" ]; then
  exit 0
fi

terraform-docs markdown table "${dir}" --output-file README.md

exit 0
