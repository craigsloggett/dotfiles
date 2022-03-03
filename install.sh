#!/bin/sh
#
# install dot files.

_zsh() {
	# Setup directories.
	mkdir -p "${XDG_CONFIG_HOME:-${HOME}/.config}"
	mkdir -p "${XDG_DATA_HOME:-${HOME}/.local/share}/zsh"

	# Update permissions on existing system files.
	chmod 755 /usr/local/share/zsh
	chmod 755 /usr/local/share/zsh/site-functions

	# Create the /etc/zshenv file to specify $ZDOTDIR.
	printf '%s\n' "Writing to /etc/zshenv using sudo..."
	cat <<- 'EOF' | sudo tee /etc/zshenv > /dev/null
	# /etc/zshenv: system-wide .zshenv file for zsh(1).
	#
	# This file is sourced on all invocations of the shell.
	# If the -f flag is present or if the NO_RCS option is
	# set within this file, all other initialization files
	# are skipped.
	#
	# This file should contain commands to set the command
	# search path, plus other important environment variables.
	# This file should not contain commands that produce
	# output or assume the shell is attached to a tty.
	#
	# Global Order: zshenv, zprofile, zshrc, zlogin
	
	# Use XDG Base Directory Specification
	export ZDOTDIR="${XDG_CONFIG_HOME:-${HOME}/.config}/zsh"
	EOF
	
	# Get the full path of the current working directory.
	dirname="$(cd "${0%/*}" && printf '%s\n' "${PWD}")"

	# Symlink the dotfiles source directory to $ZDOTDIR.
	if [ ! -e "${XDG_CONFIG_HOME}/zsh" ]; then
		if [ -d "${dirname}/zsh" ]; then
			ln -s "${dirname}/zsh" "${XDG_CONFIG_HOME:-${HOME}/.config}/zsh"
		fi
	fi

	# Cleanup
	# TODO: Preserve existing files and merge/prompt.
	# TODO: Set history file to new location before deleting.
	rm -f "${HOME}/.zsh_history"
	rm -f "${HOME}/.zcompdump"
	rm -f "${HOME}/.zprofile"
	rm -f "${HOME}/.zshrc"
	rm -rf "${HOME}/.zsh_sessions"
	rm -rf "${XDG_CONFIG_HOME:-${HOME}/.config}/zsh/.zsh_sessions"
}

_zsh
