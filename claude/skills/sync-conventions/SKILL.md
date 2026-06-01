---
name: sync-conventions
description: Use when the user asks to compare the current project against a source directory and align conventions, patterns, or configuration.
arguments:
  - name: source
    description: Path to the source directory to sync from.
    required: true
---

## Workflow

1. Identify the source and target. The source is the directory passed as an argument. The target is the current working directory.
2. Explore both directories. Launch Explore agents in parallel:
   - Source: read the directory structure, key configuration files, and recent git history (`git -C $source log --oneline -20`) to understand what has changed recently.
   - Target: read the directory structure and the same categories of files to understand the current state.

3. Compare across categories. For each category present in both projects, diff the approach:
   - Shell scripts: shebang and dialect (POSIX `sh` vs bash), strict-mode flags (`set -ef`), `main()` entrypoint pattern, function style (subshell `()` for resource-owning scopes with their own `trap EXIT INT TERM HUP`, brace `{}` for plain helpers that never set EXIT traps), session-scoped `TMPDIR_SESSION` handling, reconciler/idempotency patterns, atomic-rename-from-staging for file writes, and `shellcheck -s sh` directives.
   - Infrastructure code: resource patterns, naming, variable structure, provider versions, module usage.
   - CI/CD: workflow definitions, pipeline stages, job configuration.
   - Linting and formatting: config files (`.yamllint`, `.tflint.hcl`, `.golangci.yml`, etc.) and their rule sets.
   - Documentation: README structure, inline comments style, terraform-docs configuration.
   - Project configuration: Makefiles, `.editorconfig`, `.gitignore`, pre-commit hooks.

4. Filter to meaningful differences. Ignore differences that are intentional per-project customization (different resource names, different variable values). Focus on:
   - Conventions the source follows that the target does not.
   - Configuration the source has updated that the target still has an older version of.
   - Patterns the source uses that would improve the target.

5. Present findings. Group proposed changes by category. For each change:
   - State what differs and why the source's approach is preferable.
   - Show the specific files and lines to change in the target.
   - If a difference might be intentional, flag it as a question rather than a recommendation.

6. Apply changes only after the user confirms. Do not batch unrelated changes into a single commit.
7. Run the Consistency Reviewer subagent on the pending diff. It will interrogate the result for patterns applied to one case but missed on a sibling case (a file renamed in one place but not in another). Address any findings before considering the sync complete.

## Rules

- Respect CLAUDE.md and project-level conventions. The source informs what to change, not how to write code.
- Do not copy files wholesale. Adapt patterns to fit the target project's structure.
- If the source and target are different project types, account for the structural differences. Not everything in the source will apply.
