---
paths:
  - ".github/**"
---

# GitHub Guidelines

## Pull Requests

- PR descriptions should be concise bullet points. No markdown headings (`##`), no test plan sections.
- Keep the PR title under 70 characters. Use the description for details.

## Composite Actions

- Extract non-trivial shell logic into scripts in the `src/` directory.
- Reference scripts via `${{ github.action_path }}/src/script_name.sh` with `shell: sh`.
- Never inline multi-line shell logic in `action.yml`.
