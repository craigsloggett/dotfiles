#
# $ZDOTDIR/.zshenv.d/brew.zsh
#

# Check if Homebrew was installed in /opt (M1).
if [ -d "/opt/homebrew/bin" ]; then
  homebrew_dir="/opt/homebrew/bin"
else
  homebrew_dir="/usr/local/bin"
fi

# Add Homebrew to the PATH variable.
typeset -U path
path=("${homebrew_dir}" $path)
