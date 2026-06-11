---
name: merge-dependabot
description: Use when the user wants to settle the open dependabot PRs in the current repo, merging the green ones and investigating, fixing, and rebasing the ones whose checks fail (for example a stale terraform-docs README, or a CI bump the other PRs must satisfy) before merging.
---

## Workflow

Open PRs on the current repo:

!`gh pr list --state open --json number,title,author`

Refuse to start if `git status --porcelain` is non-empty; this skill checks out and
rebases PR branches and needs a clean tree. Record the current branch with
`git rev-parse --abbrev-ref HEAD` to return to it at the end, and `git fetch origin`
so rebases target the latest default branch.

1. Identify the dependabot PRs above (author `app/dependabot`). Report any
   non-dependabot PR for review; never touch it.
2. Order the work: a PR that redefines the checks (touches `.github/workflows/`,
   bumps a CI or lint action ref, or changes a linter config) must merge before the
   PRs it gates, because merging it changes what "green" means for the rest. Inspect
   with `gh pr diff <number> --name-only`. If ordering is unclear, proceed anyway;
   the rebase-after-merge loop in step 7 self-corrects.
3. Bring the next PR up to date with the default branch. If it is behind (merging an
   earlier PR moved main), rebase it: `gh pr checkout <number>`, `git rebase
   origin/main`, regenerate any derived files (step 5), then `git push
   --force-with-lease`. On a rebase conflict, prefer the dependabot version bump and
   regenerate derived files rather than hand-merging them; if a conflict needs
   judgment, stop and ask.
4. Read its check status with `gh pr checks <number>` (add `--watch` if runs are
   still pending). All green: merge (step 6). A check failed: investigate (step 5).
5. Investigate the failure with `gh run view <run-id> --log-failed` (run id from the
   failing check's link). Classify it:
   - Mechanical (deterministic, no judgment): a stale terraform-docs README from a
     provider or module bump, a format or lint autofix, a regenerated lockfile or
     checksum, a check that passes once rebased onto a just-merged CI bump. Fix it on
     the PR branch (`gh pr checkout <number>` if not already there). For a stale
     terraform-docs README: confirm `command -v terraform-docs` (if missing, treat as
     complex and stop), list changed files with `gh pr diff <number> --name-only`,
     take the directories holding changed `.tf` files, and for each whose `README.md`
     contains `<!-- BEGIN_TF_DOCS -->` run:

     ```sh
     terraform-docs markdown table <dir> --output-file README.md --output-mode inject
     ```

     Commit signed, matching the target repo's commit convention (read its recent
     `git log`); never include `[dependabot skip]`. Push with plain `git push` (or
     `git push --force-with-lease` if a rebase was involved). Re-watch with `gh pr
     checks <number> --watch`. Green: merge. Still failing: it was not mechanical, so
     stop and ask.
   - Complex (needs judgment): a real test failure, a breaking API change, a type
     error, anything needing a code edit. Stop and report the PR, the failing check,
     and the log excerpt; ask the user before touching it.
6. Merge. Read the allowed styles from `gh api repos/<owner>/<repo>`
   (`merge_commit_allowed`, `squash_merge_allowed`, `rebase_merge_allowed`) and merge
   with the matching `gh pr merge <number> --merge | --squash | --rebase`.
7. After a merge the default branch moved. `git fetch origin`, then loop back to step
   1: re-list (catching PRs opened meanwhile), re-evaluate, and rebase any remaining
   dependabot PR that is now behind. Continue until no mergeable dependabot PR
   remains.
8. Return to the recorded branch with `git checkout <original-branch>` and report
   which PRs merged, which were fixed or rebased first, and which were handed back as
   complex. If a feature branch is in flight, `rebase-on-main` settles it on the new
   default branch.

## Rules

- Iterate to completion: after each merge, re-fetch and re-evaluate the remaining
  dependabot PRs, since merging one can change what the others' checks require. Merge
  check-defining PRs (CI or lint bumps) before the PRs they gate.
- Adding a fix commit to an up-to-date branch is a plain `git push`. A deliberate
  rebase rewrites history and uses `git push --force-with-lease`, never plain
  `--force`.
- Never put `[dependabot skip]` in a commit message. A human commit makes dependabot
  stop force-pushing the branch, preserving the fix; the skip string re-grants it
  permission to clobber.
- Only auto-fix deterministic, mechanical failures. Anything needing a code edit or
  judgment stops for the user with the PR, the failing check, and the log excerpt.
- Sign every commit, matching the target repo's commit convention (its recent git
  log), not this repo's. If signing fails, hand back to the user to unlock the GPG
  key; do not disable signing.
- Refuse to start on a dirty working tree, and restore the original branch when done.
- Dependabot opens and updates PRs asynchronously, so this settles whatever is open
  now; run it again if more appear. A PR idle for 30 days stops auto-rebasing, so
  rebase it manually as above rather than relying on `@dependabot rebase`.
