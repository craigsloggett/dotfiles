---
name: reduce-comments
description: >-
  Remove or thin code comments, deleting by default. A comment survives only
  when removing it would cost the reader something the code cannot say.
when_to_use: >-
  Use when the user wants comments removed or thinned, whether a specific quoted
  comment, named files, or the current branch's diff.
---

## The Bar

The user's dislike of a comment is enough reason to remove it. When they point
at one, delete it. Do not defend it, negotiate, or restate its value. The tests
below guide sweeps, but taste outranks them, so when in doubt, delete.

## Scope

- Quoted comment text in the arguments means find those exact comments and
  remove them.
- Named files or directories mean sweep those.
- No arguments means sweep the comments the current branch added or modified
  (`git diff origin/<default>...HEAD`).

## Delete

- Restates the declaration or the code beneath it.
- Narrates what the next line does, or argues the change is correct
  (reviewer-talk).
- Historical or process narration, such as what it replaced or which phase added
  it.
- A doc summary that only repeats its declaration's name.
- Hedging or apology.

## Keep

- A constraint or trap the code cannot express, kept to one declarative line.
- The trade-off justification the gates require on a lint-disable directive.
- Docs a gate forces on public API (e.g. SwiftLint `missing_docs`), kept
  minimal.
- Shebangs, license headers, and structural marks (`// MARK:`), unless asked.

## Workflow

1. Collect the in-scope comments, apply the tests, and delete. Rewrite instead
   of delete only when you can shorten a keeper without losing its content.
2. Run the repo's gates if present (`make format`, then `make lint`) so wrap or
   prose rules hold for the survivors.
3. Report removals and keepers as a short list, one line each.
4. If the removals belong to an unmerged commit on the current PR branch, amend
   them into it rather than adding a cleanup commit, then force-push with lease.
   Branch commits stay subject-only.
