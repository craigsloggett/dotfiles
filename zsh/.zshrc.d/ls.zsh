alias ls='ls -G'
alias lsa='ls -la | head -n 1 && CLICOLOR_FORCE=1 ls -la | grep '^d' && CLICOLOR_FORCE=1 ls -la | grep -v '^d' | tail -n +2'
