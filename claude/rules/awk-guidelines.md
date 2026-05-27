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
