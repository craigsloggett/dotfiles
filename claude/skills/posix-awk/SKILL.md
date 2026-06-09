---
name: posix-awk
description: >
  Write strictly POSIX-conformant awk and flag gawk/mawk extensions
  (gensub, asort, length(array), systime, FIELDWIDTHS, bitwise fns).
  Invoke for any awk you write, edit, or review, including one-liners in
  shell scripts, pipelines, Makefiles, or CI. If awk appears, invoke this skill.
---

## POSIX Awk

mawk is the default `/usr/bin/awk` on Ubuntu and GitHub-hosted runners, so a gawk-ism that runs locally can break or behave differently in CI. Write to POSIX awk; reach for an extension only when the runtime is known to be gawk.

### POSIX Vs Gawk

Non-POSIX features to avoid by default:

- String functions `gensub`, `patsplit`, `strtonum`, `asort`, `asorti`: gawk-only. Use POSIX `sub`/`gsub`/`split`/`match`.
- `gensub` backreferences: no POSIX equivalent; restructure with `match` + `substr`.
- Time functions `systime`, `strftime`, `mktime`: gawk extensions, not portable (mawk support is version-dependent).
- For dates, run shell `date` and pass the value in with `-v`.
- Bit and type functions `and`, `or`, `xor`, `lshift`, `rshift`, `compl`, `isarray`, `typeof`: gawk-only.
- `length(array)`: non-POSIX. Count with `for (k in arr) n++`.
- `delete arr` (whole array): non-POSIX. Delete elements with `delete arr[k]`, or loop.
- `nextfile`: non-POSIX.
- Multi-character/regex `RS` and the `RT` variable: gawk-only. POSIX `RS` is a single character.
- gawk-only variables: `PROCINFO`, `FPAT`, `FIELDWIDTHS`, `IGNORECASE`, `ARGIND`, `ERRNO`, `BINMODE`.
- `\x` hex escapes: non-POSIX. Octal `\ddd` is POSIX.

### Passing Shell Values

- Pass shell values in as data with `awk -v var="${value}"`, not by splicing them into program text; reference `var` inside the program.

### Regex Patterns

- Embed constant regex as `/regex/` literals; reserve `-v var=...` for dynamic values (user input, env data).
- `awk -v` runs C-style string-escape processing on the value before the regex engine sees it.
- POSIX leaves unknown escapes like `\.` undefined; mawk strips the backslash (with a warning), so `\.` becomes `.` (any char), not a literal dot.
- Don't rely on this: the one true awk strips `\.` too, and behavior varies across awks and versions. Never count on a bare `\.` surviving the `-v` layer.
- Regex literals (`/.../`) skip the string layer and behave consistently across awks.
- For genuinely dynamic patterns, the caller owns the double-escape (e.g. shell-level `\\.` to survive both layers).
- `sub(/regex/, repl)` returns the substitution count, so it doubles as a boolean. Prefer `cond && sub(/r/, repl) { action }` over `if (match($0, r)) { action; sub(r, repl) }`, which duplicates the regex.
- Build a non-trivial regex from named parts: assign each fragment to a `BEGIN` variable named for what it matches, then concatenate. The names document the regex in place of a comment.
- Name parts and patterns for their meaning (`leading_indent`, `key_separator`, `key_line_pattern`), never opaque abbreviations (`keyre`).

### Script Structure

- Default to the "filter pattern": specific pattern-action blocks at the top, a trailing `{ print }` passthrough at the bottom to handle every line the blocks don't claim.
- When a matching block prints its own output, end it with `next` to skip the passthrough and avoid double-printing.
- When a matching block mutates `$0` in place (e.g. two-argument `sub`), don't `print` or `next`; let the passthrough print the modified record.
- When the caller needs "did anything match?", set a flag in the matching block, check it in `END`, and `exit 2` (a distinct non-zero) so "no match" is distinguishable from awk's own errors.
- Don't mutate `-v` inputs in place. Copy to a working local (`output = replacement`) before `sub`/`gsub`, so the input stays visible and reusable.

### Variable Naming

- Use descriptive snake_case for `-v` variables (`pattern`, `replacement`, `version`, `output`); the shell-side casing need not match.

### Comments

- Keep trailing `#` comments to a short phrase, aligned to a consistent column within each block (at least two spaces past the block's longest code line).
- When a comment needs more than a phrase (typically the "why" behind a non-obvious line), put it on its own line above the code, not trailing.

### Example

```sh
awk -v pattern="${LINE_MATCH}" -v replacement="${LINE_REPLACE}" -v version="${LATEST_VERSION}" '
  $0 ~ pattern {                         # Match on the current line using the regex supplied in `pattern`.
    output = replacement                 # Working copy of the replacement template.
    gsub(/\{version\}/, version, output) # Substitute {version} with the latest version.
    print output
    next                                 # Skip the passthrough block for this line.
  }
  { print }                              # Passthrough for non-matching lines.
' "${FILE}"
```
