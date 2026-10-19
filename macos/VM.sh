# shellcheck shell=sh

set_dock_apps \
  /Applications/Firefox.app \
  /Applications/Ghostty.app

set_default '/Library/Application Support/CrashReporter/DiagnosticMessagesHistory' AutoSubmit bool false
set_default '/Library/Application Support/CrashReporter/DiagnosticMessagesHistory' ThirdPartyDataSubmit bool false

set_firefox_exceptions
