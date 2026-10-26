#!/bin/sh
#
# hooks/yaml.sh
#
# Format and lint the YAML files among the given paths.

set -euf

for utility in yamlfmt yamllint; do
  command -v "${utility}" >/dev/null 2>&1 || exit 0
done

files=""
for file in "$@"; do
  case ${file} in
    *.yaml | *.yml | .yamlfmt | */.yamlfmt) ;;
    *) continue ;;
  esac

  [ -f "${file}" ] || continue

  files="${files}${file}
"
done

[ -n "${files}" ] || exit 0

printf '%s' "${files}" | xargs yamlfmt >&2 || exit 2
printf '%s' "${files}" | xargs yamllint >&2 || exit 2
