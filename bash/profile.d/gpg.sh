# shellcheck shell=sh
#
# ${XDG_CONFIG_HOME}/bash/profile.d/gpg.sh
#

GPG_TTY="$(tty)"
export GNUPGHOME="${XDG_DATA_HOME}/gnupg"
export GPG_TTY
