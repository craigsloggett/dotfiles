---
name: create-composite-action
description: >-
  Create a new composite action repo from the standard template.
when_to_use: >-
  Use when the user wants a new composite action repo.
arguments:
  - name
---

## Arguments

Positional and optional. Invoke as `/create-composite-action <name>`.

- `name`: name for the new action repo. Blank asks.

## Workflow

Authenticated GitHub user, the default owner:

!`gh api user --jq .login`

1. Invoke `create-from-template` with template
   `craigsloggett-lab/composite-action-template`, name `$name`, and the
   authenticated user above as owner.
2. When `create-repo-from-template` proposes metadata, propose public
   visibility and the topic `composite-action`, and let the user adjust them as
   usual.
