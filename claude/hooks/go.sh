#!/bin/sh
#
# hooks/go.sh
#
# Format and lint the Go files among the given paths.

set -euf

command -v golangci-lint >/dev/null 2>&1 || exit 0

for file in "$@"; do
  shift

  case ${file} in
    *.go) ;;
    *) continue ;;
  esac

  [ -f "${file}" ] || continue

  set -- "$@" "${file}"
done

[ "$#" -gt 0 ] || exit 0

golangci-lint fmt "$@" >&2 || exit 2

directories="$(for file in "$@"; do dirname "${file}"; done | sort -u)"

IFS='
'

for directory in ${directories}; do
  (cd "${directory}" && golangci-lint run --path-mode=abs .) >&2 || exit 2
done
