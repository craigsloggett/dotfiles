#!/bin/sh
#
# hooks/python.sh
#
# Format, lint, and type check the Python files among the given paths.

set -euf

for utility in ruff ty; do
  command -v "${utility}" >/dev/null 2>&1 || exit 0
done

for file in "$@"; do
  shift

  case ${file} in
    *.py | *.pyi) ;;
    *) continue ;;
  esac

  [ -f "${file}" ] || continue

  set -- "$@" "${file}"
done

[ "$#" -gt 0 ] || exit 0

ruff check --fix-only --force-exclude --quiet "$@" >&2 || exit 2
ruff format --force-exclude --quiet "$@" >&2 || exit 2
ruff check --force-exclude --output-format concise --quiet "$@" >&2 || exit 2
ty check --output-format concise "$@" >&2 || exit 2
