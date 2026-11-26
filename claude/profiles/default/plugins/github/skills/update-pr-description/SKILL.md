---
name: update-pr-description
description: >-
  Write or update a pull request description so it is declarative (what the PR
  introduces) rather than a history of the commits or the work done.
when_to_use: >-
  Use when the user asks to write, update, or fix a pull request description.
---

## Workflow

The current PR number:

!`gh pr view --json number --jq .number`

The current PR body:

!`gh pr view --json body --jq .body`

The files this PR changes, against its base branch:

!`git diff --stat "$(gh pr view --json baseRefName --jq .baseRefName)"...HEAD`

1. Confirm the target PR. The values above are the current branch's PR. If the
   user names a different number, fetch it instead
   (`gh pr view <number> --json number,body,baseRefName` and
   `git diff --stat <base>...HEAD`).
2. Read the diff with `git diff <base>...HEAD`, one path or group of paths at a
   time when the stat above is large, and read changed files in their final
   form where the diff is hard to summarize. The body describes the merged
   result. Treat commit history (`git log <base>..HEAD`) as at most a grouping
   hint. Never transcribe it.
3. Draft the body (see Rules). Cover every meaningful change in the diff,
   including ones the commit messages bury (a test suite, a doc table, a
   renamed default).
4. Apply it with `gh pr edit <number> --body-file <file>`. Leave the title
   alone unless the user asks. Preserve any hand-written sections the user
   wants kept (a linked issue, a screenshot).
5. Invoke `conventions:review-prose` on the PR, then report the URL.

## Rules

- The body becomes the squash commit's message on the default branch, so it is
  the lasting record of the change.
- Write declaratively, in present tense (`Adds`, `Locates`, `Fails when`,
  `Documents`). State what the PR introduces and the resulting behavior. Never
  narrate the process (`First I added`, `Then refactored`) or mirror the commit
  history.
- Give each independent change its own bullet. Where changes depend on each
  other, such as a new type and the handler that uses it, describe them in a
  short paragraph instead of splitting the reasoning across bullets.
- Derive the body from the final diff. A change added then reverted within the
  branch is not in the description, and a change in the diff that no commit
  subject mentions still belongs.
- Backtick identifiers such as inputs, outputs, filenames, flags, and function
  names.
- Don't invent. Every statement must trace to something in the diff.
