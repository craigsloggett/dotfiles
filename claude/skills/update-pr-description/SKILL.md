---
name: update-pr-description
description: Use when the user asks to write or update a pull request description, especially to make it declarative (what the PR introduces) rather than a history of the commits or the work done.
---

The current PR number:

!`gh pr view --json number --jq .number`

The current PR body:

!`gh pr view --json body --jq .body`

The diff this PR introduces, against its base branch:

!`git diff "$(gh pr view --json baseRefName --jq .baseRefName)"...HEAD`

## Workflow

1. Confirm the target PR. The values above are the current branch's PR. If the user names a different number, fetch it instead before continuing (`gh pr view <number> --json number,body,baseRefName` and `git diff <base>...HEAD`).

2. Write from the diff above, not the commit log. The description must describe the merged result. Read the changed files in their final form where the diff alone is hard to summarize. The commit history (`git log <base>..HEAD`) is at most a hint for grouping; never transcribe it.

3. Draft the new body as declarative bullets (see Rules). Cover every meaningful change in the diff, including ones the commit messages bury (a test suite, a doc table, a renamed default).

4. Apply it and report the URL.

   ```sh
   gh pr edit <number> --body "$(cat <<'EOF'
   - ...
   EOF
   )"
   ```

   Leave the title alone unless the user asks. If the existing body has hand-written sections the user clearly wants kept (a linked issue, a screenshot), preserve them.

## Rules

- Declarative, not historical. Each bullet states what the PR introduces and the resulting behavior, in present tense (`Adds`, `Locates`, `Fails when`, `Documents`). Never narrate the process (`First I added`, `Then refactored`, `Changed X to Y to Z`) or mirror the commit-by-commit history.
- Derive bullets from the final diff. If a change was added then reverted within the branch, it is not in the description. If a change exists in the diff but no commit subject mentions it, it still belongs.
- Group related changes into one bullet. One concern per bullet, not one commit per bullet.
- Concise bullet points only. No markdown headings (`##`), no test-plan section.
- Never use em dashes (`—`). Use commas or parentheses.
- Backtick identifiers: inputs, outputs, filenames, flags, function names.
- Keep the title under 70 characters if you touch it; default to not touching it.
- Don't invent. Every bullet must trace to something in the diff.
