---
name: Review PR
description: Fetch a PR, review the diff for quality and correctness, and provide feedback.
---

## Workflow

1. **Fetch the PR** using `gh pr view <number>` to get the title, description, and metadata.

2. **Review the diff** using `gh pr diff <number>`. Analyze changes for:
   - **Correctness** — Does the code do what it claims? Are there logic errors, off-by-one mistakes, or unhandled edge cases?
   - **Tests** — Are new or changed behaviors covered by tests? Are existing tests updated if behavior changed?
   - **Style** — Does the code follow project conventions per CLAUDE.md? Is naming consistent?
   - **Security** — Are there injection risks, unvalidated inputs, or exposed secrets?
   - **Simplicity** — Could the change be simpler? Is there unnecessary complexity or over-engineering?

3. **Check CI status** using `gh pr checks <number>` to see if automated checks pass.

4. **Read related code** if needed. Don't review the diff in isolation — understand the context around the changes.

5. **Provide feedback** as a structured review:
   - Start with a summary: what the PR does and whether it looks good overall.
   - List specific issues with file paths and line numbers.
   - Categorize feedback as **must fix**, **suggestion**, or **nit**.
   - If the PR looks good, say so clearly.

## Rules

- Be constructive. Point out what's good, not just what's wrong.
- Focus on substance over style. Don't nitpick formatting if there's a formatter.
- If you're unsure about something, flag it as a question rather than a demand.
- Don't approve PRs with failing CI checks without understanding why they fail.
