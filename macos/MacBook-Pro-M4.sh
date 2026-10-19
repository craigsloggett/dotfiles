# shellcheck shell=sh
#
# Settings for the MacBook-Pro-M4 profile, sourced by macos/defaults after the
# settings every Mac shares.

set_dock_apps \
  /Applications/Firefox.app \
  /Applications/Ghostty.app \
  /System/Applications/Mail.app \
  /System/Applications/Calendar.app \
  /Applications/Signal.app \
  /Applications/Obsidian.app \
  /Applications/KeePassXC.app \
  /Applications/UTM.app \
  /Applications/Xcode.app

set_default '/Library/Application Support/CrashReporter/DiagnosticMessagesHistory' AutoSubmit bool false
set_default '/Library/Application Support/CrashReporter/DiagnosticMessagesHistory' ThirdPartyDataSubmit bool false

set_firefox_exceptions \
  https://google.com \
  https://claude.ai \
  https://spotify.com
