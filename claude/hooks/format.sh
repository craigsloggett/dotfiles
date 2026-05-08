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

main() {
  check_prerequisites || return 0

  file_path="$(printf '%s' "${HOOK_INPUT}" | jq -r '.tool_input.file_path // empty')"

  [ -n "${file_path}" ] || return 0
  [ -f "${file_path}" ] || return 0

  file_extension="${file_path##*.}"

  case "${file_extension}" in
    tf | tfvars)
      terraform fmt "${file_path}" 2>/dev/null
      ;;
    yaml | yml)
      yamlfmt "${file_path}" 2>/dev/null
      ;;
    go)
      gofmt -s -w "${file_path}" 2>/dev/null
      ;;
    sh)
      shfmt -i 2 -ci -w "${file_path}" 2>/dev/null
      ;;
  esac
}

main "$@"
