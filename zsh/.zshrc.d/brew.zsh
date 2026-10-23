brew-update() {
  brew update
  brew bundle upgrade --global
  brew bundle cleanup --global --force
  brew autoremove
  brew cleanup --prune=all
  brew bundle check --global
}
