# shellcheck shell=sh

# Firefox -> Privacy & Security -> History -> Clear history when Firefox closes -> Manage Exceptions
write org.mozilla.firefox SanitizeOnShutdown__Exceptions__0 -string https://google.com
write org.mozilla.firefox SanitizeOnShutdown__Exceptions__1 -string https://claude.ai
write org.mozilla.firefox SanitizeOnShutdown__Exceptions__2 -string https://github.com
write org.mozilla.firefox SanitizeOnShutdown__Exceptions__3 -string https://spotify.com

# Dock items, left to right
dock Mail Calendar Firefox Ghostty Slack KeePassXC Obsidian
