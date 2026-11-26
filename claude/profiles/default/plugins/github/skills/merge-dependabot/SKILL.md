---
name: merge-dependabot
description: >-
  Fix the titles of the open Dependabot PRs in the current repo and merge them.
when_to_use: >-
  Use when the user wants the current repo's Dependabot PRs merged, including
  the initial ones on a freshly scaffolded repo.
---

## Workflow

Open PRs on the current repo:

!`gh pr list --state open --json number,title,author`

Default branch:

!`gh repo view --json defaultBranchRef --jq .defaultBranchRef.name`

Refuse to start if `git status --porcelain` is non-empty, because this skill
checks out and rebases PR branches and needs a clean tree. Record the current
branch with `git rev-parse --abbrev-ref HEAD` to return to it at the end, and
`git fetch origin` so rebases target the latest default branch.

1. Identify the Dependabot PRs above (author `app/dependabot`). Report any
   non-Dependabot PR for review. Never touch it.
2. Fix each Dependabot PR's title. The squash commit takes the PR title, and
   the convention is a conventional-commit prefix (`type:` / `type(scope):`)
   then a capitalized subject. If the subject's first letter is lowercase,
   capitalize only it with `gh pr edit <number> --title "<corrected>"`, so
   `chore(ci): bump actions/checkout ...` becomes
   `chore(ci): Bump actions/checkout ...`.
3. Order the work. A PR that redefines the checks (touches `.github/workflows/`,
   bumps a CI or lint action ref, or changes a linter config) must merge before
   the PRs it gates, because merging it changes what "green" means for the rest.
   Inspect with `gh pr diff <number> --name-only`. If ordering is unclear,
   proceed anyway, because the rebase-after-merge loop in step 8 self-corrects.
4. Bring the next PR up to date with the default branch. If the PR is behind
   (merging an earlier PR moved the default branch), rebase it. Run
   `gh pr checkout <number>` and `git rebase origin/<default>`, regenerate any
   derived files (step 6), then `git push --force-with-lease`. On a rebase
   conflict, prefer the Dependabot version bump and regenerate derived files
   rather than hand-merging them. If a conflict needs judgment, stop and ask.
5. Read its check status with `gh pr checks <number>` (add `--watch` if runs are
   still pending). All green: merge (step 7). A check failed: investigate (step
   6).
6. Investigate the failure with `gh run view <run-id> --log-failed` (run id from
   the failing check's link). Classify it:
   - Mechanical (deterministic, no judgment), where a check that verifies a
     generated or formatted artifact is current (rendered docs, formatting, a
     lockfile, generated code) fails because the bump changed an input without
     regenerating it. Fix it on the PR branch (`gh pr checkout <number>` if not
     already there) by running the project's own generator for that artifact,
     the same command the check runs (look in the failing check, a pre-commit
     hook, or a Makefile target). If that tool is not available locally, treat
     the failure as complex and stop. Commit signed, matching the target repo's
     commit convention (read its recent `git log`). Push with plain `git push`
     (or `git push --force-with-lease` if you rebased). Re-watch with
     `gh pr checks <number> --watch`. Green: merge. Still failing: the failure
     was not mechanical, so stop and ask.
   - Complex (needs judgment), such as a real test failure, a breaking API
     change, a type error, or anything needing a code edit. Stop and report the
     PR, the failing check, and the log excerpt. Ask the user before touching
     it.
7. Merge. Read the allowed styles from `gh api repos/<owner>/<repo>`
   (`merge_commit_allowed`, `squash_merge_allowed`, `rebase_merge_allowed`) and
   merge with the matching `gh pr merge <number> --merge | --squash | --rebase`.
8. After a merge the default branch moved. Run `git fetch origin`, then loop
   back to step 1 to re-list (catching PRs opened meanwhile), re-evaluate, and
   rebase any remaining Dependabot PR that is now behind. Continue until no
   mergeable Dependabot PR remains.
9. Return to the recorded branch with `git checkout <original-branch>`. If that
   is the default branch, run `git pull --ff-only`. Report the PRs that merged,
   the ones you fixed or rebased first, and the ones you handed back as
   complex. If a feature branch is in flight, `rebase-on-main` settles it on the
   new default branch.

## Rules

- Never put `[dependabot skip]` in a commit message: a plain human commit makes
  Dependabot stop force-pushing the branch (preserving the fix), but the skip
  string re-grants it permission to clobber.
- Dependabot opens PRs asynchronously, so this merges whatever is open now. Run
  it again if more appear.
