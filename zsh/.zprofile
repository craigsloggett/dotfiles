#
# $ZDOTDIR/.zprofile
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
path+=("${XDG_BIN_HOME}")

# Utility specific environment variables.
if [ -d "${ZDOTDIR}/.zprofile.d" ]; then
  # Homebrew is sourced first to find utilities installed by Homebrew.
  brew_zsh="${ZDOTDIR}/.zprofile.d/brew.zsh"
  [ -f "${brew_zsh}" ] && source "${brew_zsh}"

  # Similarly, rustup provides binaries as well.
  rustup_zsh="${ZDOTDIR}/.zprofile.d/rustup.zsh"
  [ -f "${rustup_zsh}" ] && source "${rustup_zsh}"

  for file in "${ZDOTDIR}/.zprofile.d/"*.zsh; do
    [ -f "${file}" ] || continue

    basename="${file##*/}"
    util="${basename%.zsh}"

    if command -v "${util}" >/dev/null; then
      source "${file}"

      # Add any completions for this command, if they exist.
      if [ -d "${ZDOTDIR}/.zfunctions/completions/${util}" ]; then
        fpath+=("${ZDOTDIR}/.zfunctions/completions/${util}")
      fi
    fi
  done
fi
