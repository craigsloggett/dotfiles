---
name: review-branch
description: Use when the user asks for a code review of the current branch before handing it off.
disable-model-invocation: true
---

## Review Branch

Current branch: !`git branch --show-current`

Default branch: !`git symbolic-ref --short refs/remotes/origin/HEAD`

Working tree: !`git status --short`

### Steps

1. Stop if the current branch is the default branch; there is no delta to
   review.
2. Delegate to the `conventions:code-reviewer` agent (via the Agent tool)
   in the foreground. Pass only the scope: the repo root, the current branch,
   the default branch, and any range or file list the user named. Without one,
   say the scope is the full branch delta including uncommitted and untracked
   changes.
3. Relay the verdict and every finding as returned.
4. Stop. Do not fix anything unless the user asks.

### Gotchas

- Never pass the reviewer your own read of the change, what it is meant to do,
  or what you suspect. A reviewer handed a hypothesis tends to confirm it; it
  must derive intent from the code.
- The `save.sh` hook runs on every Bash call, the reviewer's included. A failing
  lint check feeds its errors into the review, and a golangci-lint config with
  `fix: true` rewrites files mid-review. Run behind green lint. If the working
  tree differs from the one above after the review, tell the user which files
  changed.
- Do not soften, merge, or re-rank findings. If you disagree with one, say so
  after relaying it, and keep the two apart.
