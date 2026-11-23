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

Run hands-off. Apply confidently-inferable replacements without prompting, keep
skeleton files, and stop to ask only when a placeholder's value is ambiguous.

1. Read the repo name, directory structure, Git remote, and any existing README
   to learn what the repo is for and which template it came from.
2. Launch Explore agents in parallel to scan for template artifacts. A value is
   a placeholder if a reader would conclude "this exists only because the
   template needed something in this slot." Any one signal is enough:
   - Generic or self-naming values such as `my-input`, `My Service`, `MY_VAR`,
     `example`, or `foo`
   - Self-referential text such as
     `This is my input, there is no other input like it.`
   - Incomplete content such as values ending in `...`, sentence fragments, or
     `<...>` slots
   - Conventional stand-in tokens such as `UPDATE_ME`, `CHANGEME`, `YOUR_*`, or
     `XXX`
   - Template instruction comments such as "Remove if not using", "Replace
     with", or "Delete this"
   - Template metadata such as README titles matching the template repo, "this
     is a template for X" descriptions, or checklists of files to update
   - License attribution where the `LICENSE` copyright holder is not the
     authenticated GitHub name above, or the year is stale

   Record file path, line, current value, and the signal for each candidate.
3. Apply replacements.
   - Infer and replace what you can. Take the repo name from the directory, the
     owner from the Git remote, the GitHub username from the login above, and
     the `LICENSE` copyright from the name and current year above.
   - Remove pure template-marketing files and instruction comments ("this is a
     template for X" metadata, file checklists, "Replace with" / "Delete this").
   - Ask only when a placeholder's value is unknowable.
4. Keep skeleton files. A `.gitkeep`, an empty placeholder directory, or a
   skeleton `action.yml`/`main.tf` is for the user to fill in, so it does not
   count as a template artifact. Set obvious placeholder
   `name`/`title`/`description` fields to sensible values, but preserve the
   skeleton's structure.
5. Write a fresh README for the actual project using the repo name, structure,
   and file contents. Preserve auto-generated markers (e.g.
   `<!-- BEGIN_TF_DOCS -->` / `<!-- END_TF_DOCS -->`). Report what you wrote so
   the user can refine it.
6. Run linters: `make lint` if a `Makefile` exists, else by type:
   - Terraform: `terraform fmt -check`, `terraform validate`
   - Go: `go vet ./...`
   - Shell: `shellcheck` on `.sh` files

## Rules

- Surrounding context distinguishes a placeholder from a real value.
  `@craigsloggett` in `CODEOWNERS` is the real owner, and `TODO` about future
  work is project notes.
