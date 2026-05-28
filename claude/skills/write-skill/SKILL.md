---
name: write-skill
description: Use when the user asks to create a new Claude Code skill or clean up an existing one.
---

## Workflow

Existing skills:

!`ls ~/.claude/skills/`

1. Clarify the trigger. In one sentence, state what user request should make Claude reach for this skill. That sentence becomes the frontmatter description.
2. Decide invocation. Auto-invoke for read-only or scaffolding skills. Set `disable-model-invocation: true` for anything that mutates shared state (deploys, pushes, sends messages).
3. List the gotchas this skill exists to capture. Gotchas are the load-bearing content. If there are no gotchas, the skill probably is not worth writing.
4. Draft the body around those gotchas. Use `!command` inline where current state matters more than a description of it.
5. Decide structure. Default to a single `SKILL.md`. Split into supporting files only when the file would otherwise sprawl past ~150 lines, or when a section is a standalone format spec worth isolating.
6. Trim. Read the draft top to bottom and delete anything that restates what the reader already knows.
7. Save to `~/.claude/skills/<kebab-name>/SKILL.md`.

## Frontmatter

```yaml
---
name: kebab-case-name
description: Use when ...
---
```

Fields:

- `name`: kebab-case, action-oriented (verb-noun)
- `description`: when to invoke, not what it does. This is the only field loaded at session start, so it has to help Claude decide relevance
- `arguments`: optional. List of `{name, description, required}` for slash-command arguments
- `disable-model-invocation: true`: side-effecting skills only
- `allowed-tools`: the minimum set the skill needs

## Structure

Default: single `SKILL.md` inside a folder named after the skill. The folder lets you add `templates/`, `examples/`, or reference docs later without restructuring.

Split a section into its own file when it has a format spec of its own (the linked article's `CONTEXT-FORMAT.md` is the model). Otherwise keep it inline. Create supporting files lazily, only when you have something to write.

## Rules

Content:

- One job per skill. Multi-purpose skills branch internally and balloon.
- Gotchas over conventions. Conventions are derivable from the code. Gotchas are what justify the skill.
- Show, do not tell. A conformant example in `examples/` beats a paragraph describing the shape.
- Inline shell with `!` injects real state. Prefer `!git diff HEAD` over "look at the current diff". Only pin `!command` for ambient state available at load time (auth user, current repo, current branch). Values the user passes as arguments cannot be substituted into a `!` command, so reference them inside a step instead (e.g. `git -C $source log` in step 2).
- Be opinionated about terminology. Pick one term, name the rejected alternatives, move on.
- Check, do not guess. If the skill can verify a file exists or a command is on PATH, have it verify.

Prose:

- No em or en dashes. Use commas, colons, or parentheses.
- No bolded labels on short bullets. If `**Foo** - bar` is the whole bullet, write `Foo: bar` or drop the label.
- Imperative second person. "Run the tests," not "you should consider running the tests".
- No hedging or meta. No "I'll help you", no "this skill will".
- Do not restate what tool output already shows. If `!git status` runs, do not also describe its output shape.
- Headers earn their place. A header over two lines of content is wasted.
