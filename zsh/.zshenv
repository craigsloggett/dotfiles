#
# $ZDOTDIR/.zshenv
#

# XDG Base Directory Specification variables.
export XDG_CONFIG_HOME="${XDG_CONFIG_HOME:-${HOME}/.config}"
export XDG_CACHE_HOME="${XDG_CACHE_HOME:-${HOME}/.cache}"
export XDG_DATA_HOME="${XDG_DATA_HOME:-${HOME}/.local/share}"
export XDG_STATE_HOME="${XDG_STATE_HOME:-${HOME}/.local/state}"
export XDG_BIN_HOME="${XDG_BIN_HOME:-${HOME}/.local/bin}"

# If enabled, Apple's Terminal will create session files in 
# $ZDOTDIR/.zsh_sessions.
export SHELL_SESSIONS_DISABLE=1

# Add XDG_BIN_HOME to PATH variable.
typeset -U path
path=("${XDG_BIN_HOME}" $path)

# Homebrew must be sourced first to get the path.
source "${ZDOTDIR}/.zshenv.d/brew.zsh"

# Utility specific environment variables.
for util in brew vim gpg pass; do
	if command -v "${util}" > /dev/null; then
		source "${ZDOTDIR}/.zshenv.d/${util}.zsh"
	fi
done
