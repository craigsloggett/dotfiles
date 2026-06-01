---
paths:
  - '**/.claude/agents/*.md'
  - '**/claude/agents/*.md'
---

## Claude Agent

### Headings

- Use `##` for the document title and `###` for sections; do not use `#` (H1).

### Skill or Agent?

Decide this first. A subagent is for context isolation: it does verbose work you will not reference
again, reads many files, and returns a summary to the main thread. A skill is a reusable prompt that
runs in the main context. "Define a custom subagent when you keep spawning the same kind of worker
with the same instructions." If what you want is a reusable prompt, not an isolated worker, stop: it
belongs in a skill, not an agent.

### Workflow

1. Archetype gate, asked first. Auditor or investigator? An auditor checks encoded rules, stays
   read-only, and returns a binary verdict. An investigator reads many files and reports a summary.
   Everything downstream forks here, so settle it before writing anything.
2. Name it as a noun. Agents are entities you address (`consistency-reviewer`, `pr-reviewer`), not
   actions you invoke. This is the inverse of the verb-noun rule for skills. Lowercase and hyphens
   (the schema requires that anyway).
3. Build the frontmatter for the archetype (see below).
4. Write the body. The body is the system prompt. A subagent gets only this plus basic environment,
   not the full Claude Code prompt, so it has to be self-contained.
5. Pick model and effort. High-stakes judgment auditing gets `model: opus` or `effort: high`.
   Low-effort auditing produces shallow misses, which defeats the point.

### Auditor Archetype

Read-only is enforced by Claude Code, not by pattern-matching commands. Do not grep Bash in a
`PreToolUse` hook to catch mutations: shell has unbounded ways to express a write (`git -C other
commit`, `cp`, `find -delete`, `eval "$(...)"`, command substitution), so the guard fails open on
the first form it does not anticipate. That is the awk `-v` trap in agent clothing. Use a permission
mode instead.

1. Boundary: `permissionMode: dontAsk`. It auto-denies any tool call not pre-approved while still
   running read-only Bash, so the auditor's read-only git (`git diff`, `git log`, `git show`) works
   and every mutation is denied by default. Fail-closed and enforced. `permissionMode: plan` is the
   alternative for pure read-only exploration; it should run read-only git the same way, though that
   is unverified.
2. Tools: allowlist what a reader needs, `tools: Read, Grep, Glob, Bash`. Allowlisting is bounded
   where a denylist is not; Write, Edit, and everything else are denied. (`disallowedTools: Write,
   Edit` is the looser equivalent and does not touch Bash, so it is never the boundary alone.)
3. Non-recognized read-only tools: if the auditor runs a tool Claude Code does not know is
   read-only (`shellcheck`, `tflint`), `dontAsk` denies it. Allowlist those exact commands in
   `.claude/settings.json` `permissions.allow` (`"Bash(shellcheck:*)"`). Command-scoping lives in
   settings.json, not frontmatter, and the allowlist is project-wide, so allowlist only genuinely
   read-only commands.
4. Runaway: set `maxTurns` so a misfiring auditor cannot loop forever.

Hard gate: if the request is an auditor but names Edit or Write in its tools, refuse. "An auditor
cannot hold Edit or Write. Drop them, or switch the archetype to investigator." A reviewer that can
edit defends its own edits.

Output is a binary verdict, SHIP or FIX, never prose critique. State this in the body. A verdict
has a finite pass condition (all encoded rules satisfied) so the agent halts; prose critique has no
bottom, so it nit-loops and never hands off. The schema has no output-shape field, so this lives in
the prompt.

Scope, written into the body: the auditor checks encoded rules only, what lives in `rules/*.md`
plus any preloaded skills. Caveat it honestly: it improves recall of rules already written, invents
no taste, and enforces nothing not already encoded. It is shellcheck's judgment-based sibling, not a
senior engineer.

Context stays fresh. No `isolation: worktree`, no fork. The no-context start is the source of the
auditor's value: it did not write the code, so it will not defend it. Worktree and fork are for
agents that act.

Reference preload: if the auditor audits against a reference encoded in a skill, `skills:
[posix-awk]` injects that skill's full content at startup, so a shell auditor already knows the
gawk-versus-POSIX rules with no discovery step. You cannot preload a skill that sets
`disable-model-invocation: true`, and you would never preload a
side-effecting scribe into a reader anyway.

Trigger, in usage docs not frontmatter: run the auditor at true handoff, behind green lint, not on
every stop. The ordering is format, then lint (cheap, mechanical), then auditor (expensive,
judgment), then you. Running the opus auditor while shellcheck is still red wastes cost and
interleaves two feedback streams.

### Investigator Archetype

Lighter. It reads many files and returns a summary; the reason to make it an agent at all is
context isolation, keeping that verbose reading out of the main thread. It may hold read tools and
Bash, and it carries none of the auditor constraints: no binary verdict, no read-only permission
mode. The auditor's permission mode exists because it is trusted to be read-only; the investigator
skips it because it makes no such promise. `isolation: worktree` exists for action-taking fan-out
(relevant to `cascade-change`), not for a pure reader.

### Frontmatter Schema

Only `name` and `description` are required.

| Field             | Use                                                                          |
| ----------------- | ---------------------------------------------------------------------------- |
| `name`            | Required. Lowercase and hyphens. A noun.                                     |
| `description`     | Required. When to delegate to this agent.                                    |
| `tools`           | Allowlist (bare tool names only). Resolved after `disallowedTools`.          |
| `disallowedTools` | Denylist, applied first. Ignores Bash; a `tools` allowlist is tighter.       |
| `model`           | Alias, full ID, or `inherit`. `opus` for high-stakes auditing.               |
| `effort`          | Effort override. `high` for judgment work.                                   |
| `permissionMode`  | `dontAsk` (auto-deny unlisted; read Bash runs) or `plan` for auditors.       |
| `maxTurns`        | Turn ceiling. Set it on auditors.                                            |
| `skills`          | Preload full skill content. No `disable-model-invocation: true` skills.      |
| `hooks`           | Inline lifecycle hooks. Not the read-only mechanism (see Auditor archetype). |
| `isolation`       | `worktree` runs in a temp git worktree, auto-cleaned if unchanged.           |
| `mcpServers`      | MCP servers the agent may reach.                                             |
| `memory`          | Persistent memory scope: `user`, `project`, or `local`.                      |
| `background`      | `true` runs the agent as a background task.                                  |
| `color`           | Display color.                                                               |
| `initialPrompt`   | Auto-submitted first turn when the agent runs as a main session.             |
