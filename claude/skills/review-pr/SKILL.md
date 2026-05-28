---
name: review-pr
description: Use when the user asks to review a pull request, check a PR's diff for quality or correctness, or give feedback on someone else's changes.
---

## Workflow

1. Fetch the PR with `gh pr view <number>` to get the title, description, and metadata.

2. Review the diff with `gh pr diff <number>`. Analyze for:
   - Correctness: does the code do what it claims? Logic errors, off-by-one mistakes, unhandled edge cases.
   - Tests: are new or changed behaviors covered? Are existing tests updated if behavior changed?
   - Style: does the code follow project conventions per CLAUDE.md? Is naming consistent?
   - Security: injection risks, unvalidated inputs, exposed secrets.
   - Simplicity: could the change be simpler? Unnecessary complexity or over-engineering.

3. Check CI status with `gh pr checks <number>`.

4. Read related code to understand context around the changes. Do not review the diff in isolation.

5. Provide feedback as a structured review:
   - Start with a summary: what the PR does and whether it looks good overall.
   - List specific issues with file paths and line numbers.
   - Categorize feedback as must fix, suggestion, or nit.
   - If the PR looks good, say so clearly.

## Rules

- Focus on substance over style. Do not nitpick formatting if there is a formatter.
- If you are unsure about something, flag it as a question rather than a demand.
- Do not approve PRs with failing CI checks without understanding why they fail.
