---
name: Cascade Bump
description: Apply a change concurrently across a list of versioned upstream repos via auto-merging PRs, wait for new releases, then bump references in a consumer repo to pin the new versions.
arguments:
  - name: upstream-repos
    description: Either an explicit list of upstream repo paths/identifiers, or a discovery description (e.g., "all action repos in ~/Developer/GitHub/craigsloggett that define emit_state_log()"). When a description is given, the skill resolves it to a concrete list and confirms with the user before proceeding.
    required: true
  - name: consumer-repo
    description: Path to the consumer repo whose dependency references should be bumped after release.
    required: true
  - name: change
    description: Description of the change to apply to each upstream repo (provided in the invocation prompt).
    required: true
---

## Workflow

### Phase 0: Resolve the upstream list

1. **If `upstream-repos` is an explicit list,** use it as-is.
2. **If it is a discovery description,** resolve it to a concrete list:
   - Identify the scope (e.g., a parent directory) from the description.
   - Use `grep`, `find`, or read repo contents to identify the repos that match the predicate.
   - Match only locally cloned git repositories. Do not invent repos.
3. **Present the resolved list to the user with file paths.** Confirm before fanning out. Stop and ask if zero matches, or if the count is suspicious (e.g., the description implied "a few" but matched dozens).

### Phase 1: Canonical preview

Pick one upstream repo from the resolved list as the canonical example.

1. **Sync main.** `git checkout main && git pull && git gone`. Refuse if the working tree is dirty.
2. **Apply the change.** Locate the change site semantically per the invocation description and make the minimal edit. Do not expand scope.
3. **Show the diff** to the user and confirm it matches the invocation's intent. This is the only per-edit review; the same change pattern is applied to all remaining repos by subagents.
4. **Revert the edit.** `git restore .` so the canonical repo starts Phase 2 from a clean main, like every other repo.

### Phase 2: Concurrent fan-out

Spawn one subagent per upstream repo in a **single tool-call batch** so they run in parallel. Each subagent owns its repo's pipeline end-to-end.

**Per-subagent pipeline:**

1. **Sync main.** `git checkout main && git pull && git gone`. Abort if the working tree is dirty.
2. **Apply the change.** Same semantic edit as the canonical preview. Do not expand scope.
3. **Branch, commit, push.** Create a branch named `cascade/<short-kebab-slug-of-change>`. Commit with a conventional-commit subject derived from the change description (imperative, under 70 chars, no trailing period, GPG-signed). Push.
4. **Open the PR.** `gh pr create` with a one-line body summarizing the change. Capture the PR number.
5. **Watch checks.** `gh pr checks <number> --watch`.
6. **On pass:** inspect allowed merge styles via `gh api repos/<owner>/<repo>` (`merge_commit_allowed`, `squash_merge_allowed`, `rebase_merge_allowed`). Merge with the repo's default style using the matching `--merge | --squash | --rebase` flag. Delete the branch.
7. **Locate the release workflow.** Read `.github/workflows/`; identify the workflow that produces a tag/release on push to main. If ambiguous, abort and report rather than guessing.
8. **Watch the release run.** `gh run list --branch main --workflow <file> --limit 5` to find the run triggered by the merge commit; `gh run watch <run-id>`.
9. **Capture the new tag.** `git fetch --tags`. Find the newest tag whose commit equals the merge commit. Record `<tag>` and `git rev-parse <tag>`.

**Subagent contract:**

- Self-contained: the subagent prompt must include the full repo path, the change description, the branch name slug, and the commit subject. No shared state assumed.
- Never prompt the user. On any blocking ambiguity (e.g., multiple plausible release workflows, GPG signing failure, dirty tree), abort the subagent and report.
- Return a structured result: `{repo, pr_number, merge_sha, new_tag, tag_sha}` on success, or `{repo, phase, error_summary}` on failure.

### Phase 3: Aggregate

1. **Collect subagent results.** Build the list of `{repo, new_tag, tag_sha}` from successes.
2. **Halt on any failure.** Surface the failed repos, the phase each failed in, and the error excerpt. Do not start Phase 4 until the user resolves.

### Phase 4: Bump the consumer

1. **Pre-flight scan.** Read the consumer repo. For each upstream `owner/repo`, find all references matched on full `owner/repo` (never trailing name only). Print: "found N refs to <owner/repo> across M files," with file paths.
2. **Halt on zero matches** for any upstream the user expected to bump. Ask before continuing.
3. **Refuse if the consumer is on `main` or `master`.** The skill pushes to the currently-checked-out branch (assumed to be an active PR branch).
4. **Rewrite refs semantically.** For each match, infer the ref format from context, for example:
   - GitHub Actions: `uses: owner/repo@<sha> # <version>`
   - Terraform: `source = "..."` paired with `version = "..."`
   - npm/Go/etc.: format inferred from the manifest in use.

   Replace with the new SHA and version captured in Phase 3.
5. **Show the full consumer diff.** Confirm before pushing.
6. **Commit and push to the consumer's currently-checked-out branch.** GPG-signed, conventional commit. Never force-push.

## Rules

- When `upstream-repos` is a discovery description, always confirm the resolved list with the user before any edits, commits, or pushes.
- The canonical preview is the only per-edit human review. Do not add per-repo confirmation gates inside the concurrent fan-out — subagents cannot prompt the user.
- Spawn all Phase 2 subagents in a single tool-call batch so they run in parallel. Phase 4 (consumer bump) is always serial on the main agent.
- Concurrent commits hit the GPG agent simultaneously. If any subagent's commit fails to sign, abort that subagent and surface the failure so the user can unlock the key before retrying.
- Never silently skip a failed subagent. Halt before Phase 4 if any upstream pipeline failed.
- The `change` argument is the source of truth for what to edit. Do not expand scope beyond it.
- GPG-sign every commit. On signing failure, hand the session back to the user.
- Never `--force` push. Never push to `main` on the consumer.
- Match consumer refs on full `owner/repo`, never trailing name only.
- Use the upstream repo's default merge style; do not override.
- If the release workflow can't be auto-detected, the subagent aborts and reports; the main agent surfaces the question to the user.
- No AI/Claude attribution in commit messages or PR bodies.
