#!/bin/sh
#
# hooks/swift.sh
#
# Format and lint the Swift files among the given paths.

set -euf

for utility in swiftformat swiftlint; do
  command -v "${utility}" >/dev/null 2>&1 || exit 0
done

files=""
for file in "$@"; do
  case ${file} in
    *.swift) ;;
    *) continue ;;
  esac

  [ -f "${file}" ] || continue

  files="${files}${file}
"
done

[ -n "${files}" ] || exit 0

printf '%s' "${files}" | xargs swiftformat --quiet >&2 || exit 2
printf '%s' "${files}" | xargs swiftlint lint --quiet --strict --force-exclude >&2 || exit 2
