---
paths:
  - "**/*.sh"
  - "install"
---

# Shell Guidelines

## POSIX Compliance

- Shebang: `#!/bin/sh`. Never `#!/bin/bash` or `#!/usr/bin/env bash`.
- No bashisms: no `[[ ]]`, no `local`, no arrays, no `source` (use `.`), no `set -o pipefail`, no `<<-` heredocs.
- Use `$(( ))` for arithmetic. Avoid `expr` (legacy, fork-heavy).
- Use `printf` for all output. Never `echo`.
- Single-quote `printf` format strings. For variable expansion, use `%s` and pass the value as a separate double-quoted argument: `printf '%s\n' "message: ${var}"`. With no expansion, single-quote the full string: `printf 'static message.\n'`.
- Pass values into `sed` programs as data, not by splicing into program text. Avoid 'sed "s|pat|${value}|"' patterns, which break when ${value} contains the delimiter, &, \, or newlines. If you genuinely need `sed` with a dynamic replacement, escape the value first; `sed` is fine for static patterns.

## Quoting and Variable Expansion

- Always `"${var}"` (curly braces + double quotes), even when disambiguation isn't required. Exception: positional parameters use bare double quotes (`"$1"`, `"$@"`, `"$#"`), not `"${1}"`.
- Quote all command substitutions: `"$(command)"`.
- Pass arguments through with `"$@"`, never `$*`.
- Use `read -r` to disable backslash interpretation.

## Error Handling

- Set strict mode at the top of the file, before any function definitions: `set -euf`.
- Use `${var:?error message}` for required arguments.
- Check command availability with `command -v <cmd> >/dev/null 2>&1` before use.
- Validate inputs early. Exit non-zero on failure with a clear message to stderr.
- Set traps when temporary resources are created. Use `trap cleanup EXIT INT TERM HUP` so cleanup runs on signal interruption, not only normal exit.
- Remember that traps do not inherit into subshells. Set them in the scope that owns the resource.
- For single-statement failure handling, use `cmd || die "msg"` (or `cmd || handler`). For multi-statement failure handling, use `if ! cmd; then ... fi`. The `{ }` block form (`cmd || { ...; ...; }`) is correct but harder to read than `if` once the body is more than one statement.
- Validate one condition per statement and fail immediately with a specific message. Don't collect errors and report at the end; don't nest checks. Use `cond || die "msg"` for single-condition checks and `if cond1 && cond2; then die "msg"; fi` for compound conditions. Avoid `cond1 && cond2 && die "msg"`. The precedence reads correctly here but fails subtly when refactored, and the `if` form is unambiguous.

## Temporary Files

- Use `mktemp` for files and `mktemp -d` for session-scoped directories. Respect `$TMPDIR`; never hard-code `/tmp`.
- Write atomically: create the staging file with `mktemp` in the same directory as the target, then `mv` into place. Don't use predictable `.new`/`.tmp`/`.bak` suffixes — they collide on retry, leak on failure, and aren't safe against concurrent runs. Register the staging file with the same `trap` that covers other session resources.
- Register cleanup via `trap` immediately after `mktemp`, before any failure path can leak the resource.
- Set traps once, near the top of `main()` (or top-level for scripts without `main`), immediately after creating the resources they clean up. `trap` overwrites previous handlers for the same signal, so a second `trap` call silently disables the first. Set a single trap covering all cleanup, not one per resource.

```sh
  TMPDIR_SESSION="$(mktemp -d)"
  readonly TMPDIR_SESSION
  trap 'rm -rf "${TMPDIR_SESSION}"' EXIT INT TERM HUP
```

  For multiple resources, expand the trap body or call a cleanup function that handles all of them. Mark session resources `readonly` so later code can't accidentally reassign the path the trap will `rm -rf`.

## Script Structure

- Required-input checks (`${VAR:?msg}`), default assignments (`${VAR:=}`), and tool availability checks (`command -v`) may live at the top of the file as preamble, immediately after `set -euf` and before function definitions. Move them into a `check_requirements` function called from `main()` when the script supports `--help`, parses arguments before deciding what to do, or might be sourced by tests.
- Wrap the script body in `main()`. Call `main "$@"` as the last line of the file. Exception: small single-purpose scripts (hooks, one-shot utilities) may omit `main()` and run linearly with `set -euf` at the top.
- Define helper functions above `main()`. Each logical step gets its own function.
- Scope function-local variables with a subshell function body `func() ( ... )` instead of prefixing names with `_` to fake locality. Variables assigned inside the subshell don't leak to the caller, and `cd`/`umask`/`set` changes are confined to that scope. Trade-off: the subshell can't mutate caller state, so use a plain `{ ... }` body when the function needs to set a variable for the caller to read.

```sh
  # Yes
  do_thing() (
    target="$1"
    tmpdir="$(mktemp -d)"
    cd "${tmpdir}"
    # target, tmpdir, cwd all scoped to this subshell
  )

  # No
  do_thing() {
    _target="$1"
    _tmpdir="$(mktemp -d)"
    # leaks _target and _tmpdir into the caller's scope
  }
```

- Default to returning via exit status (0/non-zero) and optionally stdout, not by mutating caller variables. Functions that compose with `if`, `&&`, `$( )` are easier to read and test than functions that set globals the caller has to know about by name. Global mutation is fine for top-level state set once in `main()`; avoid it as a return channel from helpers.
- Helper functions that transform inputs into outputs take their inputs as positional arguments, not by reading globals. Assign positionals to named locals at the top (`file="${1:?file is required}"`), then use the names. This makes the contract visible at the call site and lets `main` thread state through pure helpers.
- Helper functions that assert about the script's environment (validating env-var inputs, checking installed tools, writing to fixed output destinations) read globals directly. Forcing them into positional form rewrites the env-var contract in a less readable shape with worse error messages.
- Keep positional argument lists to three or fewer. At four-plus the call site becomes unreadable and the function probably wants splitting, or it's actually an environment-assertion function masquerading as a transformation.
- Iterate over positional arguments with `for x in "$@"; do`. The explicit `"$@"` makes the iteration source visible and consistent with non-positional loops (`for x in some_list; do`). Never `for x in $@` (unquoted, word-splits) and never `utilities="$@"; for x in ${utilities}` (flattens to a string, loses argument boundaries).

## Formatting

- `shfmt -i 2 -ci`: 2-space indent, indented case bodies.
- Keep functions short and focused.
- `snake_case` for functions and variables.
- Format embedded program text (awk, jq, sed, sqlite, `python -c`, heredocs) across multiple lines when it exceeds one short line. Open the quote on the same line as the command and its flags; indent the program body two spaces from the command; close the quote on its own line, dedented back to the command, with any remaining shell arguments and redirects on that closing line. Indent inside the embedded program with the same two-space step. Example:

```sh
  awk -v pat="${LINE_MATCH}" -v repl="${LINE_REPLACE}" '
    $0 ~ pat {
      out = repl
      gsub(/REGEX/, "X", out)
      print out
      next
    }
    { print }
  ' "${FILE}" >"${staging}"
```

  One-liners stay one line: `awk -v x=1 '{ print $1+x }' file`. The multi-line form is for programs with multiple actions, function definitions, or anything that won't fit comfortably.
