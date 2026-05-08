#!/bin/sh
#
# hooks/docs.sh
#
# Regenerate documentation after Claude edits.

set -euf

TOOL_CONTEXT="$(cat)"
readonly TOOL_CONTEXT

check_prerequisites() {
  for utility in terraform-docs jq; do
    command -v "${utility}" >/dev/null 2>&1 || return 1
  done
}

get_file_path() (
  tool_context="$1"
  printf '%s' "${tool_context}" | jq -r '.tool_input.file_path // empty'
)

get_file_extension() (
  file_path="$1"
  printf '%s' "${file_path##*.}"
)

main() {
  check_prerequisites || return 0

  file_path="$(get_file_path "${TOOL_CONTEXT}")"
  if [ -z "${file_path}" ]; then
    return 0
  fi

  file_extension="$(get_file_extension "${file_path}")"
  if [ -z "${file_extension}" ]; then
    return 0
  fi

  case "${file_extension}" in
    tf)
      terraform-docs markdown table "$(dirname "${file_path}")" --output-file README.md --output-mode inject 2>/dev/null
      ;;
  esac
}

main "$@"
