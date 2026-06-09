---
name: merge-dependabot
description: Use when the user asks to merge open dependabot PRs, rebase the current branch on the default branch, and get a feature PR ready for review.
---

## Workflow

Open PRs on the current repo:

!`gh pr list --state open`

1. Identify any dependabot PRs in the list above.
2. For each dependabot PR, verify checks pass with `gh pr checks`, then merge with `gh pr merge <number> --squash`. These are safe to merge without reviewing the ref changes.
3. Check `gh run list --branch main` to see if any workflows are running from the merges. Wait for them to complete with `gh run watch`.
4. Rebase the current branch on the default branch:

   ```sh
   git checkout main
   git pull
   git gone
   git checkout <branch-name>
   git rebase main
   ```

5. Resolve conflicts: prefer the newer dependabot version for action refs, and keep both the feature change and the version bump.
6. Force push the rebased branch:

   ```sh
   git push --force
   ```

7. Verify checks using `gh pr checks <number> --watch`. If any fail, fix the issue, push, and re-check.
8. Report that the PR is ready for review.
