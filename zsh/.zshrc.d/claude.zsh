claude() {
  local config_dir setting_sources repo_root

  config_dir="$(git config --type=path --get-urlmatch claude.configDir "file://${PWD}" 2>/dev/null)"
  config_dir="${config_dir:-${CLAUDE_CONFIG_DIR}}"

  setting_sources="$(git config --get-urlmatch claude.settingSources "file://${PWD}" 2>/dev/null)"
  setting_sources="${setting_sources:-user,local}"

  repo_root="$(git rev-parse --path-format=absolute --git-common-dir 2>/dev/null)"
  repo_root="${repo_root%/.git}"

  local -a options
  options=(
    --mcp-config="${config_dir}/profile/mcp.json"
    --settings="${config_dir}/profile/settings.json"
    --plugin-dir="${config_dir}/profile/plugins"
    --setting-sources="${setting_sources}"
  )

  if [ -n "${repo_root}" ] && [ -f "${repo_root}/.claude/local/.claude-plugin/plugin.json" ]; then
    options+=(--plugin-dir="${repo_root}/.claude/local")
  fi

  CLAUDE_CONFIG_DIR="${config_dir}" command claude "${options[@]}" "$@"
}
