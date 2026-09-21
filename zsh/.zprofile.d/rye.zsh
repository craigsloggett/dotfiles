#
# $ZDOTDIR/.zprofile.d/rye.zsh
#

export RYE_HOME="${XDG_DATA_HOME}/rye"

[ -f "${RYE_HOME}/env" ] && . "${RYE_HOME}/env"
