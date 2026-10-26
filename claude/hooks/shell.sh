#!/bin/sh
#
# hooks/shell.sh
#
# Format and lint the shell files among the given paths.

set -euf

for utility in shellcheck shfmt; do
  command -v "${utility}" >/dev/null 2>&1 || exit 0
done

[ "$#" -gt 0 ] || exit 0

files="$(shfmt -f --apply-ignore "$@" 2>/dev/null || :)"

[ -n "${files}" ] || exit 0

printf '%s\n' "${files}" | xargs shfmt -w >&2 || exit 2
printf '%s\n' "${files}" | xargs shellcheck -x >&2 || exit 2
