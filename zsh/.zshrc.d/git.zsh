[[ -r /opt/homebrew/etc/bash_completion.d/git-prompt.sh ]] || return

setopt PROMPT_SUBST
source /opt/homebrew/etc/bash_completion.d/git-prompt.sh

GIT_PS1_SHOWDIRTYSTATE=1
GIT_PS1_SHOWSTASHSTATE=1
GIT_PS1_SHOWUNTRACKEDFILES=1
GIT_PS1_SHOWUPSTREAM="auto"
GIT_PS1_SHOWCOLORHINTS=1

RPROMPT=$'$(__git_ps1 "%s")'
