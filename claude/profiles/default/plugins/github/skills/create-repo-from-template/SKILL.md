---
name: create-repo-from-template
description: >-
  Create and configure a new GitHub repo from a template, without cloning it
  locally or cutting a release.
when_to_use: >-
  Use when the user wants only the repo created from a template. For the full
  flow, use create-from-template.
arguments:
  - template
  - name
  - owner
---

## Arguments

Positional and optional. Invoke as
`/create-repo-from-template <template> <name> <owner>`.

- `template`: owner/repo of the template. Blank lists accessible templates and
  prompts.
- `name`: name for the new repo. Blank asks.
- `owner`: owner for the new repo. Blank defaults to the authenticated user.

## Workflow

Authenticated GitHub user, for defaulting the owner:

!`gh api user --jq .login`

!`${CLAUDE_SKILL_DIR}/../../scripts/repo-corpus.sh`

1. Pre-flight. Run `gh auth status`. If it fails, hand back to the user to run
   `gh auth login`.
2. Resolve the template into `<template>` (full `owner/repo`).
   - If `$template` is non-empty, call
     `gh api repos/$template --jq '{is_template, full_name, description}'`.
     Abort if `is_template` is not `true`.
   - Otherwise, list the user's templates with
     `gh repo list <user> --json name,owner,isTemplate,description -L 200` (keep
     `isTemplate == true`) plus org templates from
     `gh api user/orgs --jq '.[].login'`, and let the user pick.
3. Resolve new-repo metadata.
   - Owner `<owner>`: `$owner` if non-empty, else the authenticated user.
     Confirm.
   - Name `<name>`: `$name` if non-empty, else ask. Reject anything not matching
     `^[A-Za-z0-9._-]+$`.
   - Visibility: default public. Use private only when asked.
4. Propose topics and a description from the corpus above.
   - Topics come from the vocabulary, matched to the user's phrasing. Let the
     user add, remove, or override them, and accept a topic outside the
     vocabulary only if the user types it. "Composite action" or "GitHub
     action" becomes `composite-action`, "Terraform module/provider" becomes
     `terraform`, a HashiCorp product also gets `hashicorp`, "vault plugin"
     becomes `vault`, and "shell script" or "POSIX" becomes `shell`.
   - The description is one sentence in the style of the descriptions whose
     topics overlap the proposed ones. Show the samples you used so the user
     can check them. Allow an empty description but discourage it.
5. Create the repo with the REST generate endpoint:

   ```sh
   gh api -X POST repos/<template>/generate \
     -f owner=<owner> \
     -f name=<name> \
     -f description="<desc>" \
     -F private=false
   ```

   Set `-F private=true` for private, and omit `-f description` if empty.
6. Configure it with
   `${CLAUDE_SKILL_DIR}/../../scripts/configure-repo.sh <owner>/<name> <topics>`,
   where `<topics>` is a comma-separated list (omit it when the list is empty).
   The script applies the settings, the squash-merge messages, the topics, and
   the default branch ruleset. If it fails, stop and surface its error.
7. Report the created `<owner>/<name>`.

## Rules

- Never change or push to the template repo. Treat it as read-only.
- The new repo's owner and the template's owner are independent. Never reuse the
  template's owner for the new repo unless the user asks.
- Do not use `gh repo create --template`. Its GraphQL clone fails for a
  fine-grained PAT when the template's owner differs from the new repo's owner,
  and `/generate` works with read access.
- If the API rejects the ruleset's `bypass_actors`, surface the error rather
  than guessing another actor id.
