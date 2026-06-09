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

- `repos`: explicit list of upstream repo paths, or a discovery description (e.g. "all action repos in ~/Developer/GitHub/craigsloggett that define emit_state_log()"), resolved to a concrete list and confirmed before fan-out. Blank asks.
- `change`: description of the change to apply to each upstream repo. Blank asks.
- `consumer`: path to a consumer repo to re-pin after release. Blank stops after aggregation and reports the new tags.

## Workflow

### Phase 0: Resolve the upstream List

1. If `$repos` is an explicit list, use it as-is.
2. If it is a discovery description, resolve it to a concrete list:
   - Identify the scope (e.g., a parent directory) from the description.
   - Use `grep`, `find`, or read repo contents to identify the repos that match the predicate.
   - Match only locally cloned git repositories. Do not invent repos.
3. Present the resolved list to the user with file paths. Confirm before fanning out. Stop and ask if zero matches, or if the count is suspicious (e.g., the description implied "a few" but matched dozens).

### Phase 1: Canonical Preview

Pick one upstream repo from the resolved list as the canonical example.

1. Sync main: `git checkout main && git pull && git gone`. Refuse if the working tree is dirty.
2. Apply the change. Locate the change site semantically per `$change` and make the minimal edit. Do not expand scope.
3. Show the diff to the user and confirm it matches the invocation's intent. This is the only per-edit review; the same change pattern is applied to all remaining repos by subagents.
4. Revert the edit: `git restore .` so the canonical repo starts Phase 2 from a clean main, like every other repo.

### Phase 2: Concurrent Fan-out

Spawn one subagent per upstream repo in a single tool-call batch so they run in parallel. Each subagent owns its repo's pipeline end-to-end.

Per-subagent pipeline:

1. Sync main: `git checkout main && git pull && git gone`. Abort if the working tree is dirty.
2. Apply the change. Same semantic edit as the canonical preview.
3. Branch, commit, push. Create a branch named `cascade/<short-kebab-slug-of-change>`. Commit with a conventional-commit subject derived from the change description (imperative, under 70 chars, no trailing period, GPG-signed). Push.
4. Open the PR: `gh pr create` with a one-line body summarizing the change. Capture the PR number.
5. Watch checks: `gh pr checks <number> --watch`.
6. On pass, inspect allowed merge styles via `gh api repos/<owner>/<repo>` (`merge_commit_allowed`, `squash_merge_allowed`, `rebase_merge_allowed`). Merge with the repo's default style using the matching `--merge | --squash | --rebase` flag. Delete the branch.
7. Locate the release workflow. Read `.github/workflows/`; identify the workflow that produces a tag/release on push to main. If ambiguous, abort and report rather than guessing.
8. Watch the release run: `gh run list --branch main --workflow <file> --limit 5` to find the run triggered by the merge commit; `gh run watch <run-id>`.
9. Capture the new tag: `git fetch --tags`. Find the newest tag whose commit equals the merge commit. Record `<tag>` and `git rev-parse <tag>`.

Subagent contract:

- Self-contained: the subagent prompt must include the full repo path, the change description, the branch name slug, and the commit subject. No shared state assumed.
- Never prompt the user. On any blocking ambiguity (e.g., multiple plausible release workflows, GPG signing failure, dirty tree), abort the subagent and report.
- Return a structured result: `{repo, pr_number, merge_sha, new_tag, tag_sha}` on success, or `{repo, phase, error_summary}` on failure.

### Phase 3: Aggregate

1. Collect subagent results. Build the list of `{repo, new_tag, tag_sha}` from successes.
2. Halt on any failure. Surface the failed repos, the phase each failed in, and the error excerpt. Do not hand off until the user resolves.

### Phase 4: Hand off

1. If `$consumer` was provided, invoke the `bump-consumer` skill with `$consumer` and the `{repo, new_tag, tag_sha}` list from Phase 3 so it can re-pin the references.
2. If `$consumer` was omitted, report the captured `{repo, new_tag, tag_sha}` list and stop. The user can run `bump-consumer` later with that list.

## Rules

- Concurrent commits hit the GPG agent simultaneously. If any subagent's commit fails to sign, abort that subagent and surface the failure so the user can unlock the key before retrying.
- The canonical preview is the only per-edit human review. Subagents cannot prompt the user, so do not add per-repo confirmation gates inside the concurrent fan-out.
- Use the upstream repo's default merge style; do not override.
