---
name: tidy-pr-commits
description: Use when the user wants the current PR branch's commit messages stripped to their subject lines, rewriting the branch history and force-pushing so the squash-merge body on main stays clean.
---

## Why

The user's repos squash-merge PRs, and GitHub's `COMMIT_MESSAGES` squash setting builds the
squash commit's body on main by concatenating every branch commit's full message. A branch
commit body therefore lands verbatim in main's history. The standing rule is that branch
commits carry a subject line only (conventional prefix, capitalized first word, imperative,
under 70 characters, no trailing period, no body); the why belongs in the PR description.
This skill is the retroactive fix for commits that were written with bodies anyway.

## Preconditions

Stop and report instead of proceeding if any of these fail:

- `git status --porcelain` is empty (no uncommitted changes).
- The current branch is not the default branch.
- `git fetch origin` succeeds, so the merge-base is computed against a current default branch.

## Workflow

1. Resolve the default branch and record the recovery points:

   ```sh
   default=$(gh repo view --json defaultBranchRef --jq .defaultBranchRef.name)
   base=$(git merge-base "origin/$default" HEAD)
   orig=$(git rev-parse HEAD)
   tree=$(git rev-parse 'HEAD^{tree}')
   ```

2. Rewrite every commit after the merge-base down to its first line. The amend re-signs each
   commit (`commit.gpgsign`); author identity and author date are preserved:

   ```sh
   git rebase -f "$base" \
     --exec 'git commit --amend --no-edit -m "$(git log -1 --format=%s HEAD)"'
   ```

3. Verify only messages changed, then confirm every rewritten commit is signed:

   ```sh
   [ "$(git rev-parse 'HEAD^{tree}')" = "$tree" ] || echo "TREE MISMATCH"
   git log --format='%G? %h %s' "$base..HEAD"
   ```

   Every line must start with `G`. On a tree mismatch, restore with
   `git reset --hard "$orig"` and report.

4. Force-push, preserving anyone else's newer work:

   ```sh
   git push --force-with-lease
   ```

## Failure handling

- GPG key locked (the amend fails to sign): `git rebase --abort` if the rebase is still in
  progress, `git reset --hard "$orig"` otherwise, then hand the session back to the user to
  unlock the key. Never disable signing.
- Any other mid-rebase failure: abort and reset to `$orig`, then report what happened. The
  original commits stay reachable from `$orig` until the rewrite is verified.
