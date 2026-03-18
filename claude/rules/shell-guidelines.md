---
paths:
  - "**/*.sh"
  - "install"
---

# Shell Guidelines

## POSIX Compliance

- Always use `#!/bin/sh`. Never use `#!/bin/bash` or `#!/usr/bin/env bash`.
- Never use bashisms: no `[[ ]]`, no `local`, no arrays, no `source` (use `.`), no `$(( ))` arithmetic when `expr` suffices, no `set -o pipefail`.
- Always run `shellcheck` before committing.
- Use `printf` for all output. Never use `echo`.
- Always single-quote `printf` format strings. When the line contains variable expansion, use `%s` and pass the expansion as a separate double-quoted argument: `printf '%s\n' "message: ${var}"`. When there is no expansion, put the entire string in the single-quoted format string: `printf 'static message.\n'`.

## Quoting and Variable Expansion

- Always use `"${var}"` (curly braces + double quotes) for variable expansion, even when disambiguation is not required.
- Quote all command substitutions: `"$(command)"`.
- Use `"$@"` to pass arguments through, never `$*`.

## Error Handling

- Use `set -ef` inside `main()`, not at the file's top level.
  - Exception: simple scripts without a `main()` function (e.g., hooks) may use `set -u` at the top level.
- Use `${var:?error message}` for required arguments (fail-fast with a useful message).
- Check command availability with `command -v <cmd> >/dev/null 2>&1` before use.
- Use `trap cleanup EXIT` when temporary resources (files, sockets, tunnels) are created.
- Validate inputs early. Exit with a non-zero status on failure.

## Script Structure

- Wrap the script body in a `main()` function. Call `main "$@"` as the last line of the file.
- Place `set -ef` and color initialization at the top of `main()`, before any logic.
- Define helper functions above `main()`. Each logical step gets its own function.
- Use TTY-aware colored output, initialized inside `main()`:
  ```sh
  ! [ -t 2 ] || {
    c1='\033[1;33m'
    c2='\033[1;34m'
    c3='\033[m'
  }
  ```
- Define a `log()` helper for user-facing messages. Direct log output to stderr (`>&2`).
- Exception: small single-purpose scripts (hooks, one-shot utilities) may omit `main()` and use a linear structure.

## Formatting

- Use `shfmt -i 2 -ci` style: 2-space indent, indented case bodies.
- Keep functions short and focused.
- Use `snake_case` for function and variable names.

## Dotfiles Repo Patterns

- The `install` script uses `_<tool>()` functions for each tool's setup: create directories, call `symlink_dotfiles`, migrate legacy files.
- Hooks read JSON from stdin via `jq`. Always guard with `command -v jq` before use.
- Use `ln -sf` for file symlinks and `ln -sfn` for directory symlinks.
