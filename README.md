# dotfiles

Configuration and setup for macOS, applied by a single idempotent `install`
script. It sets up a new machine and converges an old one to the same result.

## Install

On a new machine:

```sh
/bin/sh -c "$(curl -fsSL https://raw.githubusercontent.com/craigsloggett/dotfiles/main/install)"
```

Or, from an existing clone:

```sh
./install
```
