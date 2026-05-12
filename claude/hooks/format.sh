#!/bin/sh
#
# hooks/format.sh
#
# Format files on PostToolUse

set -euf

HOOK_INPUT="$(cat)"
readonly HOOK_INPUT

check_prerequisites() {
  for utility in gofmt jq shfmt terraform yamlfmt; do
    command -v "${utility}" >/dev/null 2>&1 || return 1
  done
}

block_with_reason() (
  reason="$1"
  jq -n --arg reason "${reason}" '{decision: "block", reason: $reason}'
)

format_file() (
  file_path="$1"
  file_extension="${file_path##*.}"

  case "${file_extension}" in
    tf | tfvars)
      terraform fmt "${file_path}" 2>&1
      ;;
    yaml | yml)
      yamlfmt "${file_path}" 2>&1
      ;;
    go)
      gofmt -s -w "${file_path}" 2>&1
      ;;
    sh)
      shfmt -i 2 -ci -w "${file_path}" 2>&1
      ;;
  esac
)

main() {
  check_prerequisites || return 0

  file_path="$(printf '%s' "${HOOK_INPUT}" | jq -r '.tool_input.file_path // empty')"

  [ -n "${file_path}" ] || return 0
  [ -f "${file_path}" ] || return 0

  if ! format_output="$(format_file "${file_path}")"; then
    block_with_reason "Formatter reported errors for ${file_path}:
${format_output}"
  fi
}

main "$@"
