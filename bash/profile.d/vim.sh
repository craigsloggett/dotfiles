# shellcheck disable=SC2155,SC2148
#
# ${XDG_CONFIG_HOME}/bash/profile.d/vim.sh
#

export VIMINIT='let $MYVIMRC="${XDG_CONFIG_HOME}/vim/vimrc" | source ${MYVIMRC}'
