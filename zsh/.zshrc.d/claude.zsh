claude() {
  local config_dir setting_sources settings

  config_dir="$(git config --type=path --get-urlmatch claude.configDir "file://${PWD}" 2>/dev/null)"
  config_dir="${config_dir:-${CLAUDE_CONFIG_DIR}}"

  setting_sources="$(git config --get-urlmatch claude.settingSources "file://${PWD}" 2>/dev/null)"
  setting_sources="${setting_sources:-user,project,local}"

  settings="$(jq -s '.[0] * .[1]' "${config_dir}/settings.json" "${config_dir}/profile/settings.json" 2>/dev/null)"
  settings="${settings:-${config_dir}/profile/settings.json}"

  local -a options
  options=(
    --mcp-config="${config_dir}/profile/mcp.json"
    --settings="${settings}"
    --plugin-dir="${config_dir}/profile/plugins"
    --setting-sources="${setting_sources}"
  )

  CLAUDE_CONFIG_DIR="${config_dir}" command claude "${options[@]}" "$@"
}
