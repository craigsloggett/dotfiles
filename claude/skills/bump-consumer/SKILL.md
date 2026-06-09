---
name: bump-consumer
description: Use when the user wants to re-pin a consumer repo's references to new upstream versions, whether supplied by the cascade-change hand-off or listed by the user directly.
arguments:
  - consumer
  - upstreams
---

## Arguments

Positional and optional. Invoke as `/bump-consumer <consumer> <upstreams>`.

- `consumer`: path to the consumer repo whose dependency references should be bumped. Blank asks.
- `upstreams`: list of upstreams at their new versions, each `{owner/repo, new_tag, tag_sha}`. Supplied by the cascade-change hand-off, or listed by the user when the releases were cut elsewhere. Blank asks.

## Workflow

1. Pre-flight scan. Read `$consumer`. For each upstream `owner/repo`, find all references matched on full `owner/repo` (never trailing name only). Print: "found N refs to <owner/repo> across M files," with file paths.
2. Halt on zero matches for any upstream the user expected to bump. Ask before continuing.
3. Refuse if `$consumer` is on `main` or `master`. The skill pushes to the currently-checked-out branch (assumed to be an active PR branch).
4. Rewrite refs semantically. For each match, infer the ref format from context, for example:
   - GitHub Actions: `uses: owner/repo@<sha> # <version>`
   - Terraform: `source = "..."` paired with `version = "..."`
   - npm/Go/etc.: format inferred from the manifest in use.

   Replace with the new SHA and version from `$upstreams`.
5. Show the full consumer diff. Confirm before pushing.
6. Commit and push to the consumer's currently-checked-out branch. GPG-signed, conventional commit. Never force-push.

## Rules

- Match consumer refs on full `owner/repo`, never trailing name only.
- Never `--force` push. Never push to `main` on the consumer.
- GPG-sign every commit. On signing failure, hand the session back to the user.
- No AI/Claude attribution in commit messages or PR bodies.
