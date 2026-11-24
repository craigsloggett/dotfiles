#!/bin/sh
#
# hooks/prose.sh
#
# Lint the prose in the Markdown and Go files among the given paths.
# Only an error-level alert fails the check.

set -euf

command -v vale >/dev/null 2>&1 || exit 0

for file in "$@"; do
  shift

  case ${file} in
    *.md | *.go) ;;
    *) continue ;;
  esac

  [ -f "${file}" ] || continue

  set -- "$@" "${file}"
done

[ "$#" -gt 0 ] || exit 0

vale --output=line --minAlertLevel=error "$@" >&2 || exit 2
