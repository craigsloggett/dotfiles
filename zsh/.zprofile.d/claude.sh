# shellcheck shell=sh

export CLAUDE_CONFIG_DIR="${XDG_CONFIG_HOME}/claude"
export CLAUDE_CODE_PLUGIN_CACHE_DIR="${XDG_DATA_HOME}/claude/plugins"
export CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC=1

if [ -n "${TMPDIR:-}" ]; then
  export CLAUDE_CODE_TMPDIR="${TMPDIR%/}"
fi
