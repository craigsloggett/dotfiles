#!/bin/sh
#
# hooks/json.sh
#
# Format and lint the JSON files among the given paths.

set -euf

command -v jq >/dev/null 2>&1 || exit 0

for file in "$@"; do
  case ${file} in
    *.json) ;;
    *) continue ;;
  esac

  [ -f "${file}" ] || continue

  formatted="$(jq -S . "${file}")" || exit 2
  [ "${formatted}" = "$(cat "${file}")" ] || printf '%s\n' "${formatted}" >"${file}"
done
