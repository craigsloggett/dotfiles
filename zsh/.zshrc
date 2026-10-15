fpath+=(
  /opt/homebrew/share/zsh/site-functions(N-/)
  "${ZDOTDIR}"/.zfunctions/completions/*(N-/)
)

autoload -Uz compinit
compinit -d "${XDG_CACHE_HOME}/zsh/zcompdump-${ZSH_VERSION}"

HISTFILE="${XDG_STATE_HOME}/zsh/history"
HISTSIZE=60000
SAVEHIST=50000

setopt EXTENDED_HISTORY
setopt SHARE_HISTORY
setopt APPEND_HISTORY
setopt INC_APPEND_HISTORY
setopt HIST_EXPIRE_DUPS_FIRST
setopt HIST_IGNORE_DUPS
setopt HIST_FIND_NO_DUPS
setopt HIST_REDUCE_BLANKS

autoload -Uz promptinit
promptinit

PROMPT=' %(!.%F{red}%B.%F{green}%B)%b%f %~ %(!.#.$) '

source "${ZDOTDIR}/.zfunctions/zsh-autosuggestions"

source "${ZDOTDIR}/.zfunctions/claude-kkp-reset"
precmd_functions+=(_claude_kkp_reset)

for file in "${ZDOTDIR}"/.zshrc.d/*.zsh(N); do
  command -v "${file:t:r}" >/dev/null || continue

  source "${file}"
done

setopt NO_CASE_GLOB
setopt AUTO_CD

zstyle ':completion:*' cache-path "${XDG_CACHE_HOME}/zsh/zcompcache"
zstyle ':completion:*' special-dirs true
zstyle ':completion:*' list-suffixes
zstyle ':completion:*' expand prefix suffix

autoload edit-command-line
zle -N edit-command-line
bindkey '^Xe' edit-command-line
