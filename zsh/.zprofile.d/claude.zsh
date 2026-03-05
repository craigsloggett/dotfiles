#
# $ZDOTDIR/.zprofile.d/claude.zsh
#

# Claude Code does not respect XDG Base Directory Specification.
# https://github.com/anthropics/claude-code/issues/1455
#
# Subdirectories inside ~/.claude are symlinked to XDG locations
# by the install script. See install:_claude() for details.
