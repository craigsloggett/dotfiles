---
name: settle-open-prs
description: Use when the user wants to settle the open PRs on a freshly scaffolded repo, fixing dependabot titles, merging the green ones, and pulling the default branch.
arguments:
  - dir
---

## Arguments

Positional and optional. Invoke as `/settle-open-prs <dir>`.

- `dir`: path to the local clone. Blank uses the current directory.

## Workflow

Work in `<dir>` (the local clone; blank means the current directory).

1. List open PRs: `gh pr list --state open --json number,title,author`.
2. For each dependabot PR (author `app/dependabot`):
   - Fix the title if needed: the convention is a conventional-commit prefix (`type:` / `type(scope):`) then a Capitalized subject. If the subject's first letter is lowercase, capitalize only it with `gh pr edit <number> --title "<corrected>"`. Example: `chore(ci): bump actions/checkout ...` becomes `chore(ci): Bump actions/checkout ...`.
   - Verify checks with `gh pr checks <number>` (add `--watch` if still running). If all green and the title is correct, merge with `gh pr merge <number> --squash`.
3. Report any non-dependabot PR for review; do not merge it.
4. Pull the default branch: `git -C <dir> pull --ff-only` (a fresh clone is already on it).

## Rules

- Dependabot opens PRs asynchronously after a repo is created, so this settles whatever is open now and does not wait. If one appears later, run it again.
