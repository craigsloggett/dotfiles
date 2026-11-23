#!/bin/sh
#
# hooks/vale.sh
#
# Lint the prose in the Markdown and Go files among the given paths.
# Report an alert when its line differs from HEAD, and skip the rest so
# a change does not have to fix prose it left alone.

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

alerts="$(
  printf '%s' "${files}" |
    xargs vale --output=line --no-exit --minAlertLevel=warning
)" || exit 2

[ -n "${alerts}" ] || exit 0

# The diff comes first and the alerts follow an empty line. A diff
# without context lines never contains an empty line.
{
  printf '%s' "${files}" | xargs git diff --unified=0 HEAD -- 2>/dev/null || :
  printf '\n%s\n' "${alerts}"
} | awk -F: '
  /^$/ { in_alerts = 1; next }                 # The empty line ends the diff.
  !in_alerts && sub(/^\+\+\+ b\//, "") {       # A tracked file opens its hunks.
    file = $0
    tracked[file] = 1
  }
  !in_alerts && /^@@ / {                       # @@ -old +start,count @@
    split($0, hunk, " ")
    count = split(hunk[3], added, ",") == 2 ? added[2] : 1
    start = substr(added[1], 2) + 0
    for (line = start; line < start + count; line++) changed[file, line] = 1
  }
  !in_alerts { next }
  !($1 in tracked) || ($1, $2) in changed {    # path:line:column:rule:message
    print
    found = 1
  }
  END { exit found ? 2 : 0 }
' >&2 || exit 2
