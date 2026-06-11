#!/bin/sh
#
# hooks/track.sh
#
# Record edited files on PostToolUse so the Stop hook can lint only those.

set -euf

HOOK_INPUT="$(cat)"
readonly HOOK_INPUT

check_prerequisites() {
  command -v jq >/dev/null 2>&1 || return 1
}

main() {
  check_prerequisites || return 0

  file_path="$(printf '%s' "${HOOK_INPUT}" | jq -r '.tool_input.file_path // empty')"
  session_id="$(printf '%s' "${HOOK_INPUT}" | jq -r '.session_id // empty')"

  [ -n "${file_path}" ] || return 0
  [ -n "${session_id}" ] || return 0

  state_dir="${XDG_STATE_HOME:-${HOME}/.local/state}/claude/worked-files"
  mkdir -p "${state_dir}"

  printf '%s\n' "${file_path}" >>"${state_dir}/${session_id}"
}

main "$@"
