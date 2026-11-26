---
name: sync-conventions
description: >-
  Compare the current project against a source directory and align its
  conventions, patterns, and configuration.
when_to_use: >-
  Use when the user asks to sync or align the current project with another
  directory.
arguments:
  - source
---

## Arguments

Positional and optional. Invoke as `/sync-conventions <source>`.

- `source`: path to the source directory to sync from. Blank asks.

## Workflow

1. The source is `$source`, and the target is the current working directory.
2. Explore both directories. Launch Explore agents in parallel:
   - In the source, read the directory structure, key configuration files, and
     recent Git history (`git -C $source log --oneline -20`) to understand what
     has changed recently.
   - In the target, read the directory structure and the same categories of
     files to understand the current state.

3. Compare across categories. For each category present in both projects, diff
   the approach:
   - In shell scripts, compare the shebang and dialect (POSIX `sh` vs Bash),
     strict-mode flags (`set -ef`), `main()` entrypoint pattern, function style
     (subshell `()` for resource-owning scopes with their own
     `trap EXIT INT TERM HUP`, brace `{}` for plain helpers that never set EXIT
     traps), session-scoped `TMPDIR_SESSION` handling, reconciler/idempotency
     patterns, atomic-rename-from-staging for file writes, and
     `shellcheck -s sh` directives.
   - In infrastructure code, compare resource patterns, naming, variable
     structure, provider versions, and module usage.
   - In CI/CD, compare workflow definitions, pipeline stages, and job
     configuration.
   - In linting and formatting, compare config files (`.yamllint`,
     `.tflint.hcl`, `.golangci.yml`, etc.) and their rule sets.
   - In documentation, compare README structure, inline comments style, and
     terraform-docs configuration.
   - In project configuration, compare Makefiles, `.editorconfig`,
     `.gitignore`, and pre-commit hooks.

4. Filter to meaningful differences. Ignore differences that are intentional
   per-project customization (different resource names, different variable
   values). Focus on:
   - Conventions the source follows that the target does not.
   - Configuration the source has updated that the target still has an older
     version of.
   - Patterns the source uses that would improve the target.

5. Present findings. Group proposed changes by category. For each change:
   - State what differs and why the source's approach is preferable.
   - Show the specific files and lines to change in the target.
   - If a difference might be intentional, flag it as a question rather than a
     recommendation.

6. Apply changes only after the user confirms. Do not batch unrelated changes
   into a single commit.
7. Delegate the pending diff to the `conventions:consistency-reviewer` agent.
   It flags patterns applied to one case but missed on a sibling case (a file
   renamed in one place but not in another). Address any findings before
   considering the sync complete.

## Rules

- Respect CLAUDE.md and project-level conventions. The source informs what to
  change, and those conventions decide how to write the code.
- Do not copy files wholesale. Adapt patterns to fit the target project's
  structure.
- If the source and target are different project types, account for the
  structural differences. Not everything in the source will apply.
