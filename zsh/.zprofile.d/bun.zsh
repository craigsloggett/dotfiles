#
# $ZDOTDIR/.zprofile.d/bun.zsh
#

export BUN_INSTALL="${XDG_DATA_HOME}/bun"
export BUN_CREATE_DIR="${XDG_DATA_HOME}/bun/create"

# BUN_INSTALL also roots the package cache, which belongs in XDG_CACHE_HOME.
export BUN_INSTALL_CACHE_DIR="${XDG_CACHE_HOME}/bun/install"

# Add globally installed package binaries to the PATH variable.
path+=("${BUN_INSTALL}/bin")

# Disable crash report uploads.
export DO_NOT_TRACK=1
