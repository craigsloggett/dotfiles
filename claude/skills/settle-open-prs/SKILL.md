---
name: settle-open-prs
description: Use when the user wants to review the open PRs on a freshly created repo, fix dependabot PR titles to the commit convention, merge any with green checks, and pull the default branch into the local clone.
arguments:
  - dir
---

## Arguments

Positional and optional. Invoke as `/settle-open-prs <dir>`.

- `dir`: path to the local clone. Blank uses the current directory.

## Workflow

Work in `<dir>` (the local clone; if `$dir` is blank, the current directory).

1. List open PRs with `gh pr list --state open --json number,title,author`.
2. For each PR opened by dependabot (author login `app/dependabot`):
   - Check the title. The convention is a conventional-commit prefix (`type:` or `type(scope):`) followed by a Capitalized subject. If the first letter of the subject is lowercase, fix only that letter with `gh pr edit <number> --title "<corrected>"`. Example: `chore(ci): bump actions/checkout from 6.0.2 to 6.0.3` becomes `chore(ci): Bump actions/checkout from 6.0.2 to 6.0.3`.
   - Verify checks with `gh pr checks <number>`. If they are still running, wait with `gh pr checks <number> --watch`.
   - If every check is green and the title is correct, merge with `gh pr merge <number> --squash`.
3. For any non-dependabot PR, report it for review. Do not merge it.
4. Pull the default branch into the local clone so later work starts from the merged state: `git -C <dir> pull --ff-only` (a fresh clone is already on the default branch).

## Rules

- Only merge dependabot PRs, and only when every check is green and the title matches the convention. Never auto-merge a non-dependabot PR.
- Squash-merge so the default branch keeps the linear history its ruleset requires.
- Dependabot opens PRs asynchronously after a repo is created, so this settles whatever is open now and does not wait. If a dependabot PR appears later, run it again.
