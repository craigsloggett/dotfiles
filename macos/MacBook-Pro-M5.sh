# shellcheck shell=sh

lock_screen() {
  # Require password after screen saver begins or display is turned off = Immediately
  sysadminctl -screenLock status 2>&1 | grep -q 'delay is immediate' ||
    (
      printf '%s\n' "Setting the screen lock delay needs your login password."
      sysadminctl -screenLock immediate -password -
    )
  # Reopen windows when logging back in = Disabled
  write com.apple.loginwindow TALLogoutSavesState -bool false
}

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
write org.mozilla.firefox SanitizeOnShutdown__Exceptions__1 -string https://github.com
write org.mozilla.firefox SanitizeOnShutdown__Exceptions__2 -string https://spotify.com

# Firefox -> Add-ons and themes -> Extensions -> 1Password = Installed
write org.mozilla.firefox 'ExtensionSettings__{d634138d-c276-4fc8-924b-40a0ea21d284}__installation_mode' -string normal_installed
# Firefox -> Add-ons and themes -> Extensions -> 1Password -> Run in Private Windows = Allow
write org.mozilla.firefox 'ExtensionSettings__{d634138d-c276-4fc8-924b-40a0ea21d284}__private_browsing' -bool true
# Firefox -> Toolbar -> 1Password -> Unpin from Toolbar
write org.mozilla.firefox 'ExtensionSettings__{d634138d-c276-4fc8-924b-40a0ea21d284}__default_area' -string menupanel

# Dock items, left to right
dock Mail Calendar Firefox Ghostty KeePassXC Slack
