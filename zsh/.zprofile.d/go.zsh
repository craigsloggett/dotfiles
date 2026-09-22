#
# $ZDOTDIR/.zprofile.d/go.zsh
#

export GOPATH="${XDG_DATA_HOME}/go"
export GOBIN="${XDG_BIN_HOME}"
export GOMODCACHE="${XDG_CACHE_HOME}/go/mod"
export GOCACHE="${XDG_CACHE_HOME}/go/build"
export GOENV="${XDG_CONFIG_HOME}/go/env"

path+=("${GOPATH}/bin")
