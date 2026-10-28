---
name: update-pr-description
description: Use when the user asks to write or update a pull request description, especially to make it declarative (what the PR introduces) rather than a history of the commits or the work done.
---

## Workflow

The current PR number:

!`gh pr view --json number --jq .number`

The current PR body:

!`gh pr view --json body --jq .body`

The diff this PR introduces, against its base branch:

!`git diff "$(gh pr view --json baseRefName --jq .baseRefName)"...HEAD`

1. Confirm the target PR. The values above are the current branch's PR. If the user names a different number, fetch it instead (`gh pr view <number> --json number,body,baseRefName` and `git diff <base>...HEAD`).

2. Write from the diff above, not the commit log; the body describes the merged result. Read changed files in their final form where the diff is hard to summarize. Treat commit history (`git log <base>..HEAD`) as at most a grouping hint; never transcribe it.

3. Draft the body as declarative bullets (see Rules). Cover every meaningful change in the diff, including ones the commit messages bury (a test suite, a doc table, a renamed default).

4. Apply it and report the URL.

   ```sh
   gh pr edit <number> --body "$(cat <<'EOF'
   - ...
   EOF
   )"
   ```

   Leave the title alone unless the user asks. Preserve any hand-written sections the user clearly wants kept (a linked issue, a screenshot).

## Rules

- Declarative, not historical. Each bullet states what the PR introduces and the resulting behavior, in present tense (`Adds`, `Locates`, `Fails when`, `Documents`). Never narrate the process (`First I added`, `Then refactored`) or mirror the commit history.
- Derive bullets from the final diff. A change added then reverted within the branch is not in the description; a change in the diff that no commit subject mentions still belongs.
- Group related changes into one bullet, one concern per bullet.
- Backtick identifiers: inputs, outputs, filenames, flags, function names.
- Don't invent. Every bullet must trace to something in the diff.
