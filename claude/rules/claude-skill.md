---
paths:
  - '**/.claude/skills/**/*.md'
  - '**/claude/skills/**/*.md'
---

## Frontmatter

| Field                      | Use                                                                          |
| -------------------------- | ---------------------------------------------------------------------------- |
| `name`                     | Required. kebab-case, action-oriented (verb-noun).                           |
| `description`              | Required. When to invoke, not what it does; what Claude reads for relevance. |
| `arguments`                | List of `{name, description, required}` for slash-command arguments.         |
| `disable-model-invocation` | `true` for side-effecting skills only; leave off read-only ones to auto-run. |
| `allowed-tools`            | The minimum set the skill needs.                                             |

Example:

```yaml
---
name: kebab-case-name
description: Use when ...
---
```

## Headings

- Use `##` for the document title and `###` for sections; do not use `#` (H1).

## Scope

- One job per skill. Multi-purpose skills branch internally and balloon.
- A skill earns its existence from gotchas. If there are no gotchas to capture,
  do not write it.

## Body

- Gotchas are the load-bearing content. Conventions are derivable from the code;
  gotchas are what justify the skill.
- Show, do not tell. A conformant example in `examples/` beats a paragraph
  describing the shape.
- Inline shell with `!` injects real state. Prefer `!git diff HEAD` over "look
  at the current diff". Only pin `!command` for ambient state available at load
  time (auth user, current repo, current branch). Values the user passes as
  arguments cannot be substituted into a `!` command, so reference them inside a
  step instead (e.g. `git -C $source log` in step 2).
- Be opinionated about terminology. Pick one term, name the rejected
  alternatives, move on.
- Check, do not guess. If the skill can verify a file exists or a command is on
  PATH, have it verify.

## Structure

- Default to a single `SKILL.md` inside a folder named after the skill. The
  folder lets you add `templates/`, `examples/`, or reference docs later without
  restructuring.
- Split a section into its own file only when it is a standalone format spec, or
  when the file would otherwise sprawl past ~150 lines. Otherwise keep it inline.
- Create supporting files lazily, only when you have something to write.

## Prose

- Imperative second person. "Run the tests," not "you should consider running
  the tests".
- No hedging or meta. No "I'll help you", no "this skill will".
- Do not restate what tool output already shows. If `!git status` runs, do not
  also describe its output shape.
- Headers earn their place. A header over two lines of content is wasted.
