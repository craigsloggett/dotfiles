#!/bin/sh
#
# shell-lint.sh - run shellcheck on edited shell scripts before stopping
#
# Called as a Stop hook. Reads the list of .sh files edited during
# the session (tracked by format.sh) and runs shellcheck on them.
# Blocks the agent from stopping if issues are found so it can
# address them.

set -u

if ! command -v shellcheck >/dev/null 2>&1; then
  exit 0
fi

if ! command -v jq >/dev/null 2>&1; then
  exit 0
fi

# Read hook input from stdin.
input="$(cat)"

# Avoid infinite loops: if the agent already continued from a
# previous Stop hook, let it stop this time.
stop_hook_active="$(printf '%s\n' "${input}" | jq -r '.stop_hook_active // false')"
if [ "${stop_hook_active}" = "true" ]; then
  exit 0
fi

session_id="$(printf '%s\n' "${input}" | jq -r '.session_id // empty')"
if [ -z "${session_id}" ]; then
  exit 0
fi

# Read the list of edited shell scripts tracked by format.sh.
state_dir="${XDG_STATE_HOME:-${HOME}/.local/state}/claude"
state_file="${state_dir}/edited-sh-${session_id}"

if [ ! -f "${state_file}" ]; then
  exit 0
fi

# Deduplicate the file list.
files="$(sort -u "${state_file}" | sed '/^$/d')"

if [ -z "${files}" ]; then
  exit 0
fi

# Run shellcheck. If issues are found, block so the agent can fix them.
output="$(printf '%s\n' "${files}" | xargs shellcheck 2>&1)"

if [ -n "${output}" ]; then
  printf '%s\n' "${output}" >&2
  exit 2
fi

exit 0
