---
name: fix-github-issue
description: Use when the user asks to fix, resolve, or work on a GitHub issue by number.
---

## Workflow

1. Fetch the issue with `gh issue view <number>` to get the description, labels, and comments.

2. Create a branch named `fix/<issue-number>-<short-description>` from the default branch.

3. Analyze the codebase to understand the relevant code. Read related files, trace the code path, and identify the root cause.

4. Implement the fix with the minimum changes needed. Follow existing patterns and conventions per CLAUDE.md.

5. Run tests and linters. Prefer `make test` and `make lint` if a `Makefile` exists. Otherwise by project type:
   - Go: `go test ./...`, `go vet ./...`
   - Terraform: `terraform validate`, `terraform fmt -check`
   - Shell: `shellcheck <script>`

6. Commit with a message referencing the issue: `Fix #<number>: <Description>` (capitalize the first word after the colon).

7. Push the branch and create a PR using `gh pr create`:
   - Title: `Fix #<number>: <Description>` (capitalize the first word after the colon)
   - Body: summary of the issue, root cause, and what the fix does. Link the issue in the body.

8. Monitor CI with `gh pr checks <number>` to verify the PR passes all checks.

## Rules

- Keep changes focused on the issue. Surface unrelated problems separately.
- If the issue is unclear or needs more context, ask before implementing.
