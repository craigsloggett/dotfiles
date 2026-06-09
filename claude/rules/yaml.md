---
paths:
  - '**/*.yaml'
  - '**/*.yml'
---

## Formatting

- Format with yamlfmt and ensure the file passes yamllint.
- Indent two spaces; indent sequence items under their key.
- Omit document markers: no leading `---` or trailing `...`.
- Single-quote strings only when needed; never quote a value that parses correctly bare.
- Keep lines to 120 characters or fewer.
- Allow at most one consecutive blank line.
- Start comments with a space after `#`, at least one space from any preceding content.

## Inline Shell

- Set `shell: sh` on `run:` steps; the runner defaults to bash, and the shell rules assume POSIX sh.
- Keep `run:` steps short. Extract non-trivial or multi-line logic to `src/<name>.sh` and invoke it, as the composite-actions rule requires.
- Inline snippets follow the POSIX compliance, quoting, and error-handling rules in `shell.md`. File-level rules (shebang, `set -euf`, `main()`, file-wide shfmt/shellcheck) do not apply to a snippet.
- Pass `${{ }}` expression values into shell through `env:`, never spliced into the command text, so a value cannot break out of the command.
