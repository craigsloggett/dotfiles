---
name: rebase-on-main
description: >-
  Rebase the current feature branch on the freshly-updated default branch,
  resolve conflicts, force-push, and get the feature PR ready for review.
when_to_use: >-
  Use when the user wants the current feature branch brought up to date with the
  default branch.
---

## Workflow

Current branch and status:

!`git status -sb`

Default branch:

!`gh repo view --json defaultBranchRef --jq .defaultBranchRef.name`

1. Refuse if this is the default branch or the working tree is dirty, because
   this rebases a feature branch and needs a clean tree.
2. Update the default branch, prune merged branches, and rebase:

   ```sh
   git checkout <default>
   git pull
   git gone
   git checkout <branch-name>
   git rebase <default>
   ```

3. Resolve conflicts: prefer the newer dependency version for bumped refs, and
   keep both the feature change and the version bump. Regenerate derived files
   (e.g. a terraform-docs README) rather than hand-merging them.
4. Force-push the rebased branch with `git push --force-with-lease`.
5. Verify checks with `gh pr checks <number> --watch`. If a check fails, read
   the log with `gh run view <run-id> --log-failed` and classify the failure.
   - Mechanical, where a check that verifies a generated or formatted artifact
     (rendered docs, formatting, a lockfile) fails because the rebase changed
     an input. Run the project's own generator for it, the same command the
     check runs, commit signed, push, and watch again. If it still fails, treat
     it as complex.
   - Complex, such as a real test failure or anything that needs a code edit.
     Stop and report the failing check and the log excerpt. Ask before
     touching it.
6. Report that the PR is ready for review.
