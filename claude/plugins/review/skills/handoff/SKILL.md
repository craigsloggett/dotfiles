---
name: handoff
description: >-
  Review the current branch at handoff by running the consistency, code, and
  design reviewer agents in parallel and relaying each verdict.
disable-model-invocation: true
---

## Handoff Review

Current branch: !`git branch --show-current`

Default branch: !`git symbolic-ref --short refs/remotes/origin/HEAD`

Working tree: !`git status --short`

### Steps

1. Stop if the current branch is the default branch, because the delta is
   empty.
2. Group the changed files by package, from
   `git diff --name-only $(git merge-base HEAD <default>)...HEAD` and
   `git ls-files -o --exclude-standard`. Skip this when the user named a range
   or file list.
3. In a single message, start the `review:consistency-reviewer` agent, the
   `review:code-reviewer` agent, and one `review:design-reviewer`
   agent per changed package. Pass each only the scope. That is the repo root,
   the current branch, the default branch, and any range or file list the user
   named. Without one, say the scope is the full branch delta including
   uncommitted and untracked changes. Give each design reviewer its package as
   the scope and say the rest of the delta is there to read. If the user asks
   for only some of the reviewers, start only those.
4. Wait for every report. Relay each verdict and every finding as returned,
   grouped by reviewer, with each design reviewer's "Not read in full" line.
5. Stop. Do not fix anything unless the user asks.

### Gotchas

- Never pass a reviewer your own read of the change, what it should do, or what
  you suspect. A reviewer handed a hypothesis tends to confirm it.
- The reviewers split the work. The consistency reviewer owns `rules/*.md` and
  sibling gaps, the code reviewer owns defects, and the design reviewer owns
  structure. If two report the same line, relay both and say they overlap.
- A reviewer can end without sending its report. It has still done the
  reading, so resume it with SendMessage and ask for the report.
- One design reviewer does not get through a large branch. A review of four new
  packages ran out of turns before it reported, so step 3 starts one per
  package. Each still needs the rest of the delta, because a pass-through
  only shows across a package boundary.
- A design SHIP that leaves packages unread is not a SHIP for the branch. Check
  the changed files against each "Not read in full" line before relaying it.
- A design FIX means the reviewer could name a simpler shape. It does not mean
  the branch has defects.
- Do not soften, merge, or re-rank findings. If you disagree with one, say so
  after relaying it, and keep the two apart.
- The `save.sh` hook runs on every Bash call, each reviewer's included. A
  failing lint check feeds its errors into every review, so run behind green
  lint. If the working tree differs from the one above afterwards, tell the
  user which files changed.
- Acting on a finding moves code. Run this skill again afterwards.
