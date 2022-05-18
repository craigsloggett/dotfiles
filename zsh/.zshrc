#
# $ZDOTDIR/.zshrc
#

# Initialize completion.
typeset -U fpath
fpath+=("${XDG_DATA_HOME}/zsh/site-functions/")

# Enable auto completion.
autoload -Uz compinit
compinit -d "${XDG_CACHE_HOME}/zsh/zcompdump-${ZSH_VERSION}"

# Terminal history settings.
HISTFILE="${XDG_STATE_HOME}/zsh/history"
HISTSIZE=60000
SAVEHIST=50000

# Add more data to the history file.
setopt EXTENDED_HISTORY
# Share history across multiple zsh sessions.
setopt SHARE_HISTORY
# Append to history.
setopt APPEND_HISTORY
# Add commands as they are typed, not at shell exit.
setopt INC_APPEND_HISTORY
# Expire duplicates first.
setopt HIST_EXPIRE_DUPS_FIRST
# Do not store duplications.
setopt HIST_IGNORE_DUPS
# Ignore duplicates when searching.
setopt HIST_FIND_NO_DUPS
# Removes blank lines from history.
setopt HIST_REDUCE_BLANKS

# Load the prompt theme system.
autoload -Uz promptinit
promptinit

# Configure the left prompt.
PROMPT=' %(!.%F{red}%B.%F{green}%B)%b%f %1~ %(!.#.$) '

# Show git on the right prompt.
setopt PROMPT_SUBST
source "${ZDOTDIR}/plugin/git-prompt.zsh"

# Enable ZSH Auto-suggestions.
source "${ZDOTDIR}/plugin/zsh-autosuggestions.zsh"

# Configure which git details to display.
GIT_PS1_SHOWDIRTYSTATE=1
GIT_PS1_SHOWSTASHSTATE=1
GIT_PS1_SHOWUNTRACKEDFILES=1
GIT_PS1_SHOWUPSTREAM="auto"
GIT_PS1_SHOWCOLORHINTS=1

# Configure the right prompt.
export RPROMPT=$'$(__git_ps1 "%s")'

# Source the alias file.
source "${ZDOTDIR}/aliases"

# Turn on case insensitive globbing.
setopt NO_CASE_GLOB

# Turn on Auto CD.
setopt AUTO_CD

# Turn on partial completion suggestions.
zstyle ':completion:*' cache-path "${XDG_CACHE_HOME}/zsh/zcompcache"
zstyle ':completion:*' special-dirs true
zstyle ':completion:*' list-suffixes
zstyle ':completion:*' expand prefix suffix

# Turn on any custom completions.
if [ -d "${ZDOTDIR}/completions" ]; then
	for file in "${ZDOTDIR}/completions/"*.zsh-completion; do
		[ -f "${file}" ] || continue

		basename="${file##*/}"
		util="${basename%.zsh-completion}"

		if command -v "${util}" > /dev/null; then
			source "${file}"
		fi
	done
fi
