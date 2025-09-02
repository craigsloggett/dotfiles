#
# $ZDOTDIR/.zprofile.d/git.zsh
#

# Show git on the right prompt.
setopt PROMPT_SUBST
source "${ZDOTDIR}/.zfunctions/git-prompt"

# Configure which git details to display.
GIT_PS1_SHOWDIRTYSTATE=1
GIT_PS1_SHOWSTASHSTATE=1
GIT_PS1_SHOWUNTRACKEDFILES=1
GIT_PS1_SHOWUPSTREAM="auto"
GIT_PS1_SHOWCOLORHINTS=1

# Configure the right prompt.
export RPROMPT=$'$(__git_ps1 "%s")'
