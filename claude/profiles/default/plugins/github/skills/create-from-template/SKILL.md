---
name: create-from-template
description: >-
  Run the full from-template flow (create the repo, clone, release, settle PRs,
  clean up, open a PR).
when_to_use: >-
  Use when the user wants a new repo set up end to end from a template. For the
  repo alone, use create-repo-from-template.
arguments:
  - template
  - name
  - owner
---

## Arguments

Positional and optional, passed to the create step. Invoke as
`/create-from-template <template> <name> <owner>`.

- `template`: owner/repo of the template. Blank lists accessible templates and
  prompts.
- `name`: name for the new repo. Blank asks.
- `owner`: owner for the new repo. Blank defaults to the authenticated user.

## Workflow

Invoke these step skills in order:

1. `create-repo-from-template` with `$template`, `$name`, `$owner`. Note the
   resulting `<owner>/<name>`.
2. `clone-repo-locally` with `<owner>/<name>`.
3. `create-initial-release` with `<owner>/<name>`.
4. `settle-open-prs` in `~/Developer/GitHub/<owner>/<name>`.
5. `cleanup-template-scaffolding` in `~/Developer/GitHub/<owner>/<name>`.
6. `open-pr` in `~/Developer/GitHub/<owner>/<name>` with branch
   `clean-up-template-scaffolding` and title
   `chore: Clean up template scaffolding`.

## Rules

- Keep this order. The release tags the pristine template before cleanup, PRs
  settle before cleanup so it starts from the merged default branch, and cleanup
  lands as its own PR because the ruleset blocks direct pushes to the default
  branch.
