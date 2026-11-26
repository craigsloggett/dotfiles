#!/bin/sh
#
# hooks/prose.sh
#
# Lint the prose in the Markdown, Go, and shell files among the given
# paths. Only an error-level alert fails the check.

set -euf

command -v vale >/dev/null 2>&1 || exit 0

[ "$#" -gt 0 ] || exit 0

if command -v shfmt >/dev/null 2>&1; then
  scripts="$(shfmt -f --apply-ignore "$@" 2>/dev/null || :)"

  IFS='
'

  for file in ${scripts}; do
    if ! output="$(vale --output=line --minAlertLevel=error --ext=.sh <"${file}")"; then
      printf '%s\n' "${output}" | sed "s|^stdin\.sh:|${file}:|" >&2
      exit 2
    fi
  done
fi

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
