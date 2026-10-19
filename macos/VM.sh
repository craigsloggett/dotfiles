# shellcheck shell=sh
#
# Settings for the VM profile, sourced by macos/defaults after the settings
# every Mac shares.

set_dock_apps \
  /Applications/Firefox.app \
  /Applications/Ghostty.app

set_default '/Library/Application Support/CrashReporter/DiagnosticMessagesHistory' AutoSubmit bool false
set_default '/Library/Application Support/CrashReporter/DiagnosticMessagesHistory' ThirdPartyDataSubmit bool false

set_firefox_exceptions
