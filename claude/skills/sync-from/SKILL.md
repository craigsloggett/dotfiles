---
name: Sync From
description: Compare the current project against a source directory and propose changes to align conventions, patterns, and configuration.
arguments:
  - name: source
    description: Path to the source directory to sync from.
    required: true
---

## Workflow

1. **Identify the source and target.** The source is the directory passed as an argument. The target is the current working directory.

2. **Explore both directories.** Launch Explore agents in parallel to understand:
   - **Source:** Read the directory structure, key configuration files, and recent git history (`git -C <source> log --oneline -20`) to understand what has changed recently.
   - **Target:** Read the directory structure and the same categories of files to understand the current state.

3. **Compare across categories.** For each category present in both projects, diff the approach:
   - **Infrastructure code** — Resource patterns, naming, variable structure, provider versions, module usage.
   - **CI/CD** — Workflow definitions, pipeline stages, job configuration.
   - **Linting and formatting** — Config files (`.yamllint`, `.tflint.hcl`, `.golangci.yml`, etc.) and their rule sets.
   - **Documentation** — README structure, inline comments style, terraform-docs configuration.
   - **Project configuration** — Makefiles, `.editorconfig`, `.gitignore`, pre-commit hooks.

4. **Filter to meaningful differences.** Ignore differences that are intentional per-project customization (e.g., different resource names, different variable values). Focus on:
   - Conventions the source follows that the target does not.
   - Configuration the source has updated that the target still has an older version of.
   - Patterns the source uses that would improve the target.

5. **Present findings.** Group proposed changes by category. For each change:
   - State what differs and why the source's approach is preferable.
   - Show the specific files and lines to change in the target.
   - If a difference might be intentional, flag it as a question rather than a recommendation.

6. **Apply changes** only after the user confirms. Do not batch unrelated changes into a single commit.

## Rules

- Read both directories thoroughly before proposing anything. Never assume what a file contains.
- Respect CLAUDE.md and project-level conventions. The source informs what to change, not how to write code.
- Do not copy files wholesale. Adapt patterns to fit the target project's structure.
- If the source and target are different project types (e.g., module vs root module), account for the structural differences. Not everything in the source will apply.
- Keep proposals minimal. Only suggest changes where the source is clearly ahead of the target.
