---
name: review-design
description: Use when the user asks for a design review of the current branch before handing it off.
disable-model-invocation: true
---

## Review Design

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
3. Delegate to the `conventions:design-reviewer` agent (via the Agent tool).
   Pass only the scope. That is the repo root, the current branch, the default
   branch, and any range or file list the user named. Without one, say the
   scope is the full branch delta including uncommitted and untracked changes.
   When the delta changes more than one package, start one reviewer per
   package in a single message. Give each its package as the scope and say the
   rest of the delta is there to read.
4. Wait for every report. Relay each verdict, every finding with its cost and
   simpler shape, and the "Not read in full" line as returned.
5. Stop. Do not restructure anything unless the user asks.

### Gotchas

- Never pass the reviewer your own read of the change, what it should do, or
  what you suspect. A reviewer handed a hypothesis tends to confirm it, so it
  must derive the design from the code.
- A reviewer can end without sending its report, at its turn limit or before. It
  has still done the reading. Resume it with SendMessage and ask for the report,
  because a new reviewer starts the reading again.
- One reviewer does not get through a large branch. A code review of four new
  packages ran out of turns before it reported, and step 3 splits by package
  for that reason. Each reviewer still needs the rest of the delta, because a
  pass-through only shows across a package boundary.
- FIX means the reviewer could name a simpler shape. It does not mean the
  branch has defects.
- Do not soften, merge, or re-rank findings. If you disagree with one, say so
  after relaying it, and keep the two apart. The usual reason to disagree is a
  shape the repo forces, such as an interface it defines, a wire format, or a
  signature a framework fixes.
- A SHIP that leaves packages unread is not a SHIP for the branch. Count the
  changed files yourself and check them against the "Not read in full" line
  before relaying the verdict.
- Acting on a finding moves code, and a defect review of the old shape no
  longer covers it. Run `/conventions:review-branch` again afterwards.
- The `save.sh` hook runs on every Bash call, the reviewer's included. A failing
  lint check feeds its errors into the review, and a `golangci-lint` config with
  `fix: true` rewrites files mid-review. Run behind green lint. If the working
  tree differs from the one above after the review, tell the user which files
  changed.
