---
name: Cascade Bump
description: Apply a change across a list of versioned upstream repos via auto-merging PRs, wait for new releases, then bump references in a consumer repo to pin the new versions.
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

### Phase 1: Fan out the change

For each upstream repo, sequentially:

1. **Sync main.** `git checkout main && git pull && git gone`. Refuse if the working tree is dirty.
2. **Apply the change.** Locate the change site semantically per the invocation description and make the minimal edit. Do not expand scope.
3. **Diff check.** Show the diff. Confirm it matches the invocation's intent and has not sprawled into unrelated files.
4. **Branch, commit, push.** Create a branch named `cascade/<short-kebab-slug-of-change>`. Commit with a conventional-commit subject derived from the change description (imperative, under 70 chars, no trailing period, GPG-signed). Push.
5. **Open the PR.** `gh pr create` with a one-line body summarizing the change. Capture the PR number.

### Phase 2: Auto-merge on green

For each PR, sequentially:

1. **Watch checks.** `gh pr checks <number> --watch`.
2. **On pass:** inspect the repo's allowed merge styles via `gh api repos/<owner>/<repo>` (`merge_commit_allowed`, `squash_merge_allowed`, `rebase_merge_allowed`). Merge with the repo's default style using the matching `--merge | --squash | --rebase` flag. Delete the branch.
3. **On any failing check:** capture failing job names and a short excerpt. Halt the run. Do not proceed to Phase 3 or Phase 4 for any repo until the user resolves.

### Phase 3: Wait for release

For each successfully merged repo:

1. **Locate the release workflow.** Read `.github/workflows/`; identify the workflow that produces a tag/release on push to main. If multiple candidates exist or none is obvious, ask the user.
2. **Watch the run.** `gh run list --branch main --workflow <file> --limit 5` to find the run triggered by the merge commit; `gh run watch <run-id>`.
3. **Capture the new tag.** `git fetch --tags`. Find the newest tag whose commit equals the merge commit. Record `<tag>` and `git rev-parse <tag>`.
4. **On release-workflow failure:** capture and surface; halt.

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
- Process upstream repos one at a time. Surface failures early; never silently skip.
- The `change` argument is the source of truth for what to edit. Do not expand scope beyond it.
- GPG-sign every commit. On signing failure, hand the session back to the user.
- Never `--force` push. Never push to `main` on the consumer.
- Match consumer refs on full `owner/repo`, never trailing name only.
- Use the upstream repo's default merge style; do not override.
- If the release workflow can't be auto-detected, ask the user which workflow signals "release published."
- No AI/Claude attribution in commit messages or PR bodies.
