#!/bin/sh
#
# statusline-command.sh
#
# Render the Claude Code status line

set -euf

STATUSLINE_INPUT="$(cat)"
readonly STATUSLINE_INPUT

check_prerequisites() {
  command -v jq >/dev/null 2>&1
}

main() {
  check_prerequisites || return 0

  model_display_name="$(printf '%s' "${STATUSLINE_INPUT}" | jq -r '.model.display_name // empty')"
  context_remaining="$(printf '%s' "${STATUSLINE_INPUT}" | jq -r '.context_window.remaining_percentage // 100')"
  workspace_directory="$(printf '%s' "${STATUSLINE_INPUT}" | jq -r '.workspace.current_dir // empty')"
  short_workspace_directory="$(printf '%s' "${workspace_directory}" | sed "s|^${HOME}|~|")"

  effort_level=""
  settings="${HOME}/.claude/settings.json"
  if [ -f "${settings}" ]; then
    effort_level="$(jq -r '.effortLevel // empty' "${settings}" 2>/dev/null)"
  fi

  statusline=""
  statusline="${model_display_name}"
  statusline="${statusline} · ${effort_level}"
  statusline="${statusline} · ${context_remaining}% left"
  statusline="${statusline} · ${short_workspace_directory}"

  printf '%s' "${statusline}"
}

main "$@"
