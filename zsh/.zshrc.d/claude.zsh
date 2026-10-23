claude() {
  local config_dir
  claude_config_dir="$(git config --type=path --get claude.configDir 2>/dev/null)"

  CLAUDE_CONFIG_DIR="${claude_config_dir:-${CLAUDE_CONFIG_DIR}}" command claude "$@"
}
