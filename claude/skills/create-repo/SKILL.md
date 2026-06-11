---
name: create-repo
description: Use when the user wants to create and configure a new empty GitHub repo (not from a template), without cloning it locally or cutting a release.
arguments:
  - name
  - owner
---

## Arguments

Positional and optional. Invoke as `/create-repo <name> <owner>`.

- `name`: name for the new repo. Blank asks.
- `owner`: owner for the new repo. Blank defaults to the authenticated user.

## Workflow

Authenticated GitHub user, for defaulting the owner:

!`gh api user --jq .login`

Existing topic vocabulary (count, name):

!`gh repo list --json repositoryTopics -L 200 | jq -r '[.[].repositoryTopics[]?.name] | group_by(.) | map("\(length)\t\(.[0])") | sort | reverse | .[]'`

Existing descriptions, tagged with their topics:

!`gh repo list --json description,repositoryTopics -L 200 | jq -r '.[] | select(.description != null and .description != "") | "[\([.repositoryTopics[]?.name] | join(","))] \(.description)"'`

1. Pre-flight. Run `gh auth status`; if it fails, hand back to the user to run `gh auth login`.
2. Resolve new-repo metadata.
   - Owner `<owner>`: `$owner` if non-empty, else the authenticated user. Confirm.
   - Name `<name>`: `$name` if non-empty, else ask. Reject anything not matching `^[A-Za-z0-9._-]+$`.
   - Visibility: default public; use private only when asked.
3. Propose topics from the vocabulary above, matching the user's phrasing. Examples: "composite action" or "GitHub action" becomes `composite-action`; "terraform module/provider" becomes `terraform` (add `hashicorp` for a HashiCorp product); "vault plugin" becomes `vault`; "shell script" or "POSIX" becomes `shell`. Let the user add, remove, or override; accept topics outside the vocabulary only if the user explicitly types them.
4. Propose a one-sentence description in the style of the corpus samples whose topics overlap the proposed ones; show the samples used so the user can sanity-check. Empty is allowed but discouraged.
5. Create the repo with an initial commit so the default branch exists (the ruleset, and any later release, need a branch to target):

   ```
   gh repo create <owner>/<name> \
     --public \
     --description "<desc>" \
     --add-readme
   ```

   Use `--private` for private; omit `--description` if empty.
6. Apply settings and topics:

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

   `--add-topic` takes a comma-separated list; omit it if no topics. If `gh` rejects a flag, stop and surface the error.
7. Create the default branch ruleset (every repo gets this). Write the body to a temp file (`mktemp`) and post it with `gh api -X POST repos/<owner>/<name>/rulesets --input <file>`:

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
8. Report the created `<owner>/<name>`.

## Rules

- `--add-readme` seeds an initial commit so the default branch exists; without it the ruleset POST has no branch to target.
