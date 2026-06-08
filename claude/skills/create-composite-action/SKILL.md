---
name: create-composite-action
description: Use when the user wants to create a new composite action repo from the standard template.
arguments:
  - name
---

## Arguments

Positional and optional. Invoke as `/create-composite-action <name>`.

- `name`: name for the new action repo. Blank asks.

## Workflow

Authenticated GitHub user, the default owner:

!`gh api user --jq .login`

1. Delegate to the `repo-scaffolder` agent (via the Agent tool): template `craigsloggett-lab/composite-action-template`, name `$name`, owner the authenticated user above, visibility public, topic `composite-action`. Wait for its summary; if it reports a collision or failure, surface that and stop.
2. Invoke `settle-open-prs` in `~/Developer/GitHub/<owner>/$name`.
3. Invoke `cleanup-template-scaffolding` in the local clone.
4. Invoke `open-pr` in the local clone with branch `clean-up-template-scaffolding` and title `chore: Clean up template scaffolding`.
5. Report the repo URL, local path, and cleanup PR URL.
