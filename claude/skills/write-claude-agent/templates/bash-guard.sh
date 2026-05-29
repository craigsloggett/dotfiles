#!/bin/sh
#
# bash-guard.sh
#
# PreToolUse(Bash) guard for a read-only auditor subagent. Copy this next to the
# agent that references it and tune the patterns below for that auditor.
#
# Why this exists: disallowedTools: Write, Edit blocks the Write/Edit tools but
# leaves Bash untouched, so an auditor with Bash can still mutate the repo
# (git commit, rm, output redirects, sed -i). This guard inspects the proposed
# command and exits 2 to reject mutations. On a PreToolUse hook, exit 2 blocks
# the call and feeds stderr back to the agent as the reason; exit 0 lets the
# normal permission flow continue.

set -euf

command -v jq >/dev/null 2>&1 || exit 0

cmd="$(jq -r '.tool_input.command // empty')"
readonly cmd

[ -n "${cmd}" ] || exit 0

deny() {
  reason="$1"
  printf 'Blocked: %s This auditor is read-only.\n' "${reason}" >&2
  exit 2
}

# Mutating git subcommands. git diff/log/show/status and friends pass through.
if printf '%s' "${cmd}" |
  grep -Eq '(^|[^[:alnum:]_-])git[[:space:]]+(commit|push|add|reset|restore|stash|merge|rebase|tag|am|apply|cherry-pick|revert|clean|mv|rm)([[:space:]]|$)'; then
  deny 'git command would modify the repository or history.'
fi

# Filesystem mutators.
if printf '%s' "${cmd}" |
  grep -Eq '(^|[^[:alnum:]_-])(rm|rmdir|mv|truncate|tee|dd|shred|install)([[:space:]]|$)'; then
  deny 'command would delete or overwrite files.'
fi

# In-place edit flags. grep -i (case-insensitive read) is deliberately not
# matched; perl's combined forms (perl -pi) need their own pattern if used.
if printf '%s' "${cmd}" |
  grep -Eq '(^|[^[:alnum:]_-])(sed|perl|gawk)[[:space:]]([^|;&]*[[:space:]])?(-i|--in-place)([[:space:]]|=|$)'; then
  deny 'in-place edit flag would rewrite a file.'
fi

# Output redirects to a file. Strip fd duplications (2>&1) and the read-safe
# /dev/null and /dev/stderr targets first; any remaining > writes to a file.
stripped="$(
  printf '%s' "${cmd}" |
    sed -e 's/[0-9]*>&[0-9-]*//g' \
      -e 's@[0-9]*>>\{0,1\}[[:space:]]*/dev/null@@g' \
      -e 's@[0-9]*>>\{0,1\}[[:space:]]*/dev/stderr@@g'
)"
if printf '%s' "${stripped}" | grep -q '>'; then
  deny 'output redirect would write to a file.'
fi

exit 0
