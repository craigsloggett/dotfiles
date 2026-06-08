---
name: create-initial-release
description: Use when the user wants to cut the first release of a repo, defaulting to a v0.0.1 prerelease that marks the pristine template state before cleanup.
arguments:
  - repo
  - tag
  - notes
---

## Arguments

Positional and optional. Invoke as `/create-initial-release <repo> <tag> <notes>`.

- `repo`: owner/repo to release. Blank defaults to the current directory's repo.
- `tag`: release tag. Blank defaults to `v0.0.1`.
- `notes`: release notes. Blank defaults to `Initial release`. Quote multi-word notes.

Prerelease is on by default; ask for a full release to drop it.

## Workflow

1. Pre-flight. Run `gh release create --help` once to confirm flag names before invoking them. If `gh auth status` fails, hand the session back to the user to run `gh auth login`.
2. Resolve `<repo>`: use `$repo` if non-empty, else the current repo from `gh repo view --json nameWithOwner --jq .nameWithOwner`.
3. Create the release, defaulting `<tag>` to `$tag` or `v0.0.1` and `<notes>` to `$notes` or `Initial release`:

   ```
   gh release create <tag> \
     --repo <repo> \
     --prerelease \
     --title <tag> \
     --notes "<notes>"
   ```

   Drop `--prerelease` when the user asks for a full release.

## Rules

- The default `v0.0.1` prerelease marks the unmodified template state, so cut it before any cleanup commits land on the default branch. Later work goes in subsequent commits and a future release.
- Verify `gh` flag behavior with `--help` at runtime rather than guessing.
