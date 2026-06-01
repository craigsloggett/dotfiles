---
name: write-claude-rule
description: >
  Use when the user wants to create a NEW <type>.md rule file for a topic that has none yet. Author-side: it
  applies the taxonomy gate, then scaffolds frontmatter with the correct activation glob. To append a rule to a file that
  already exists, use add-claude-rule instead.
disable-model-invocation: true
arguments:
  - name: type
    description: >
      Topic for the new rule file. Resolves to <type>.md.
    required: true
  - name: glob
    description: >
      The activation glob(s) the topic owns (e.g. **/*.py). If omitted, propose one and confirm.
    required: false
allowed-tools: Write, Bash
---

## Write Claude Rule

This authors a new rule file, the one thing the scribe `add-claude-rule` refuses to do. It is two parts: a taxonomy gate (the real value) and a trivial scaffold. The gate is what stops a topic that is really a section (yq) from becoming its own always-on file. This is separate from authoring a skill, which produces a folder of files rather than a single rule file.

The target is `<type>.md`. The rules directory is a symlink into the dotfiles repo. Write through the symlink, run git in the repo so the change is versioned.

Existing topics and their globs:

!`cd ~/.claude/rules && for f in *.md; do printf '%s:' "${f%.md}"; awk '/^---$/{c++; next} c==1 && /^[[:space:]]*-[[:space:]]*"/{ q=$0; sub(/^[^"]*"/,"",q); sub(/".*$/,"",q); printf " %s", q } c>=2{exit}' "$f"; echo; done`

Dotfiles repo root:

!`git -C ~/.claude/rules rev-parse --show-toplevel`

1. Refuse if it already exists. If `<type>` is in the list above, stop: the file exists, so appending a rule is `add-claude-rule`'s job, not this skill's.
2. Taxonomy gate. Establish the activation glob the topic owns (from the `glob` argument, or propose one and confirm). Compare it to the globs above:
   - If it is already owned by, or a subset of, an existing file's glob, refuse. The topic is a section of that file, not its own file (yq fires on `**/*.sh`, so it belongs in shell). Point the user at `add-claude-rule` for that file and stop.
   - A topic qualifies only if it activates on a pattern no existing file owns. It need not be a file extension; a distinct path pattern counts (`**/action.yml`, `.github/**`).
3. Scaffold. Write the file with frontmatter listing the glob(s) and a single H1 title in title case (`composite-actions` becomes `# Composite Actions`):

   ```
   ---
   paths:
     - "<glob>"
   ---

   # <Type>
   ```

   No invented rules and no headings beyond the title. Headings appear when `add-claude-rule` files the first rule.
4. Stage the new file and show `git -C <repo-root> diff --staged -- claude/rules/<type>.md`. Confirm before committing.
5. Commit GPG-signed as `claude: Add <type> rule` (subject under 70 chars, imperative, no trailing period, no AI attribution). On signing failure, hand the session back to the user; do not disable signing.
6. Hand off. If the user has the first rule in hand, invoke `add-claude-rule` for `<type>` to file it.
