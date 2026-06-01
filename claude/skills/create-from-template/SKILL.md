---
name: create-from-template
description: Use when the user asks to create a new GitHub repo from a template, clone it locally, apply standard repo settings, and hand off to the clean-scaffold skill.
arguments:
  - name: template
    description: owner/repo of the template. If omitted, the skill lists the user's accessible template repos via gh and prompts.
    required: false
  - name: name
    description: Name for the new repo. If omitted, the skill asks.
    required: false
  - name: owner
    description: Owner for the new repo. Defaults to the authenticated user from `gh api user --jq .login`.
    required: false
---

## Workflow

Authenticated GitHub user, for defaulting the owner:

!`gh api user --jq .login`

Existing topic vocabulary (count, name):

!`gh repo list --json repositoryTopics -L 200 | jq -r '[.[].repositoryTopics[]?.name] | group_by(.) | map("\(length)\t\(.[0])") | sort | reverse | .[]'`

Existing descriptions, tagged with their topics:

!`gh repo list --json description,repositoryTopics -L 200 | jq -r '.[] | select(.description != null and .description != "") | "[\([.repositoryTopics[]?.name] | join(","))] \(.description)"'`

1. Pre-flight. Run `gh auth status`. If it fails, hand the session back to the user to run `gh auth login`. Run `gh repo create --help` and `gh repo edit --help` once to confirm flag names before invoking them.
2. Resolve the template.
   - If `template` is given as `owner/repo`, call `gh api repos/<owner>/<repo> --jq '{is_template, full_name, description}'`. Abort if `is_template` is not `true`.
   - Otherwise, query the authenticated user with `gh repo list <user> --json name,owner,isTemplate,description -L 200`, keep only `isTemplate == true`, and present the list with name and description for the user to pick. Accept org-owned templates the user can read by also listing orgs from `gh api user/orgs --jq '.[].login'` and querying each.

3. Collect new-repo metadata.
   - Owner: default to the authenticated user above. Confirm.
   - Name: ask if not provided. Reject anything that does not match `^[A-Za-z0-9._-]+$`.
   - Visibility: default `--public`. Confirm before creating.

4. Propose topics from the existing topic vocabulary above. Match the user's invocation phrasing against the list. Examples: "composite action" or "GitHub action" becomes `composite-action`; "terraform module" or "terraform provider" becomes `terraform` (add `hashicorp` if it is a HashiCorp-product module); "vault plugin" becomes `vault`; "shell script" or "POSIX" becomes `shell`. Present the proposed topics and let the user add, remove, or override. Only accept topics outside this list if the user explicitly types them.
5. Propose a description in the style of the existing descriptions above. Write a one-sentence description that mirrors the style of the samples whose topics overlap with the proposed topics from step 4. Match length, sentence shape, capitalization, and ending punctuation. If no topic-overlapping samples exist, fall back to the overall style. Show the proposed description and the samples it was modeled on so the user can sanity-check before confirming. The user may edit it. Empty is allowed but discouraged.
6. Block on local collisions. If `~/Developer/GitHub/<owner>/<name>` already exists, stop and ask the user to rename or remove it. Never delete it automatically.
7. Create and clone.
   - `mkdir -p ~/Developer/GitHub/<owner>`.
   - From `~/Developer/GitHub/<owner>`, run:

     ```
     gh repo create <owner>/<name> \
       --template <template-owner>/<template-repo> \
       --public \
       --description "<desc>" \
       --clone
     ```

   - If `--clone` does not land the repo at `~/Developer/GitHub/<owner>/<name>`, fall back to `gh repo clone <owner>/<name> ~/Developer/GitHub/<owner>/<name>`.
   - Confirm with `git -C ~/Developer/GitHub/<owner>/<name> rev-parse HEAD`.

8. Apply repo settings defaults and topics in one `gh repo edit` call:

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

9. Create the initial pre-release. Tag the template's initial commit as `v0.0.1`:

   ```
   gh release create v0.0.1 \
     --repo <owner>/<name> \
     --prerelease \
     --title v0.0.1 \
     --notes "Initial release"
   ```

   Flags verified via `gh release create --help`. This runs before the clean-scaffold hand-off so `v0.0.1` marks the unmodified template state; subsequent cleanup work lands in later commits and a future release.

10. Hand off to clean-scaffold. Invoke the `clean-scaffold` skill on `~/Developer/GitHub/<owner>/<name>` so it can scan for placeholders, apply replacements, and rewrite the README.

## Rules

- Never modify or push to the template repo itself. It is read-only here.
- Topics must come from the existing corpus vocabulary unless the user explicitly types a new one. Do not invent topics.
- Descriptions are modeled on the corpus, not generated freehand. Show the samples used as the basis so the user can sanity-check the style match before confirming.
- Verify `gh` flag behavior with `--help` at runtime rather than guessing. Say "unverified" when a flag's behavior is uncertain.
