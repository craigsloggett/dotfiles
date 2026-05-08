#!/bin/sh
#
# hooks/format.sh
#
# Format files after Claude edits.

set -euf

TOOL_CONTEXT="$(cat)"
readonly TOOL_CONTEXT

check_prerequisites() {
  for utility in jq terraform yamlfmt gofmt golangci-lint shfmt; do
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

get_go_project_root() (
  file_path="$1"
  file_parent_directory="$(dirname "${file_path}")"

  while [ "${file_parent_directory}" != "/" ]; do
    if [ -f "${file_parent_directory}"/go.mod ]; then
      printf '%s' "${file_parent_directory}"
      return 0
    fi
  done

  return 1
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
    tf | tfvars)
      terraform fmt "${file_path}" 2>/dev/null
      ;;
    yaml | yml)
      yamlfmt "${file_path}" 2>/dev/null
      ;;
    go)
      gofmt -s -w "${file_path}" 2>/dev/null
      # golangci-lint --fix
      go_project_root="$(get_go_project_root "${file_path}")" || return 0
      cd "${go_project_root}"
      golangci-lint run --fix ./... >/dev/null 2>&1
      cd -
      ;;
    sh)
      shfmt -i 2 -ci -w "${file_path}" 2>/dev/null
      ;;
  esac
}

main "$@"
