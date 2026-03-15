#!/bin/sh
#
# shell-lint.sh - run shellcheck on modified shell scripts at session end
#
# Called as a Stop hook. Finds shell scripts that have been
# modified in the current git working tree and runs shellcheck
# on them.

set -u

if ! command -v shellcheck >/dev/null 2>&1; then
  exit 0
fi

if ! command -v git >/dev/null 2>&1; then
  exit 0
fi

# Only run in git repositories.
if ! git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  exit 0
fi

# Find modified shell scripts (staged + unstaged).
files="$(git diff --name-only --diff-filter=ACMR HEAD -- '*.sh' 2>/dev/null)"

# Also check files without extensions that have a shell shebang.
for f in $(git diff --name-only --diff-filter=ACMR HEAD 2>/dev/null); do
  if [ -f "${f}" ] && head -1 "${f}" 2>/dev/null | grep -q '^#!/bin/sh'; then
    files="$(printf '%s\n%s' "${files}" "${f}")"
  fi
done

# Deduplicate and filter to existing files.
files="$(printf '%s\n' "${files}" | sort -u | while read -r f; do
  if [ -n "${f}" ] && [ -f "${f}" ]; then
    printf '%s\n' "${f}"
  fi
done)"

if [ -z "${files}" ]; then
  exit 0
fi

printf '%s\n' "${files}" | xargs shellcheck

exit 0
