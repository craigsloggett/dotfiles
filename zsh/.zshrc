#
# $ZDOTDIR/.zshrc
#

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
PROMPT=' %(!.%F{red}%B.%F{green}%B)%b%f %~ %(!.#.$) '

# Enable ZSH Auto-suggestions.
source "${ZDOTDIR}/.zfunctions/zsh-autosuggestions"

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

# Turn on Bash like, open the current input in terminal to an editor.
autoload edit-command-line
zle -N edit-command-line
bindkey '^Xe' edit-command-line
