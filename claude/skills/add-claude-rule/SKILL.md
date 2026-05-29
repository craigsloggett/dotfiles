---
name: add-claude-rule
description: >
  Use when the user wants to add a rule to an existing ~/.claude/rules/<type>.md, however they phrase it
  (e.g. "add a markdown rule to keep lines under 120", "make it a shell rule that ...") for a known type.
  Interpret the rule from their message and file it; capture their intent without expanding its scope.
  For a brand-new rule file on a topic no existing file owns, use write-claude-rule instead.
arguments:
  - name: type
    description: >
      The rule domain, matching a rule file in ~/.claude/rules (e.g. markdown, shell, terraform, go, yq).
      Resolves to <type>.md.
    required: true
  - name: rule
    description: >
      The rule to file, interpreted from the user's request. Phrase it as a clean imperative bullet that
      captures what they asked for, without inventing or expanding the intent.
    required: true
allowed-tools: Read, Edit, Bash
---

# Add Claude rule

Capture the user's intent, do not author beyond it. Interpret their request into a clean imperative bullet that matches the voice and format of sibling bullets, but never add scope, caveats, or constraints they did not ask for. If their wording is already a clean rule, keep it close to how they said it.

The target is `<type>.md`. The rules directory is a symlink into the dotfiles repo. Edit through the symlink, run git in the repo so the change is versioned.

Three conditions stop it cold: the target file does not exist, the rule duplicates an existing line, or it contradicts one. On any of them, change nothing and hand back to the user.

Available rule files:

!`ls ~/.claude/rules/`

Dotfiles repo root:

!`git -C ~/.claude/rules rev-parse --show-toplevel`

1. Resolve the target: `~/.claude/rules/<type>.md`. If it is in the list above, continue. If not, stop (write nothing, create nothing):
   - If `<type>` looks like a typo or alias for a listed file, show the available files and ask which one.
   - If no file covers this topic, hand back to the user. Do not create a new rule file; that is an authoring decision (a new always-on, path-gated config layer) outside this skill's mandate, and it has its own skill, `write-claude-rule`. The test for whether a new file is even warranted: the topic must activate on a glob no existing rule file owns. A glob that is a subset of another file's (yq fires on `**/*.sh`, so it is a section of shell, not its own file) means the rule belongs in that existing file.
2. Read the whole target file, including its headings.
3. Check the `rule` against every existing line:
   - Duplicate (an existing line already states this intent): report which line, change nothing, stop.
   - Contradicts an existing line: surface both lines, ask the user how to resolve, do not write.
4. Append it under the best-fitting existing heading, matching the file's bullet format. If no existing heading fits, propose a new heading and confirm it before writing.
5. Show the one-line diff (`git -C <repo-root> diff -- claude/rules/<type>.md`) and confirm before committing.
6. Commit GPG-signed. This repo scopes commits by directory, so use `claude: <subject>` (subject under 70 chars, imperative, no trailing period, no AI attribution). On signing failure, hand the session back to the user; do not disable signing.
