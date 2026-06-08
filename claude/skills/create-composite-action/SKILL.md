---
name: create-composite-action
description: Use when the user wants to create a new composite action repo from the standard template. Delegates the create, clone, and release to the repo-scaffolder agent in isolation, then settles open PRs, cleans up scaffolding, and opens a cleanup PR.
arguments:
  - name
---

## Arguments

Positional and optional. Invoke as `/create-composite-action <name>`.

- `name`: name for the new action repo. Blank asks.

## Workflow

Authenticated GitHub user, the default owner:

!`gh api user --jq .login`

1. Delegate to the `repo-scaffolder` agent (via the Agent tool) with these inputs: template `craigsloggett-lab/composite-action-template`, name `$name`, owner the authenticated user above, visibility public, topic `composite-action`. Wait for its summary. If it reports a collision or failure, surface that and stop.
2. Invoke the `settle-open-prs` skill on the local clone at `~/Developer/GitHub/<owner>/$name` so it fixes any dependabot PR titles, merges the green ones, and pulls the default branch locally.
3. Invoke the `cleanup-template-scaffolding` skill on the local clone so it cleans up placeholders and writes a fresh README.
4. Invoke the `open-pr` skill on the local clone with branch `clean-up-template-scaffolding` and title `chore: Clean up template scaffolding`, so the cleanup lands on a branch and pull request rather than dirtying the working tree.
5. Report the repo URL, local path, and the cleanup PR URL. The directory is ready to start implementing the action.
