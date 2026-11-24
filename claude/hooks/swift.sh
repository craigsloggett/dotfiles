#!/bin/sh
#
# hooks/swift.sh
#
# Format and lint the Swift files among the given paths.

set -euf

for utility in swiftformat swiftlint; do
  command -v "${utility}" >/dev/null 2>&1 || exit 0
done

for file in "$@"; do
  shift

  case ${file} in
    *.swift) ;;
    *) continue ;;
  esac

  [ -f "${file}" ] || continue

  set -- "$@" "${file}"
done

[ "$#" -gt 0 ] || exit 0

swiftformat --quiet "$@" >&2 || exit 2
swiftlint lint --quiet --strict --force-exclude "$@" >&2 || exit 2
