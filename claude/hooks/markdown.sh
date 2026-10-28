#!/bin/sh
#
# hooks/markdown.sh
#
# Format and lint the Markdown files among the given paths.

set -euf

command -v rumdl >/dev/null 2>&1 || exit 0

files=""
for file in "$@"; do
  case ${file} in
    *.md) ;;
    *) continue ;;
  esac

  [ -f "${file}" ] || continue

  files="${files}${file}
"
done

[ -n "${files}" ] || exit 0

printf '%s' "${files}" | xargs rumdl fmt >&2 || exit 2
printf '%s' "${files}" | xargs rumdl check >&2 || exit 2
