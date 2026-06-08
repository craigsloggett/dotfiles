---
name: cleanup-template-scaffolding
description: Use when the user asks to clean up a repo cloned from a template, replace placeholder values, or write a fresh README for a newly scaffolded project.
---

## Workflow

Authenticated GitHub login, for inferring placeholder usernames:

!`gh api user --jq .login`

Authenticated GitHub name, for the LICENSE copyright holder:

!`gh api user --jq .name`

Current year, for the LICENSE copyright:

!`date +%Y`

Run hands-off: apply confidently-inferable replacements without prompting, keep skeleton files, and only stop to ask when a placeholder's intended value is genuinely ambiguous.

1. Read the repo name, directory structure, git remote, and any existing README to learn what the repo is for and which template it came from.
2. Launch Explore agents in parallel to scan for template artifacts. A value is a placeholder if a reader would conclude "this exists only because the template needed something in this slot." Any one of these signals is enough to flag a candidate:
   - Generic or self-naming values: `my-input`, `My Service`, `MY_VAR`, `example`, `foo`
   - Self-referential text: "This is my input, there is no other input like it."
   - Incomplete content: values ending in `...`, sentence fragments, `<...>` slots
   - Conventional stand-in tokens: `UPDATE_ME`, `CHANGEME`, `YOUR_*`, `XXX` (illustrative, not exhaustive)
   - Template instruction comments: "Remove if not using", "Replace with", "Delete this"
   - Template metadata: README titles matching the template repo, "this is a template for X" descriptions, checklists of files to update
   - License attribution: a `LICENSE` copyright holder that is not the authenticated GitHub name above, or a stale year.

   For each candidate, record file path, line number, current value, and which signal flagged it.

3. Apply replacements hands-off.
   - Infer and replace what you can: repo name from the directory, owner or org from the git remote, GitHub username from the login above, and the `LICENSE` copyright from the name and current year above.
   - Remove pure template-marketing files and instruction comments: README "this is a template for X" metadata, checklists of files to update, and "Replace with" / "Delete this" comments.
   - Stop to ask only when a placeholder's intended value is genuinely unknowable.
4. Keep skeleton files. A `.gitkeep`, an empty placeholder directory, or a skeleton `action.yml` or `main.tf` exists for the user to fill in during implementation, not as template noise. Set obvious placeholder `name`, `title`, and `description` fields to sensible values derived from the repo, but preserve the skeleton's structure (its example inputs, outputs, and steps).
5. Write a fresh README describing the actual project, using the repo name, directory structure, and file contents. Preserve auto-generated markers like `<!-- BEGIN_TF_DOCS -->` and `<!-- END_TF_DOCS -->`. Report what you wrote; the user can refine it.
6. Run linters. Prefer `make lint` if a `Makefile` exists. Otherwise by project type:
   - Terraform: `terraform fmt -check`, `terraform validate`
   - Go: `go vet ./...`
   - Shell: `shellcheck` on `.sh` files

## Rules

- Surrounding context distinguishes a placeholder from a real value. `@craigsloggett` in `CODEOWNERS` is the real owner. `TODO` in a code comment about future work is project notes, not a template artifact.
- Keep skeleton and placeholder files (`.gitkeep`, empty directories, a skeleton `action.yml` or `main.tf`). They hold structure for the user to fill in.
- The `LICENSE` copyright holder is the authenticated GitHub name above (`gh api user --jq .name`) and the year is the current year above. Apply it without asking.
- Apply confidently-inferable replacements without prompting. Ask only when a placeholder's intended value is genuinely ambiguous.
