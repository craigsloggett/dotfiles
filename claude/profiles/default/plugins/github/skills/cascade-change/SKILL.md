---
name: cascade-change
description: Use when the user wants to apply a change concurrently across versioned upstream repos via auto-merging PRs and release each. Hands off to bump-consumer to pin the new versions in a consumer repo.
arguments:
  - repos
  - change
  - consumer
---

## Arguments

Positional and optional. Invoke as `/cascade-change <repos> <change> <consumer>`.

- `repos`: explicit list of upstream repo paths, or a discovery description (e.g. "all action repos in `~/Developer/GitHub/craigsloggett` that define `emit_state_log()`"), resolved to a concrete list and confirmed before fan-out. Blank asks.
- `change`: description of the change to apply to each upstream repo. Blank asks.
- `consumer`: path to a consumer repo to re-pin after release. Blank stops after aggregation and reports the new tags.

## Workflow

1. Resolve the upstream list.
   - If `$repos` is an explicit list, use it as-is.
   - If it is a discovery description, identify the scope (e.g. a parent directory), then use `grep`, `find`, or repo contents to find the locally cloned git repos matching the predicate. Do not invent repos.
   - Present the resolved list with file paths and confirm before fanning out. Stop and ask on zero matches, or a suspicious count (the description implied "a few" but matched dozens).
2. Preview the change on one canonical repo from the list.
   - Sync main: `git checkout main && git pull && git gone`. Refuse if the working tree is dirty.
   - Apply the change: locate the change site semantically per `$change` and make the minimal edit. Do not expand scope.
   - Show the diff and confirm it matches the invocation's intent. This is the only per-edit review; subagents apply the same pattern to every other repo.
   - Revert: `git restore .` so the canonical repo starts the fan-out from a clean main, like every other repo.
3. Fan out one subagent per repo in a single tool-call batch so they run in parallel. Each subagent is self-contained (its prompt carries the full repo path, the change description, the branch slug, and the commit subject), never prompts the user, and runs this pipeline end-to-end:
   - Sync main: `git checkout main && git pull && git gone`. Abort if the working tree is dirty.
   - Apply the change: the same semantic edit as the canonical preview.
   - Branch `cascade/<short-kebab-slug-of-change>`, commit (conventional-commit subject from the change description, imperative, under 70 chars, no trailing period, GPG-signed), and push.
   - Open the PR with `gh pr create` and a one-line body. Capture the PR number.
   - Watch checks: `gh pr checks <number> --watch`.
   - On pass, read the allowed merge styles from `gh api repos/<owner>/<repo>` (`merge_commit_allowed`, `squash_merge_allowed`, `rebase_merge_allowed`) and merge with the repo's default using the matching `--merge | --squash | --rebase` flag. Delete the branch.
   - Locate the release workflow in `.github/workflows/` (the one that tags or releases on push to main). If ambiguous, abort and report rather than guessing.
   - Watch the release run: `gh run list --branch main --workflow <file> --limit 5` to find the run from the merge commit, then `gh run watch <run-id>`.
   - Capture the new tag: `git fetch --tags`, find the newest tag on the merge commit, and record `<tag>` and `git rev-parse <tag>`.
   - Return `{repo, pr_number, merge_sha, new_tag, tag_sha}` on success, or `{repo, step, error_summary}` on any blocking ambiguity (multiple plausible release workflows, GPG signing failure, dirty tree).
4. Aggregate the results into the `{repo, new_tag, tag_sha}` list from the successes. Halt on any failure: surface the failed repos, the step each failed at, and the error excerpt. Do not hand off until the user resolves them.
5. Hand off. If `$consumer` was provided, invoke `bump-consumer` with `$consumer` and the `{repo, new_tag, tag_sha}` list to re-pin the references. If it was omitted, report the list and stop; the user can run `bump-consumer` later.

## Rules

- Concurrent commits hit the GPG agent simultaneously. If any subagent's commit fails to sign, abort that subagent and surface the failure so the user can unlock the key before retrying.
- The canonical preview is the only per-edit human review. Subagents cannot prompt the user, so do not add per-repo confirmation gates inside the fan-out.
- Use the upstream repo's default merge style; do not override.
