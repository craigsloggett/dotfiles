#
# $ZDOTDIR/.zprofile.d/brew.zsh
#

# Add site-functions that come with Homebrew.
brew_fpath="$(brew --prefix)/share/zsh/site-functions"
[ -d "${brew_fpath}" ] && fpath+=("${brew_fpath}")

export HOMEBREW_NO_ANALYTICS=1
