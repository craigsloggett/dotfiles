#!/bin/sh
#
# hooks/prose.sh
#
# Lint the prose in the Markdown and Go files among the given paths.
# Only an error-level alert fails the check.

set -euf

command -v vale >/dev/null 2>&1 || exit 0

files=""
for file in "$@"; do
  case ${file} in
    *.md | *.go) ;;
    *) continue ;;
  esac

  [ -f "${file}" ] || continue

  files="${files}${file}
"
done

[ -n "${files}" ] || exit 0

printf '%s' "${files}" | xargs vale --output=line --minAlertLevel=error >&2 || exit 2
