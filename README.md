# dotfiles

Configuration and setup for macOS, applied by a single idempotent `install` script. It sets up a new Mac and converges an old one to the same result, and running it again changes nothing.

## Install

On a new Mac:

```sh
/bin/sh -c "$(curl -fsSL https://raw.githubusercontent.com/craigsloggett/dotfiles/main/install)"
```

From an existing clone:

```sh
./install
```

## What It Does

- Installs Homebrew (and with it the Command Line Tools) if missing.
- Clones this repository to `~/Developer/GitHub/craigsloggett/dotfiles` over HTTPS.
- Asks once for the host profile, the hostname and the Git email.
- Installs the profile's `Brewfile` with `brew bundle --global`.
- Links the configuration into `$XDG_CONFIG_HOME`.
- Moves files that tools leave in `~` into their XDG locations.
- Applies the macOS and app settings in `macos/defaults`.
- Creates an SSH key and switches `origin` to SSH once GitHub accepts it.

Anything that needs a person (adding the SSH key to GitHub, a conflict between an old and a new location) is listed at the end. Resolve it and run `install` again.

## Profiles

Each profile is a `homebrew/<profile>.Brewfile`. The chosen profile is linked to `$XDG_CONFIG_HOME/homebrew/Brewfile`, so `brew bundle --global` works by hand too.

## Environment

`zsh/.zprofile.d/<command>.sh` sets the XDG environment for a tool, and only loads when that command exists. `install` reads the same files, so every path is defined once.

## macOS Settings

`macos/defaults` sets System Settings and app preferences, one `set_default` line per setting, grouped by pane. A line writes only when the value differs, and the Dock, Finder and Control Center restart only when one of their settings changed, so a re-run is silent. `install` runs it every time, and it runs on its own too. `CHECK=1 macos/defaults` prints what differs without writing anything.

Safari, Mail and Contacts keep their preferences where only a terminal with Full Disk Access can write, so those sections wait for that grant. FileVault, iCloud, login items, Time Machine options, the wallpaper and the default browser still need a person.

## Left in `~`

- `.ssh`: OpenSSH has no way to move it.
- `.terraform.d`: `terraform login` always writes its credentials there.
- `.swiftpm`: SwiftPM recreates its links there on every run.
