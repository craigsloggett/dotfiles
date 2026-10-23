claude() {
  local config_dir
  config_dir="$(git config --type=path --get claude.configDir 2>/dev/null)"
  config_dir="${config_dir:-${CLAUDE_CONFIG_DIR}}"

  CLAUDE_CONFIG_DIR="${config_dir}" command claude --mcp-config="${config_dir}/mcp.json" --strict-mcp-config "$@"
}
