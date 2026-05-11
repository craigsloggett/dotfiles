# shellcheck shell=sh
#
# ${XDG_CONFIG_HOME}/bash/profile.d/vim.sh
#

# shellcheck disable=SC2016
export VIMINIT='let $MYVIMRC="${XDG_CONFIG_HOME}/vim/vimrc" | source ${MYVIMRC}'
