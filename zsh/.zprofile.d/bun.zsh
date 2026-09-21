#
# $ZDOTDIR/.zprofile.d/bun.zsh
#

export BUN_INSTALL="${XDG_DATA_HOME}/bun"
export BUN_CREATE_DIR="${XDG_DATA_HOME}/bun/create"
export BUN_INSTALL_CACHE_DIR="${XDG_CACHE_HOME}/bun/install"

# Add globally installed package binaries to the PATH variable.
path+=("${BUN_INSTALL}/bin")
