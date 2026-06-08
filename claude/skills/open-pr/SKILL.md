---
name: open-pr
description: Use when the user wants to commit the current working-tree changes onto a new branch and open a pull request, for a repo whose default branch requires PRs.
arguments:
  - dir
  - branch
  - title
---

## Arguments

Positional and optional. Invoke as `/open-pr <dir> <branch> <title>`.

- `dir`: path to the local clone. Blank uses the current directory.
- `branch`: branch to create. Blank derives a short kebab-case name from the change.
- `title`: commit subject and PR title. Blank derives a conventional-commit subject from the change.

## Workflow

Work in `<dir>` (the local clone; blank means the current directory).

1. If `git -C <dir> status --porcelain` is empty, report there is nothing to open and stop.
2. Branch: `git -C <dir> checkout -b <branch>` (carries the uncommitted changes onto it).
3. Stage and commit signed: `git -C <dir> add -A` then `git -C <dir> commit -S -m "<title>"`. If signing fails, hand back to the user to unlock the GPG key; do not commit unsigned.
4. Push: `git -C <dir> push -u origin <branch>`.
5. Open the PR: `gh pr create --title "<title>" --body "<brief summary>"` (run from `<dir>`; pass a body so it does not open an editor). Then invoke `update-pr-description` on the new PR for a declarative body.
6. Report the PR URL; leave the branch checked out with a clean tree.

## Rules

- The default branch's ruleset requires a PR and signed commits, so always branch and sign; never commit to the default branch directly.
- Do not merge the PR here; leave it open unless the caller asks otherwise.
