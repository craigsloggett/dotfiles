#!/bin/sh
#
# go-fix.sh - run Go analysis and auto-fix tools before stopping
#
# Called as a Stop hook. Reads the list of .go files edited during
# the session (tracked by go-fmt.sh), finds their module roots,
# and runs go fix and go vet in each. Blocks the agent from
# stopping if go vet reports issues so it can address them.

set -u

if ! command -v go >/dev/null 2>&1; then
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

# Read the list of edited Go files tracked by go-fmt.sh.
state_dir="${XDG_STATE_HOME:-${HOME}/.local/state}/claude"
state_file="${state_dir}/edited-go-${session_id}"

if [ ! -f "${state_file}" ]; then
  exit 0
fi

# Find unique module roots from edited file paths.
module_roots=""
while read -r f; do
  [ -z "${f}" ] && continue
  dir="$(dirname "${f}")"
  while [ "${dir}" != "/" ]; do
    if [ -f "${dir}/go.mod" ]; then
      module_roots="$(printf '%s\n%s' "${module_roots}" "${dir}")"
      break
    fi
    dir="$(dirname "${dir}")"
  done
done <"${state_file}"

module_roots="$(printf '%s\n' "${module_roots}" | sort -u | sed '/^$/d')"

if [ -z "${module_roots}" ]; then
  exit 0
fi

# Run go fix and go vet in each module root.
all_output=""
printf '%s\n' "${module_roots}" | while read -r root; do
  cd "${root}" && go fix ./... 2>/dev/null
done

while read -r root; do
  output="$(cd "${root}" && go vet ./... 2>&1)"
  if [ -n "${output}" ]; then
    all_output="$(printf '%s\n%s' "${all_output}" "${output}")"
  fi
done <<EOF
${module_roots}
EOF

if [ -n "${all_output}" ]; then
  printf '%s\n' "${all_output}"
  exit 2
fi

exit 0
