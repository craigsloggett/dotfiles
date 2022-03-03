#
# $ZDOTDIR/.zprofile
#

# XDG Base Directory Specification variables.
export XDG_CONFIG_HOME="${XDG_CONFIG_HOME:-${HOME}/.config}"
export XDG_CACHE_HOME="${XDG_CACHE_HOME:-${HOME}/.cache}"
export XDG_DATA_HOME="${XDG_DATA_HOME:-${HOME}/.local/share}"
export XDG_STATE_HOME="${XDG_STATE_HOME:-${HOME}/.local/state}"
export XDG_BIN_HOME="${XDG_BIN_HOME:-${HOME}/.local/bin}"

# Add XDG_BIN_HOME to PATH variable.
export PATH="${XDG_BIN_HOME}:${PATH}"

# If enabled, Apple's Terminal will create session files in 
# $ZDOTDIR/.zsh_sessions.
export SHELL_SESSIONS_DISABLE=1

# VIM
export VIMINIT='let $MYVIMRC="${XDG_CONFIG_HOME}/vim/vimrc" | source ${MYVIMRC}'
