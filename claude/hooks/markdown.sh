#!/bin/sh
#
# hooks/markdown.sh
#
# Format and lint the Markdown files among the given paths.

set -euf

command -v rumdl >/dev/null 2>&1 || exit 0

for file in "$@"; do
  shift

  case ${file} in
    *.md) ;;
    *) continue ;;
  esac

  [ -f "${file}" ] || continue

  set -- "$@" "${file}"
done

[ "$#" -gt 0 ] || exit 0

rumdl fmt --silent "$@" >&2 || exit 2
rumdl check "$@" >&2 || exit 2
