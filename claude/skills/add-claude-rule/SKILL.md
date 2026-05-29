---
name: add-claude-rule
description: >
  Use when the user says add a <type> rule: <imperative> (e.g. add a markdown rule, add a shell rule). Files an
  already-vetted, imperatively-stated rule into the matching cross-repo <type>-guidelines.md. The user has decided it is
  rule-worthy; scribe it, do not author or reword it.
disable-model-invocation: true
arguments:
  - name: type
    description: >
      The rule domain, matching a guidelines file in ~/.claude/rules (e.g. markdown, shell, awk, terraform, go, yq).
      Resolves to <type>-guidelines.md.
    required: true
  - name: rule
    description: >
      The finished imperative rule, exactly as the user stated it. Do not invent, reword, or expand its intent.
    required: true
allowed-tools: Read, Edit, Bash
---

# Add Claude rule

You are a scribe, not an author. The `rule` argument is final. Preserve its intent exactly. The only permitted edit is tidying surface voice (capitalization, leading verb form, punctuation) to match sibling bullets. Never change what the rule means.

The target is `<type>-guidelines.md`, not `<type>.md`. The rules directory is a symlink into the dotfiles repo. Edit through the symlink, run git in the repo so the change is versioned.

Three conditions stop the scribe cold: the target file does not exist, the rule duplicates an existing line, or it contradicts one. On any of them, change nothing and hand back to the user.

Available rule files:

!`ls ~/.claude/rules/`

Dotfiles repo root:

!`git -C ~/.claude/rules rev-parse --show-toplevel`

1. Resolve the target: `~/.claude/rules/<type>-guidelines.md`. If it is in the list above, continue. If not, stop (write nothing, create nothing):
   - If `<type>` looks like a typo or alias for a listed file, show the available files and ask which one.
   - If no file covers this topic, hand back to the user. Do not create a new guidelines file. A new file is a new always-on, path-gated config layer, and deciding a topic is rule-shaped enough to own one is an authoring decision, outside this skill's mandate. Only the user decides whether to create it and what it covers.
2. Read the whole target file, including its headings.
3. Check the `rule` against every existing line:
   - Duplicate (an existing line already states this intent): report which line, change nothing, stop.
   - Contradicts an existing line: surface both lines, ask the user how to resolve, do not write.
4. Append it under the best-fitting existing heading, matching the file's bullet format. Tidy voice only. If no existing heading fits, propose a new heading and confirm it before writing.
5. Show the one-line diff (`git -C <repo-root> diff -- claude/rules/<type>-guidelines.md`) and confirm before committing.
6. Commit GPG-signed. This repo scopes commits by directory, so use `claude: <subject>` (subject under 70 chars, imperative, no trailing period, no AI attribution). On signing failure, hand the session back to the user; do not disable signing.
