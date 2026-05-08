#!/bin/sh
#
# hooks/docs.sh
#
# Regenerate documentation on PostToolUse

set -euf

HOOK_INPUT="$(cat)"
readonly HOOK_INPUT

check_prerequisites() {
  for utility in jq terraform-docs; do
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
    tf)
      terraform-docs markdown table "$(dirname "${file_path}")" --output-file README.md --output-mode inject 2>/dev/null
      ;;
  esac
}

main "$@"
