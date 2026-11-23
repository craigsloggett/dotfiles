---
name: create-from-scratch
description: Use when the user wants the full from-scratch flow (create an empty repo, configure it, clone it locally). For the repo alone, use create-repo.
arguments:
  - name
  - owner
---

## Arguments

Positional and optional. Invoke as `/create-from-scratch <name> <owner>`.

- `name`: name for the new repo. Blank asks.
- `owner`: owner for the new repo. Blank defaults to the authenticated user.

## Workflow

Invoke these step skills in order:

1. `create-repo` with `$name`, `$owner`; note the resulting `<owner>/<name>`.
2. `clone-repo-locally` with `<owner>/<name>`.
3. Report the repo URL and the local path at
   `~/Developer/GitHub/<owner>/<name>`.

## Rules

- A from-scratch repo starts without template scaffolding to clean up or
  initial Dependabot PRs, so this flow skips the settle, cleanup, and PR steps.
  Scaffold content yourself in the local clone.
- No release by default. Run `create-initial-release` in the clone only if the
  user asks for one.
