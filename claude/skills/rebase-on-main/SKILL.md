---
name: rebase-on-main
description: Use when the user wants to rebase the current feature branch on the freshly-updated default branch, resolve conflicts, force-push, and get the feature PR ready for review.
---

## Workflow

Current branch and status:

!`git status -sb`

1. Refuse if this is the default branch or the working tree is dirty; this rebases a
   feature branch and needs a clean tree.
2. Update the default branch, prune merged branches, and rebase:

   ```sh
   git checkout main
   git pull
   git gone
   git checkout <branch-name>
   git rebase main
   ```

3. Resolve conflicts: prefer the newer dependency version for bumped refs, and keep
   both the feature change and the version bump. Regenerate derived files (e.g. a
   terraform-docs README) rather than hand-merging them.
4. Force-push the rebased branch with `git push --force-with-lease`.
5. Verify checks with `gh pr checks <number> --watch`. If any fail, fix the issue,
   push, and re-check.
6. Report that the PR is ready for review.
