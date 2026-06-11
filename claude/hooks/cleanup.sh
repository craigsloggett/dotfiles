#!/bin/sh
#
# hooks/cleanup.sh
#
# Remove per-session worked-file lists. On SessionStart, sweep lists orphaned by
# sessions that ended without a final Stop (Ctrl+C, terminal close, crash, kill);
# on SessionEnd, drop the ending session's list.

set -euf

HOOK_INPUT="$(cat)"
readonly HOOK_INPUT

readonly MAX_AGE_DAYS=7

check_prerequisites() {
  command -v jq >/dev/null 2>&1 || return 1
}

main() {
  check_prerequisites || return 0

  state_dir="${XDG_STATE_HOME:-${HOME}/.local/state}/claude/worked-files"
  [ -d "${state_dir}" ] || return 0

  hook_event_name="$(printf '%s' "${HOOK_INPUT}" | jq -r '.hook_event_name // empty')"

  case "${hook_event_name}" in
    SessionStart)
      find "${state_dir}" -type f -mtime "+${MAX_AGE_DAYS}" -exec rm -f {} +
      ;;
    SessionEnd)
      exit_reason="$(printf '%s' "${HOOK_INPUT}" | jq -r '.exit_reason // empty')"
      # A resumed session keeps its pending list to lint on its next Stop.
      [ "${exit_reason}" != "resume" ] || return 0
      session_id="$(printf '%s' "${HOOK_INPUT}" | jq -r '.session_id // empty')"
      [ -n "${session_id}" ] || return 0
      rm -f "${state_dir}/${session_id}"
      ;;
  esac
}

main "$@"
