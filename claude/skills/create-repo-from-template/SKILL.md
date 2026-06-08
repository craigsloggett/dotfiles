---
name: create-repo-from-template
description: Use when the user wants to create and configure a new GitHub repo from a template repo on GitHub, without cloning it locally or cutting a release.
arguments:
  - template
  - name
  - owner
---

## Arguments

Positional and optional. Invoke as `/create-repo-from-template <template> <name> <owner>`.

- `template`: owner/repo of the template. Blank lists accessible templates and prompts.
- `name`: name for the new repo. Blank asks.
- `owner`: owner for the new repo. Blank defaults to the authenticated user, independent of the template's owner.

## Workflow

Authenticated GitHub user, for defaulting the owner:

!`gh api user --jq .login`

Existing topic vocabulary (count, name):

!`gh repo list --json repositoryTopics -L 200 | jq -r '[.[].repositoryTopics[]?.name] | group_by(.) | map("\(length)\t\(.[0])") | sort | reverse | .[]'`

Existing descriptions, tagged with their topics:

!`gh repo list --json description,repositoryTopics -L 200 | jq -r '.[] | select(.description != null and .description != "") | "[\([.repositoryTopics[]?.name] | join(","))] \(.description)"'`

1. Pre-flight. Run `gh auth status`. If it fails, hand the session back to the user to run `gh auth login`. Run `gh repo edit --help` once to confirm flag names before invoking it.
2. Resolve the template into `<template>` (full `owner/repo`).
   - If `$template` is non-empty, call `gh api repos/$template --jq '{is_template, full_name, description}'`. Abort if `is_template` is not `true`.
   - Otherwise, query the authenticated user with `gh repo list <user> --json name,owner,isTemplate,description -L 200`, keep only `isTemplate == true`, and present the list with name and description for the user to pick. Accept org-owned templates the user can read by also listing orgs from `gh api user/orgs --jq '.[].login'` and querying each.
3. Resolve new-repo metadata.
   - Owner `<owner>`: use `$owner` if non-empty, else default to the authenticated user above. Independent of the template's owner either way. Confirm.
   - Name `<name>`: use `$name` if non-empty, else ask. Reject anything that does not match `^[A-Za-z0-9._-]+$`.
   - Visibility: default public. Confirm before creating. Use private only when the user asks for it.
4. Propose topics from the existing topic vocabulary above. Match the user's invocation phrasing against the list. Examples: "composite action" or "GitHub action" becomes `composite-action`; "terraform module" or "terraform provider" becomes `terraform` (add `hashicorp` if it is a HashiCorp-product module); "vault plugin" becomes `vault`; "shell script" or "POSIX" becomes `shell`. Present the proposed topics and let the user add, remove, or override. Only accept topics outside this list if the user explicitly types them.
5. Propose a description in the style of the existing descriptions above. Write a one-sentence description that mirrors the style of the samples whose topics overlap with the proposed topics from step 4. Match length, sentence shape, capitalization, and ending punctuation. If no topic-overlapping samples exist, fall back to the overall style. Show the proposed description and the samples it was modeled on so the user can sanity-check before confirming. The user may edit it. Empty is allowed but discouraged.
6. Create the repo from the template (no clone here; that is `clone-repo-locally`'s job). Use the REST generate endpoint, not `gh repo create --template`. `gh repo create --template` goes through the GraphQL `cloneTemplateRepository` path, which a fine-grained PAT cannot use when the template's owner differs from the new repo's owner: that clone needs real access to the template's owner and does not get the public-repo read exception. The REST `/generate` endpoint works with read access to the template.

   ```
   gh api -X POST repos/<template>/generate \
     -f owner=<owner> \
     -f name=<name> \
     -f description="<desc>" \
     -F private=false
   ```

   `<template>` is the full `owner/repo` from step 2. Set `-F private=true` when the user chose private. Omit `-f description` if the description is empty.

7. Apply repo settings defaults and topics in one `gh repo edit` call:

   ```
   gh repo edit <owner>/<name> \
     --enable-wiki=false \
     --enable-projects=false \
     --enable-merge-commit=false \
     --enable-rebase-merge=false \
     --allow-update-branch \
     --delete-branch-on-merge \
     --add-topic <topic1>,<topic2>,...
   ```

   `--add-topic` accepts a comma-separated list (verified via `gh repo edit --help`: `--add-topic strings`). Omit the flag entirely if the user declined to add topics. If `gh` rejects any flag, stop and surface the exact error. Do not retry with different flags.
8. Create the default branch ruleset. Every repo gets this, regardless of type. It targets the default branch, requires pull requests, linear history, and signed commits, restricts deletions, blocks force pushes, and lets the repository admin bypass. Write the body below to a temp file (`mktemp`) and post it with `gh api -X POST repos/<owner>/<name>/rulesets --input <file>`:

   ```json
   {
     "name": "default",
     "target": "branch",
     "enforcement": "active",
     "conditions": { "ref_name": { "include": ["~DEFAULT_BRANCH"], "exclude": [] } },
     "bypass_actors": [
       { "actor_id": 5, "actor_type": "RepositoryRole", "bypass_mode": "always" }
     ],
     "rules": [
       { "type": "pull_request", "parameters": { "required_approving_review_count": 0, "dismiss_stale_reviews_on_push": false, "require_code_owner_review": false, "require_last_push_approval": false, "required_review_thread_resolution": false } },
       { "type": "required_linear_history" },
       { "type": "required_signatures" },
       { "type": "deletion" },
       { "type": "non_fast_forward" }
     ]
   }
   ```

   `actor_id` 5 is the Repository admin role, a well-known value GitHub does not officially document. If the API rejects `bypass_actors`, surface the error rather than guessing another id.
9. Report the created `<owner>/<name>` so a caller can clone it (`clone-repo-locally`) and release it (`create-initial-release`).

## Rules

- Never modify or push to the template repo itself. It is read-only here.
- The new repo's owner and the template's owner are independent. Default the new owner to the authenticated user and never reuse the template's owner unless the user asks for it.
- Topics must come from the existing corpus vocabulary unless the user explicitly types a new one. Do not invent topics.
- Descriptions are modeled on the corpus, not generated freehand. Show the samples used as the basis so the user can sanity-check the style match before confirming.
- Verify `gh` flag behavior with `--help` at runtime rather than guessing. Say "unverified" when a flag's behavior is uncertain.
