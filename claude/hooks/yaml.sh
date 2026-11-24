#!/bin/sh
#
# hooks/yaml.sh
#
# Format and lint the YAML files among the given paths.

set -euf

for utility in yamlfmt yamllint; do
  command -v "${utility}" >/dev/null 2>&1 || exit 0
done

for file in "$@"; do
  shift

  case ${file} in
    *.yaml | *.yml | .yamlfmt | */.yamlfmt) ;;
    *) continue ;;
  esac

  [ -f "${file}" ] || continue

  set -- "$@" "${file}"
done

[ "$#" -gt 0 ] || exit 0

yamlfmt "$@" >&2 || exit 2
yamllint "$@" >&2 || exit 2
