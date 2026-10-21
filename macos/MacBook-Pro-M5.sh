# shellcheck shell=sh

privacy_and_security() {
  # Analytics & Improvements -> Share Mac Analytics = Unset
  ! defaults read '/Library/Application Support/CrashReporter/DiagnosticMessagesHistory' AutoSubmit >/dev/null 2>&1 ||
    (
      sudo -n -v 2>/dev/null || printf '%s\n' "Unsetting DiagnosticMessagesHistory AutoSubmit needs sudo access."
      sudo defaults delete '/Library/Application Support/CrashReporter/DiagnosticMessagesHistory' AutoSubmit
    )
  # Analytics & Improvements -> Share with App Developers = Unset
  ! defaults read '/Library/Application Support/CrashReporter/DiagnosticMessagesHistory' ThirdPartyDataSubmit >/dev/null 2>&1 ||
    (
      sudo -n -v 2>/dev/null || printf '%s\n' "Unsetting DiagnosticMessagesHistory ThirdPartyDataSubmit needs sudo access."
      sudo defaults delete '/Library/Application Support/CrashReporter/DiagnosticMessagesHistory' ThirdPartyDataSubmit
    )

  # Apple Advertising -> Personalized Ads = Disabled
  write com.apple.AdLib allowApplePersonalizedAdvertising -bool false
}

# Firefox -> Privacy & Security -> History -> Clear history when Firefox closes -> Manage Exceptions
write org.mozilla.firefox SanitizeOnShutdown__Exceptions__0 -string https://google.com

# Dock items, left to right
dock Mail Calendar Firefox Ghostty KeePassXC Slack
