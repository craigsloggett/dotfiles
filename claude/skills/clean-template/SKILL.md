---
name: Clean Template
description: Scan a repo cloned from a template, identify placeholder artifacts, interactively replace them, and rewrite the README.
---

## Workflow

1. **Identify the project** by reading the repo name, directory structure, git remote, and any existing README to understand what the repo is for and which template it came from. The authenticated GitHub user, used below to distinguish real owner references from placeholder usernames, is **!`gh api user --jq .login`**.

2. **Scan for template artifacts** by launching Explore agents in parallel. The goal is to identify any value the template author left as a stand-in for the consumer to replace. Use semantic judgment, not a fixed keyword list: a value is a placeholder if a human reading it would conclude "this exists only because the template needs *something* in this slot." Signals that suggest a placeholder, any of which is enough to flag a candidate:

   - **Generic or self-naming values** — `my-input`, `My Service`, `MY_VAR`, `example`, `foo`, or anything else whose name describes its role rather than identifying it.
   - **Self-referential or tautological text** — descriptions that describe the act of describing ("This is my input, there is no other input like it.", "The default description.", "The output this composite action produces.").
   - **Incomplete content** — values ending in `...`, sentence fragments, or `<...>`-style angle-bracket slots.
   - **Conventional placeholder tokens** — anything obviously stand-in, including but not limited to `UPDATE_ME`, `CHANGEME`, `YOUR_*`, `XXX`. Treat the literal token list as illustrative, not exhaustive.
   - **Template instruction comments** — "Remove if not using", "Update this to", "Replace with", "Delete this" in any comment syntax (`#`, `//`, `<!-- -->`).
   - **Template metadata** — README titles matching the template repo's name, checklists of files to update, boilerplate "this is a template for X" descriptions.
   - **Files that exist only as scaffolding** — empty files, example files, `.gitkeep` in a directory that has no other content.
   - **License attribution carried over from the template author** — the `LICENSE` file's copyright holder and year are commonly missed because they look like real values. Compare the copyright holder to the authenticated GitHub user above and to `git config user.name`; if they differ, flag for replacement. Compare the year to the current year and flag if stale.

   For each candidate, record file path, line number, current value, and which signal flagged it. Use surrounding context to rule out legitimate values: `@craigsloggett` in `CODEOWNERS` matches the authenticated user above and is the real owner, not a placeholder.

3. **Present findings** grouped by file. For each artifact, show the file path, line number, current value, and what kind of artifact it is (placeholder, instruction comment, or template metadata). If no artifacts are found, report that the repo appears clean and stop.

4. **Gather replacement values** by asking the user for each distinct placeholder. Group related placeholders together (e.g., all `UPDATE_ME` occurrences in the same file in a single question showing the context for each). For instruction comments, ask whether to remove the comment or keep it. Infer values where possible — GitHub username from `gh api user --jq .login`, repo name from the directory name, organization from the git remote — and let the user confirm or override inferred values.

5. **Apply replacements** based on user responses. Replace placeholder strings with the provided values. Remove instruction comments the user confirmed for deletion. Delete any pure-template metadata files.

6. **Rewrite the README** to describe the actual project. Use the repo name, directory structure, and file contents to generate a project-appropriate README. Preserve auto-generated markers (e.g., `<!-- BEGIN_TF_DOCS -->` / `<!-- END_TF_DOCS -->`). Replace the template title, description, and checklist with real content. Ask the user to confirm the new README before writing it.

7. **Run linters and validators** to verify the changes are clean. Detect the project type and run the appropriate commands:
   - Look for a `Makefile` first. Use `make lint` if available.
   - Terraform: `terraform fmt -check`, `terraform validate`
   - Go: `go vet ./...`
   - Shell: `shellcheck` on any `.sh` files

## Rules

- Always scan the full repo before proposing any changes. Never assume what a file contains.
- Never apply replacements without user confirmation. Present all findings first.
- Infer values where possible (GitHub username, repo name, org from the remote URL) to minimize questions. Show inferred values and let the user override them.
- Preserve file structure and formatting. Only change the artifact text, not surrounding code.
- Keep auto-generated section markers intact (e.g., `<!-- BEGIN_TF_DOCS -->` / `<!-- END_TF_DOCS -->`). Only rewrite content outside auto-generated sections.
- Do not treat legitimate uses of common words as artifacts. A `TODO` in a code comment about future work is not a template artifact. Use surrounding context to distinguish template placeholders from real project notes.
- Respect CLAUDE.md conventions. Match the project's existing style for any generated content.
