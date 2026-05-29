---
name: write-claude-agent
description: Use when the user asks to create a new Claude Code subagent (a reusable worker spawned for context isolation), or to clean up an existing one.
---

## Skill or agent?

Decide this first. A subagent is for context isolation: it does verbose work you will not reference again, reads many files, and returns a summary to the main thread. A skill is a reusable prompt that runs in the main context. "Define a custom subagent when you keep spawning the same kind of worker with the same instructions." If what you want is a reusable prompt, not an isolated worker, stop and use `write-claude-skill` instead.

The boilerplate is not the point. What this skill bakes in is the agent-specific discipline: the archetype fork, mechanical read-only enforcement, a terminating verdict, and noun naming.

## Workflow

Existing agents:

!`ls ~/.claude/agents/`

1. Archetype gate, asked first. Auditor or investigator? An auditor checks encoded rules, stays read-only, and returns a binary verdict. An investigator reads many files and reports a summary. Everything downstream forks here, so settle it before writing anything.
2. Name it as a noun. Agents are entities you address (`consistency-reviewer`, `pr-reviewer`), not actions you invoke. This is the inverse of the verb-noun rule for skills. Lowercase and hyphens (the schema requires that anyway).
3. Build the frontmatter for the archetype (see below).
4. Write the body. The body is the system prompt. A subagent gets only this plus basic environment, not the full Claude Code prompt, so it has to be self-contained.
5. Pick model and effort. High-stakes judgment auditing gets `model: opus` or `effort: high`. Low-effort auditing produces shallow misses, which defeats the point.
6. Save to `~/.claude/agents/<noun>.md`.

## Auditor archetype

Read-only is not one switch. It decomposes into three independent leaks, and you plug all three or the agent is read-only in appearance only.

1. Tool layer: `disallowedTools: Write, Edit`. Necessary, not sufficient.
2. Shell layer: a `PreToolUse` Bash-guard hook. The moment an auditor has Bash (and it does, for `git diff` and `shellcheck`), the denylist is a half-measure: `disallowedTools` does not touch Bash, so the agent can still `git commit`, `git push`, `rm`, redirect with `>`, or `sed -i`. Copy `templates/bash-guard.sh` next to the agent and reference it. The coupling is absolute: an auditor with Bash in its tools carries the Bash-guard hook. The two are emitted together, never separately. An auditor with no Bash may use `permissionMode: plan` instead and skip the guard (plan mode permits read-only Bash but blocks edits).
3. Runaway layer: set `maxTurns` so a misfiring auditor cannot loop forever.

Hard gate: if the request is an auditor but names Edit or Write in its tools, refuse. "An auditor cannot hold Edit or Write. Drop them, or switch the archetype to investigator." A reviewer that can edit defends its own edits.

Output is a binary verdict, SHIP or FIX, never prose critique. State this in the body. A verdict has a finite pass condition (all encoded rules satisfied) so the agent halts; prose critique has no bottom, so it nit-loops and never hands off. The schema has no output-shape field, so this lives in the prompt.

Scope, written into the body: the auditor checks encoded rules only, what lives in `rules/*.md` plus any preloaded skills. Caveat it honestly: it improves recall of rules already written, invents no taste, and enforces nothing not already encoded. It is shellcheck's judgment-based sibling, not a senior engineer.

Context stays fresh. No `isolation: worktree`, no fork. The no-context start is the source of the auditor's value: it did not write the code, so it will not defend it. Worktree and fork are for agents that act.

Reference preload: if the auditor audits against a reference encoded in a skill, `skills: [posix-awk]` injects that skill's full content at startup, so a shell auditor already knows the gawk-versus-POSIX rules with no discovery step. You cannot preload a skill that sets `disable-model-invocation: true` (a scribe like `add-claude-rule`), and you would never preload a side-effecting scribe into a reader anyway.

Trigger, in usage docs not frontmatter: run the auditor at true handoff, behind green lint, not on every stop. The ordering is format, then lint (cheap, mechanical), then auditor (expensive, judgment), then you. Running the opus auditor while shellcheck is still red wastes cost and interleaves two feedback streams.

## Investigator archetype

Lighter. It reads many files and returns a summary; the reason to make it an agent at all is context isolation, keeping that verbose reading out of the main thread. It may hold read tools and Bash, and it carries none of the auditor constraints: no binary verdict, no three-layer guard. `isolation: worktree` exists for action-taking fan-out (relevant to `cascade-change`), not for a pure reader.

## Frontmatter schema

Only `name` and `description` are required.

| Field             | Use                                                                          |
| ----------------- | ---------------------------------------------------------------------------- |
| `name`            | Required. Lowercase and hyphens. A noun.                                     |
| `description`     | Required. When to delegate to this agent.                                    |
| `tools`           | Allowlist. Resolved against the pool left after `disallowedTools`.           |
| `disallowedTools` | Denylist, applied first. `Write, Edit` for any auditor.                      |
| `model`           | Alias, full ID, or `inherit`. `opus` for high-stakes auditing.               |
| `effort`          | Effort override. `high` for judgment work.                                   |
| `permissionMode`  | `plan` is read-only (allows read Bash, blocks edits); also `default`, etc.   |
| `maxTurns`        | Turn ceiling. Set it on auditors.                                            |
| `skills`          | Preload full skill content. No `disable-model-invocation: true` skills.      |
| `hooks`           | Inline lifecycle hooks. `PreToolUse` with exit 2 blocks a call.              |
| `isolation`       | `worktree` runs in a temp git worktree, auto-cleaned if unchanged.           |
| `mcpServers`      | MCP servers the agent may reach.                                             |
| `memory`          | Persistent memory scope: `user`, `project`, or `local`.                      |
| `background`      | `true` runs the agent as a background task.                                  |
| `color`           | Display color.                                                               |
| `initialPrompt`   | Auto-submitted first turn when the agent runs as a main session.             |

## Gotchas

- `disallowedTools: Write, Edit` does not block Bash writes. An auditor with Bash needs the Bash-guard hook, or it is writable in practice. This is the agent-world cousin of the awk `-v` escaping trap.
- Noun naming, not verb. Agents are addressed, not invoked.
- An auditor emits SHIP or FIX, never prose.
- Never preload a `disable-model-invocation: true` skill.
- An auditor never gets `isolation: worktree` or a fork.
