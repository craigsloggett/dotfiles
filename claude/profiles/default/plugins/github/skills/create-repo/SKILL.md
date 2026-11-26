---
name: create-repo
description: >-
  Create and configure a new empty GitHub repo (not from a template), and clone
  it locally when the user wants a local copy.
when_to_use: >-
  Use when the user wants a new repo without a template. For a repo from a
  template, use create-from-template.
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

!`${CLAUDE_SKILL_DIR}/../../scripts/repo-corpus.sh`

1. Pre-flight. Run `gh auth status`. If it fails, hand back to the user to run
   `gh auth login`.
2. Resolve new-repo metadata.
   - Owner `<owner>`: `$owner` if non-empty, else the authenticated user.
     Confirm.
   - Name `<name>`: `$name` if non-empty, else ask. Reject anything not matching
     `^[A-Za-z0-9._-]+$`.
   - Visibility: default public. Use private only when asked.
3. Propose topics and a description from the corpus above.
   - Topics come from the vocabulary, matched to the user's phrasing. Let the
     user add, remove, or override them, and accept a topic outside the
     vocabulary only if the user types it. "Composite action" or "GitHub
     action" becomes `composite-action`, "Terraform module/provider" becomes
     `terraform`, a HashiCorp product also gets `hashicorp`, "vault plugin"
     becomes `vault`, and "shell script" or "POSIX" becomes `shell`.
   - The description is one sentence in the style of the descriptions whose
     topics overlap the proposed ones. Show the samples you used so the user
     can check them. Allow an empty description but discourage it.
4. Create the repo with an initial commit so the default branch exists:

   ```sh
   gh repo create <owner>/<name> \
     --public \
     --description "<desc>" \
     --add-readme
   ```

   Use `--private` for private, and omit `--description` if empty.
5. Configure it with
   `${CLAUDE_SKILL_DIR}/../../scripts/configure-repo.sh <owner>/<name> <topics>`,
   where `<topics>` is a comma-separated list (omit it when the list is empty).
   The script applies the settings, the squash-merge messages, the topics, and
   the default branch ruleset. If it fails, stop and surface its error.
6. If the user wants a local copy, invoke `clone-repo-locally` with
   `<owner>/<name>`. Ask when the request doesn't say.
7. Report the repo URL, and the local path if you cloned it.

## Rules

- `--add-readme` seeds an initial commit so the default branch exists. Without
  it the ruleset POST in the script doesn't have a branch to target.
- A repo without a template doesn't start with scaffolding to clean up or
  initial Dependabot PRs, so this skill skips those steps. Scaffold content
  yourself in the local clone.
- No release by default. Run `create-initial-release` only if the user asks for
  one.
- If the API rejects the ruleset's `bypass_actors`, surface the error rather
  than guessing another actor id.
