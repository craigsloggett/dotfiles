#!/bin/sh
#
# install dot files

# Global Variables
: "${XDG_CONFIG_HOME:=${HOME}/.config}"
: "${XDG_CACHE_HOME:=${HOME}/.cache}"
: "${XDG_STATE_HOME:=${HOME}/.local/state}"
: "${XDG_DATA_HOME:=${HOME}/.local/share}"

_zsh() {
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
	
	# Setup directories.
	mkdir -p "${XDG_CONFIG_HOME}"
	mkdir -p "${XDG_CACHE_HOME}/zsh"
	mkdir -p "${XDG_STATE_HOME}/zsh"

	# Update permissions on existing system files.
	if [ -d /usr/local/share/zsh ]; then
		chmod 755 /usr/local/share/zsh
		chmod 755 /usr/local/share/zsh/site-functions
	fi

	# Get the full path of the current working directory.
	dirname="$(cd "${0%/*}" && printf '%s\n' "${PWD}")"

	# TODO: DRY: Pull this out into a function.
	# Symlink the dotfiles source directory to $ZDOTDIR.
	if [ ! -e "${XDG_CONFIG_HOME}/zsh" ]; then
		# TODO: Update the symlink if the location changed.
		if [ -d "${dirname}/zsh" ]; then
			ln -s "${dirname}/zsh" "${XDG_CONFIG_HOME}/zsh"
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
	rm -rf "${ZDOTDIR}/.zsh_sessions"
}

_vim() {
	# Setup directories.
	mkdir -p "${XDG_CONFIG_HOME}"
	mkdir -p "${XDG_STATE_HOME}/vim"
	mkdir -p "${XDG_DATA_HOME}/vim/spell"
	mkdir -p "${XDG_DATA_HOME}/vim/view"
	mkdir -p "${XDG_CACHE_HOME}/vim/backup"
	mkdir -p "${XDG_CACHE_HOME}/vim/swap"
	mkdir -p "${XDG_CACHE_HOME}/vim/undo"

	# Get the full path of the current working directory.
	dirname="$(cd "${0%/*}" && printf '%s\n' "${PWD}")"

	# TODO: DRY: Pull this out into a function.
	# Symlink the dotfiles source directory to $ZDOTDIR.
	if [ ! -e "${XDG_CONFIG_HOME}/vim" ]; then
		# TODO: Update the symlink if the location changed.
		if [ -d "${dirname}/vim" ]; then
			ln -s "${dirname}/vim" "${XDG_CONFIG_HOME}/vim"
		fi
	fi

	# Cleanup
	rm -f "${HOME}/.viminfo"
}

_git() {
	# Setup directories.
	mkdir -p "${XDG_CONFIG_HOME}/git"

	if [ -f "${HOME}/.gitconfig" ]; then
		mv "${HOME}/.gitconfig" "${XDG_CONFIG_HOME}/git/config"
	fi
}

_gnupg() {
	# Migrate existing GnuPG keys, otherwise setup directory.
	if [ -d "${HOME}/.gnupg" ]; then
		mv "${HOME}/.gnupg" "${XDG_DATA_HOME}/gnupg"
	else
		mkdir -p "${XDG_DATA_HOME}/gnupg"
	fi

	# Get the full path of the current working directory.
	dirname="$(cd "${0%/*}" && printf '%s\n' "${PWD}")"

	# TODO: DRY: Pull this out into a function.
	# Symlink the dotfiles source directory to $ZDOTDIR.
	if [ ! -e "${XDG_DATA_HOME}/gnupg/gpg.conf" ]; then
		# TODO: Update the symlink if the location changed.
		if [ -f "${dirname}/gnupg/gpg.conf" ]; then
			ln -s "${dirname}/gnupg/gpg.conf" "${XDG_DATA_HOME}/gnupg/gpg.conf"
		fi
	fi
}

_zsh
_vim
_git
_gnupg
