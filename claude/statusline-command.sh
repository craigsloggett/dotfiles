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

  now="$(date +%s)"
  model_display_name="$(printf '%s' "${STATUSLINE_INPUT}" | jq -r '.model.display_name // empty')"
  context_remaining="$(printf '%s' "${STATUSLINE_INPUT}" | jq -r '.context_window.remaining_percentage // 100')"
  workspace_directory="$(printf '%s' "${STATUSLINE_INPUT}" | jq -r '.workspace.current_dir // empty')"
  short_workspace_directory="$(printf '%s' "${workspace_directory}" | sed "s|^${HOME}|~|")"
  five_hour_used="$(printf '%s' "${STATUSLINE_INPUT}" | jq -r '.rate_limits.five_hour.used_percentage // empty')"
  five_hour_resets_at="$(printf '%s' "${STATUSLINE_INPUT}" | jq -r '.rate_limits.five_hour.resets_at // empty')"
  five_hour_minutes_until_reset=$(((five_hour_resets_at - now) / 60))
  seven_day_used="$(printf '%s' "${STATUSLINE_INPUT}" | jq -r '.rate_limits.seven_day.used_percentage // empty')"
  seven_day_resets_at="$(printf '%s' "${STATUSLINE_INPUT}" | jq -r '.rate_limits.seven_day.resets_at // empty')"
  seven_day_hours_until_reset=$(((seven_day_resets_at - now) / 3600))

  effort_level=""
  settings="${HOME}/.claude/settings.json"
  if [ -f "${settings}" ]; then
    effort_level="$(jq -r '.effortLevel // empty' "${settings}" 2>/dev/null)"
  fi

  statusline=""
  statusline="${model_display_name}"
  statusline="${statusline} · ${effort_level}"
  statusline="${statusline} · ${context_remaining}% left"
  statusline="${statusline} · 5h: $(printf '%.0f' "${five_hour_used}")% (${five_hour_minutes_until_reset}m)"
  statusline="${statusline} · 7d: $(printf '%.0f' "${seven_day_used}")% (${seven_day_hours_until_reset}h)"
  statusline="${statusline} · ${short_workspace_directory}"

  printf '%s' "${statusline}"
}

main "$@"
