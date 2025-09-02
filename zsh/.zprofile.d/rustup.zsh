#
# $ZDOTDIR/.zprofile.d/rustup.zsh
#

export RUSTUP_HOME="${XDG_DATA_HOME}/rustup"

# Add `rustup` to the PATH variable.
typeset -U path
path=("$(brew --prefix rustup)/bin" $path)
