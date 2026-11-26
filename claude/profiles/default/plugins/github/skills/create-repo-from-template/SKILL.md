---
name: create-repo-from-template
description: >-
  Create a new GitHub repo from a template and set it up end to end, from
  configuring and cloning it to opening the PR that cleans up the template
  scaffolding.
when_to_use: >-
  Use when the user wants a new repo from a template, such as a new composite
  action, Terraform module, or Go project. For a repo without a template, use
  create-repo.
arguments:
  - template
  - name
  - owner
---

## Arguments

Positional and optional. Invoke as
`/create-repo-from-template <template> <name> <owner>`.

- `template`: owner/repo of the template, or a kind from the table below. Blank
  lists accessible templates and prompts.
- `name`: name for the new repo. Blank asks.
- `owner`: owner for the new repo. Blank defaults to the authenticated user.

## Templates

| Kind                     | Template                                           |
| ------------------------ | -------------------------------------------------- |
| Composite action         | `craigsloggett-lab/composite-action-template`      |
| Terraform module         | `craigsloggett-lab/terraform-module-template`      |
| Terraform root module    | `craigsloggett-lab/terraform-root-module-template` |
| Terraform provider       | `craigsloggett-lab/terraform-provider-template`    |
| Go project               | `craigsloggett-lab/go-project-template`            |
| HCP Terraform management | `craigsloggett/hcp-terraform-management-template`  |

## Workflow

Authenticated GitHub user, for defaulting the owner:

!`gh api user --jq .login`

!`${CLAUDE_SKILL_DIR}/../../scripts/repo-corpus.sh`

1. Pre-flight. Run `gh auth status`. If it fails, hand back to the user to run
   `gh auth login`.
2. Resolve the template into `<template>` (full `owner/repo`).
   - If `$template` or the request names a kind in the table above, use its
     template.
   - If `$template` is an `owner/repo`, call
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
7. Invoke `clone-repo-locally` with `<owner>/<name>`.
8. Cut the first release, a prerelease of the pristine template:

   ```sh
   gh release create v0.0.1 \
     --repo <owner>/<name> \
     --prerelease \
     --title v0.0.1 \
     --notes "Initial release"
   ```

9. Invoke `merge-dependabot` in `~/Developer/GitHub/<owner>/<name>`.
10. Invoke `cleanup-template-scaffolding` in the same directory.
11. Invoke `open-pr` in the same directory with branch
    `clean-up-template-scaffolding` and title
    `chore: Clean up template scaffolding`.
12. Report the repo URL, the local path, the release tag, and the cleanup PR
    URL.

## Rules

- Keep the order of steps 7 to 11. The release tags the pristine template
  before cleanup, the Dependabot PRs merge before cleanup so it starts from the
  merged default branch, and cleanup lands as its own PR because the ruleset
  blocks direct pushes to the default branch.
- Never change or push to the template repo. Treat it as read-only.
- The new repo's owner and the template's owner are independent. Never reuse the
  template's owner for the new repo unless the user asks.
- Do not use `gh repo create --template`. Its GraphQL clone fails for a
  fine-grained PAT when the template's owner differs from the new repo's owner,
  and `/generate` works with read access.
- If the API rejects the ruleset's `bypass_actors`, surface the error rather
  than guessing another actor id.
- Dependabot opens PRs asynchronously on a new repo, so step 9 merges whatever
  is open at the time. Run `merge-dependabot` again if more appear later.
