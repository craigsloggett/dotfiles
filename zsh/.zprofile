#
# $ZDOTDIR/.zprofile
#

export XDG_CONFIG_HOME="${XDG_CONFIG_HOME:-${HOME}/.config}"
export XDG_CACHE_HOME="${XDG_CACHE_HOME:-${HOME}/.cache}"
export XDG_DATA_HOME="${XDG_DATA_HOME:-${HOME}/.local/share}"
export XDG_STATE_HOME="${XDG_STATE_HOME:-${HOME}/.local/state}"
export XDG_BIN_HOME="${XDG_BIN_HOME:-${HOME}/.local/bin}"

export SHELL_SESSIONS_DISABLE=1
export DO_NOT_TRACK=1

typeset -U path
path=(
  /opt/homebrew/bin(N-/)
  /opt/homebrew/sbin(N-/)
  /opt/homebrew/opt/rustup/bin(N-/)
  /Applications/Ghostty.app/Contents/MacOS(N-/)
  $path
  ${XDG_BIN_HOME}(N-/)
)

for file in "${ZDOTDIR}"/.zprofile.d/*.zsh(N); do
  command -v "${file:t:r}" >/dev/null || continue

  source "${file}"
done
