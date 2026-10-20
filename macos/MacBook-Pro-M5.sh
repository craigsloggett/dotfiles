# shellcheck shell=sh

# Privacy & Security -> Analytics & Improvements -> Share Mac Analytics = Managed by MDM
sudo defaults delete '/Library/Application Support/CrashReporter/DiagnosticMessagesHistory' AutoSubmit 2>/dev/null || :
# Privacy & Security -> Analytics & Improvements -> Share with App Developers = Managed by MDM
sudo defaults delete '/Library/Application Support/CrashReporter/DiagnosticMessagesHistory' ThirdPartyDataSubmit 2>/dev/null || :

# Firefox -> Privacy & Security -> History -> Clear history when Firefox closes -> Manage Exceptions
write org.mozilla.firefox SanitizeOnShutdown__Exceptions__0 -string https://google.com

# Dock items, left to right
dock Mail Calendar Firefox Ghostty KeePassXC Slack
