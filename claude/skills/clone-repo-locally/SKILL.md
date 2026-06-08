---
name: clone-repo-locally
description: Use when the user wants to clone a GitHub repo into the standard local location at ~/Developer/GitHub/<owner>/<name>.
arguments:
  - repo
  - dest
---

## Arguments

Positional and optional. Invoke as `/clone-repo-locally <repo> <dest>`.

- `repo`: owner/repo to clone. A bare name is prefixed with the authenticated user. Blank asks.
- `dest`: destination directory. Blank defaults to `~/Developer/GitHub/<owner>/<name>`.

## Workflow

Authenticated GitHub user, for owner-prefixing a bare repo name:

!`gh api user --jq .login`

1. Resolve `$repo` into `<owner>/<name>`; prefix a bare name with the authenticated user above. If `$repo` is blank, ask.
2. The destination is `$dest` if non-empty, else `~/Developer/GitHub/<owner>/<name>`. If it already exists, stop and ask the user to rename or remove it; never delete it.
3. Clone over SSH:
   - `mkdir -p` the destination's parent.
   - `git clone git@github.com:<owner>/<name>.git <destination>`.
4. Confirm with `git -C <destination> rev-parse HEAD`.
