---
paths:
  - '**/*.sh'
  - install
---

## Shell

### POSIX Compliance

- Shebang `#!/bin/sh`. Never `#!/bin/bash` or `#!/usr/bin/env bash`.
- No bashisms: no `[[ ]]`, no `local`, no arrays, no `source` (use `.`), no `set -o pipefail`, no `<<-` heredocs.
- Use `$(( ))` for arithmetic, never `expr`.
- Use `printf` for all output, never `echo`.
- Single-quote `printf` format strings; pass expansions as `%s` with separate double-quoted arguments: `printf '%s\n' "message: ${var}"`.
- Pass values into embedded programs (`sed`, `awk`, `jq`) as data, not spliced into program text. `sed` is fine for static patterns; escape the value first if the replacement is dynamic. For awk-specific mechanics (`-v` escaping, regex literals), see the `posix-awk` skill.

### Quoting and Variable Expansion

- Always `"${var}"`. Exception: positional parameters use bare double quotes (`"$1"`, `"$@"`, `"$#"`), not `"${1}"`.
- Quote all command substitutions: `"$(command)"`.
- Pass arguments through with `"$@"`, never `$*`.
- Use `read -r`.

### Error Handling

- Set strict mode at the top of the file, before any function definitions: `set -euf`.
- Use `${var:?error message}` for required arguments.
- Check command availability with `command -v <cmd> >/dev/null 2>&1` before use.
- Validate inputs early; exit non-zero on failure with a clear message to stderr.
- Set `trap cleanup EXIT INT TERM HUP` when creating temporary resources. Traps don't inherit into subshells; set them in the scope that owns the resource.
- Single-statement failure: `cmd || die "msg"`. Multi-statement: `if ! cmd; then ... fi`, not the `{ }` block form.
- One condition per statement, failing immediately with a specific message. Don't collect errors to report at the end and don't nest checks. Use `cond || die "msg"` for single conditions and `if cond1 && cond2; then die "msg"; fi` for compound ones; avoid `cond1 && cond2 && die "msg"`.
- Aggregating output from independent tools into one block (e.g. running several linters and printing all their findings together) is reporting, not error collection; the fail-fast rule above governs validation conditions, so deferring such output to the end is fine.

### Temporary Files

- Use `mktemp` for files and `mktemp -d` for session-scoped directories. Respect `$TMPDIR`; never hard-code `/tmp`.
- Write atomically: `mktemp` a staging file in the target's directory, then `mv` into place. No predictable `.new`/`.tmp`/`.bak` suffixes.
- Register cleanup via `trap` immediately after `mktemp`, before any failure path can leak the resource.
- Set one trap covering all cleanup near the top of `main()` (or top-level for scripts without `main`), not one per resource. A second `trap` for the same signal silently disables the first.
- Mark session resources `readonly` so the path the trap will `rm -rf` can't be reassigned.

### Script Structure

- Required-input checks (`${VAR:?msg}`), default assignments (`${VAR:=}`), and tool checks (`command -v`) may sit at the top of the file as preamble, after `set -euf` and before function definitions. Move them into a `check_requirements` function called from `main()` when the script supports `--help`, parses arguments before deciding what to do, or might be sourced by tests.
- Wrap the script body in `main()`; call `main "$@"` as the last line. Small single-purpose scripts (hooks, one-shot utilities) may omit `main()` and run linearly.
- Define helper functions above `main()`. Each logical step gets its own function.
- Scope function-local variables with a subshell body `func() ( ... )` rather than `_`-prefixed names. Use a plain `{ ... }` body when the function must set a variable for the caller to read.
- Return via exit status (and optionally stdout), not by mutating caller variables. State set once in `main()` may be global; don't use globals as a return channel from helpers.
- Transformation helpers take inputs as positional arguments, assigned to named locals at the top (`file="${1:?file is required}"`). Environment-assertion helpers (validating env-var inputs, checking installed tools, writing to fixed destinations) read globals directly.
- Keep positional argument lists to three or fewer.
- Iterate over positional arguments with `for x in "$@"; do`. Never `for x in $@` (word-splits) or `utilities="$@"; for x in ${utilities}` (loses argument boundaries).
- Prefer `case` over chained `if`/`elif` for fixed alternatives.

### Formatting

- `shfmt -i 2 -ci`: 2-space indent, indented case bodies.
- Keep functions short and focused.
- `snake_case` for functions and variables.
- Format embedded program text (awk, jq, sed, sqlite, `python -c`, heredocs) across multiple lines when it exceeds one short line: open the quote on the command line, indent the body two spaces, close the quote on its own line dedented to the command with any remaining arguments and redirects there. One-liners stay one line.

### Gotchas

- In mikefarah yq (v4), `select(.uses | test(...))` needs no `// ""` guard, since `test()` on null returns false.
