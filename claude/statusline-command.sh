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

format_duration() {
  total_seconds="$1"

  if [ "${total_seconds}" -lt 0 ]; then
    total_seconds=0
  fi

  if [ "${total_seconds}" -lt 3600 ]; then
    printf '%dm' "$((total_seconds / 60))"
  elif [ "${total_seconds}" -lt 86400 ]; then
    printf '%dh' "$((total_seconds / 3600))"
  else
    printf '%dd' "$((total_seconds / 86400))"
  fi
}

main() {
  check_prerequisites || return 0

  now="$(date +%s)"
  settings="${HOME}/.claude/settings.json"
  effort_level="$(jq -r '.effortLevel // empty' "${settings}" 2>/dev/null)"

  model_display_name="$(printf '%s' "${STATUSLINE_INPUT}" | jq -r '.model.display_name // empty')"
  context_remaining="$(printf '%s' "${STATUSLINE_INPUT}" | jq -r '.context_window.remaining_percentage // 100')"

  workspace_directory="$(printf '%s' "${STATUSLINE_INPUT}" | jq -r '.workspace.current_dir // empty')"
  short_workspace_directory="$(printf '%s' "${workspace_directory}" | sed "s|^${HOME}|~|")"

  five_hour_used="$(printf '%s' "${STATUSLINE_INPUT}" | jq -r '.rate_limits.five_hour.used_percentage // empty')"
  five_hour_resets_at="$(printf '%s' "${STATUSLINE_INPUT}" | jq -r '.rate_limits.five_hour.resets_at // empty')"

  seven_day_used="$(printf '%s' "${STATUSLINE_INPUT}" | jq -r '.rate_limits.seven_day.used_percentage // empty')"
  seven_day_resets_at="$(printf '%s' "${STATUSLINE_INPUT}" | jq -r '.rate_limits.seven_day.resets_at // empty')"

  statusline="${model_display_name}"
  statusline="${statusline} · $((100 - context_remaining))%"
  statusline="${statusline} · ${effort_level}"

  if [ -n "${five_hour_used}" ] && [ -n "${five_hour_resets_at}" ]; then
    five_hour_reset_in="$(format_duration $((five_hour_resets_at - now)))"
    statusline="${statusline} · 5h $(printf '%.0f' "${five_hour_used}")% (${five_hour_reset_in})"
  fi

  if [ -n "${seven_day_used}" ] && [ -n "${seven_day_resets_at}" ]; then
    seven_day_reset_in="$(format_duration $((seven_day_resets_at - now)))"
    statusline="${statusline} · 7d $(printf '%.0f' "${seven_day_used}")% (${seven_day_reset_in})"
  fi

  statusline="${statusline} · ${short_workspace_directory}"

  printf '%s' "${statusline}"
}

main "$@"
