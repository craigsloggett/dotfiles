---
paths:
  - "**/*.sh"
---

# awk Guidelines

## Passing Shell Values

- Pass values into `awk` programs as data, not by splicing into program text. Use `awk -v var="${value}"` and reference `var` inside the program.

## Regex Patterns

- For constant regex patterns, embed them as `/regex/` literals inside the awk program. Reserve `-v var=...` for dynamic values (user input, env-supplied data).
- Reason: `awk -v` runs C-style string-escape processing on the value before the regex engine sees it. POSIX leaves unknown escapes like `\.` undefined; mawk (the default `/usr/bin/awk` on Ubuntu, including GitHub-hosted runners) warns and strips the backslash, so the regex evaluated is `.` (any character), not `\.` (literal dot). gawk and BWK awk preserve `\.`. Regex literals (`/.../`) skip the string layer and behave identically on all three.
- When the pattern genuinely is dynamic, `-v` is the right tool; the caller is responsible for the double-escape (e.g., shell-level `\\.` to survive both layers).
- `sub(/regex/, repl)` returns the substitution count, so it doubles as a boolean condition. Prefer `cond && sub(/r/, repl) { action }` over `if (match($0, r)) { action; sub(r, repl) }`, which duplicates the regex.

## Script Structure

- Default to the **filter pattern**: specific pattern-action blocks at the top, a trailing `{ print }` passthrough at the bottom. The passthrough handles every line the specific blocks don't claim.
- When a matching block prints its own output, end it with `next` to skip the trailing passthrough and avoid double-printing. When a matching block mutates `$0` in place (e.g. two-argument `sub`), don't `print` or `next`, let the passthrough print the modified record.
- When "did anything match?" matters to the caller, set a flag in the matching block and check it in an `END` block. Exit a distinct non-zero code (e.g. `exit 2`) so the caller can distinguish "no match" from awk's own errors.
- Don't mutate `-v` input variables in place. Copy to a working local (`output = replacement`) before calling `sub`/`gsub` on it, so the input stays visible and reusable.

## Variable Naming

- Use descriptive snake_case names for `-v` variables (`pattern`, `replacement`, `version`, `line`, `output`). The shell-side casing (`UPPER` or `lower`) does not need to match.

## Comments

- Align trailing `#` comments to a consistent column within each block.

## Example

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
