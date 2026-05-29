---
name: clean-scaffold
description: Use when the user asks to clean up a repo cloned from a template, replace placeholder values, or write a fresh README for a newly scaffolded project.
---

## Workflow

Authenticated GitHub user, for comparison against placeholder usernames:

!`gh api user --jq .login`

1. Read the repo name, directory structure, git remote, and any existing README to learn what the repo is for and which template it came from.

2. Launch Explore agents in parallel to scan for template artifacts. A value is a placeholder if a reader would conclude "this exists only because the template needed something in this slot." Any one of these signals is enough to flag a candidate:
   - Generic or self-naming values: `my-input`, `My Service`, `MY_VAR`, `example`, `foo`
   - Self-referential text: "This is my input, there is no other input like it."
   - Incomplete content: values ending in `...`, sentence fragments, `<...>` slots
   - Conventional stand-in tokens: `UPDATE_ME`, `CHANGEME`, `YOUR_*`, `XXX` (illustrative, not exhaustive)
   - Template instruction comments: "Remove if not using", "Replace with", "Delete this"
   - Template metadata: README titles matching the template repo, "this is a template for X" descriptions, checklists of files to update
   - Scaffolding-only files: empty files, `.gitkeep` in directories that have no other content
   - License attribution: compare the `LICENSE` copyright holder to the authenticated user above and to `git config user.name`. Flag if they differ or the year is stale. Commonly missed because it parses as a real value.

   For each candidate, record file path, line number, current value, and which signal flagged it.

3. Present findings grouped by file. If none, report the repo is clean and stop.

4. Gather replacement values. Group related placeholders into a single question with context. For instruction comments, ask whether to remove or keep. Infer where possible (GitHub username from the value above, repo name from the directory, org from the git remote) and let the user override.

5. Apply replacements. Replace placeholder strings, remove confirmed instruction comments, delete pure-template metadata files.

6. Rewrite the README to describe the actual project, using the repo name, directory structure, and file contents. Preserve auto-generated markers like `<!-- BEGIN_TF_DOCS -->` and `<!-- END_TF_DOCS -->`. Confirm the new README with the user before writing.

7. Run linters. Prefer `make lint` if a `Makefile` exists. Otherwise by project type:
   - Terraform: `terraform fmt -check`, `terraform validate`
   - Go: `go vet ./...`
   - Shell: `shellcheck` on `.sh` files

## Rules

- Surrounding context distinguishes a placeholder from a real value. `@craigsloggett` in `CODEOWNERS` is the real owner. `TODO` in a code comment about future work is project notes, not a template artifact.
- Never apply replacements without user confirmation.
