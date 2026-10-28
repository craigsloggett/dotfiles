claude() {
  local config_dir
  config_dir="$(git config --type=path --get claude.configDir 2>/dev/null)"
  config_dir="${config_dir:-${CLAUDE_CONFIG_DIR}}"

  local -a options
  options=(
    --strict-mcp-config
    --mcp-config="${config_dir}/profile/mcp.json"
    --settings="${config_dir}/profile/settings.json"
    --plugin-dir="${config_dir}/profile/plugins"
    --setting-sources=user,local
  )

  CLAUDE_CONFIG_DIR="${config_dir}" command claude "${options[@]}" "$@"
}
