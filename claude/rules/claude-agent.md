---
paths:
  - '**/.claude/agents/*.md'
  - '**/claude/agents/*.md'
---

## Claude Agent

### Headings

- Use `##` for the document title and `###` for sections; do not use `#` (H1).

### When To Create

- Create a subagent only for context isolation: verbose work you will not
  reference again that returns a summary to the main thread.
- A reusable prompt that runs in the main context is a skill, not an agent.

### Frontmatter

Only `name` and `description` are required.

| Field             | Use                                                                       |
| ----------------- | ------------------------------------------------------------------------- |
| `name`            | Required. Lowercase and hyphens. A noun you address.                      |
| `description`     | Required. When to delegate to this agent, not what it does.               |
| `tools`           | Allowlist (bare tool names). Resolved after `disallowedTools`.            |
| `disallowedTools` | Denylist, applied first. Ignores Bash; a `tools` allowlist is tighter.    |
| `model`           | Alias, full ID, or `inherit`. `opus` for high-stakes auditing.            |
| `effort`          | Effort override. `high` for judgment work.                                |
| `permissionMode`  | `dontAsk` (auto-deny unlisted, read Bash runs) or `plan` for read-only.   |
| `maxTurns`        | Turn ceiling. Set it on auditors so a misfire cannot loop forever.        |
| `skills`          | Preload full skill content. No `disable-model-invocation: true` skills.   |
| `hooks`           | Inline lifecycle hooks. Not the read-only mechanism; see Tools.           |
| `isolation`       | `worktree` runs in a temp git worktree, auto-cleaned if unchanged.        |
| `mcpServers`      | MCP servers the agent may reach.                                          |
| `memory`          | Persistent memory scope: `user`, `project`, or `local`.                   |
| `background`      | `true` runs the agent as a background task.                               |
| `color`           | Display color.                                                            |
| `initialPrompt`   | Auto-submitted first turn when the agent runs as a main session.          |

### Name

- Name agents as nouns you address (`consistency-reviewer`, `pr-reviewer`), not
  actions you invoke. This is the inverse of the verb-noun rule for skills.
- Lowercase and hyphens (the schema requires that anyway).

### Description

- State when to delegate to the agent, not what it does. It is what Claude reads
  to decide relevance.

### Tools

- Allowlist the minimum a reader needs, `tools: Read, Grep, Glob, Bash`.
  Allowlisting is bounded where a denylist is not.
- Enforce read-only with `permissionMode: dontAsk` (or `plan`), not by
  pattern-matching commands in a hook; shell has unbounded ways to express a
  write, so a hook guard fails open.
- `dontAsk` still runs read-only Bash, so read-only git (`git diff`, `git log`,
  `git show`) works while mutations are denied by default.
- Scope non-recognized read-only commands (`shellcheck`, `tflint`) in
  `.claude/settings.json` `permissions.allow`, not frontmatter; the allowlist is
  project-wide, so allowlist only genuinely read-only commands.
- Preload reference skills with `skills: [posix-awk]` to inject their full
  content at startup, skipping a discovery step.
- An investigator may hold Bash and write tools; an auditor holds neither Edit
  nor Write. If a read-only agent names them, refuse or switch the archetype.

### Body

- The body is the system prompt. A subagent gets only this plus basic
  environment, so it must be self-contained.
- State output shape here; the schema has no output field. An auditor returns a
  binary verdict (SHIP or FIX) and checks only encoded rules (`rules/*.md` plus
  preloaded skills). An investigator returns a summary.
- Note the trigger in the body: run an auditor at true handoff, behind green
  format and lint.

### Model And Effort

- High-stakes judgment auditing gets `model: opus` or `effort: high`; low effort
  produces shallow misses.
