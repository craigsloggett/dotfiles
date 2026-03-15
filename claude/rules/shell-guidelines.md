---
paths:
  - "**/*.sh"
  - "install"
---

# Shell Guidelines

## POSIX Compliance

- Target `#!/bin/sh`. Avoid bashisms: no `[[ ]]`, no `local` (use function-scoped variables carefully), no arrays, no `source` (use `.`), no `$(( ))` arithmetic when `expr` suffices.
- Always run `shellcheck` before committing.
- Use `printf` over `echo` for portable output, especially with variables or escape sequences.

## Quoting and Variable Expansion

- Always use `"${var}"` (curly braces + double quotes) for variable expansion, even when disambiguation is not required.
- Quote all command substitutions: `"$(command)"`.
- Use `"$@"` to pass arguments through, never `$*`.

## Error Handling

- Use `set -u` to catch unset variable references.
- Check command availability with `command -v <cmd> >/dev/null 2>&1` before using optional tools.
- Validate inputs early. Exit with a non-zero status on failure.

## Formatting

- Use `shfmt -i 2 -ci` style: 2-space indent, indented case bodies.
- Keep functions short and focused.
- Use `snake_case` for function and variable names.

## Patterns Used in This Repo

- The `install` script uses `_<tool>()` functions for each tool's setup: create directories, call `symlink_dotfiles`, migrate legacy files.
- Hooks read JSON from stdin via `jq`. Always guard with `command -v jq` before use.
- Use `ln -sf` for file symlinks and `ln -sfn` for directory symlinks.
