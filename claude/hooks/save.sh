#!/bin/sh
#
# hooks/save.sh
#
# A PostToolUse hook that acts on files changed in the working tree.
# The changed set comes from git to catch changes from both Edit/Write
# and Bash. Every change is passed to each handler script, which picks
# out its own filetype. A failed check exits with status 2, the
# "blocking error" status that Claude Code feeds back to the model.

set -euf

command -v jq >/dev/null 2>&1 || exit 0

cd "$(jq -r .cwd)"
root="$(git rev-parse --show-toplevel 2>/dev/null)" || exit 0
cd "${root}"

changed="$({
  git diff --name-only HEAD
  git ls-files -o --exclude-standard
})"

status=0
for type in shell json; do
  printf '%s\n' "${changed}" | xargs "${0%/*}/${type}.sh" || status=2
done
exit "${status}"
