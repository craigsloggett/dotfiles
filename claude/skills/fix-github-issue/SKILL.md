---
name: Fix GitHub Issue
description: Fetch a GitHub issue, analyze it, implement a fix, and create a PR.
---

## Workflow

1. **Fetch the issue** using `gh issue view <number>` to get the full description, labels, and comments.

2. **Create a branch** named `fix/<issue-number>-<short-description>` from the default branch.

3. **Analyze the codebase** to understand the relevant code. Read related files, trace the code path, and identify the root cause.

4. **Implement the fix** with the minimum changes needed. Follow existing patterns and conventions per CLAUDE.md.

5. **Run tests and linters** to verify the fix:
   - Look for a `Makefile` first. Use `make test` and `make lint` if available.
   - Otherwise, detect the project type and run the appropriate commands:
     - Go: `go test ./...`, `go vet ./...`
     - Terraform: `terraform validate`, `terraform fmt -check`
     - Shell: `shellcheck <script>`

6. **Commit the changes** with a message referencing the issue: `Fix #<number>: <description>`.

7. **Push the branch** and **create a PR** using `gh pr create`:
   - Title: `Fix #<number>: <short description>`
   - Body: Summary of the issue, root cause, and what the fix does.
   - Link the issue in the PR body.

8. **Monitor CI** using `gh pr checks <number>` to verify the PR passes all checks.

## Rules

- Always read the issue and codebase before writing code.
- Keep changes focused on the issue. Don't fix unrelated things.
- If the issue is unclear or needs more context, ask before implementing.
- Run tests before pushing. Don't create PRs with failing tests.
