#!/bin/sh
#
# hooks/go.sh
#
# Format and lint the Go files among the given paths.

set -euf

command -v golangci-lint >/dev/null 2>&1 || exit 0

files=""
for file in "$@"; do
  case ${file} in
    *.go) ;;
    *) continue ;;
  esac

  [ -f "${file}" ] || continue

  files="${files}${file}
"
done

[ -n "${files}" ] || exit 0

printf '%s' "${files}" | xargs golangci-lint fmt >&2 || exit 2

directories="$(printf '%s' "${files}" | xargs -n1 dirname | sort -u)"

status=0
for directory in ${directories}; do
  (cd "${directory}" && golangci-lint run --path-mode=abs .) >&2 || status=2
done
exit "${status}"
