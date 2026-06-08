---
name: create-from-template
description: Use when the user wants the full flow from a template repo, creating the GitHub repo, cloning it locally, cutting the initial release, settling open PRs, then cleaning up template scaffolding. Orchestrates the step skills.
arguments:
  - template
  - name
  - owner
---

## Arguments

Positional and optional, passed straight to the create step. Invoke as `/create-from-template <template> <name> <owner>`.

- `template`: owner/repo of the template. Blank lists accessible templates and prompts.
- `name`: name for the new repo. Blank asks.
- `owner`: owner for the new repo. Blank defaults to the authenticated user.

## Workflow

Run the step skills in order. Each is invocable on its own; this skill sequences them for the from-template flow.

1. Invoke the `create-repo-from-template` skill with `$template`, `$name`, and `$owner` so it can resolve the template, create the repo, apply settings and topics, and add the default branch ruleset. Note the resulting `<owner>/<name>`.
2. Invoke the `clone-repo-locally` skill with `<owner>/<name>` so it can clone to `~/Developer/GitHub/<owner>/<name>`.
3. Invoke the `create-initial-release` skill with `<owner>/<name>` so it can cut the `v0.0.1` prerelease that marks the pristine template state.
4. Invoke the `settle-open-prs` skill on `~/Developer/GitHub/<owner>/<name>` so it can fix any dependabot PR titles, merge the green ones, and pull the default branch locally.
5. Invoke the `cleanup-template-scaffolding` skill on `~/Developer/GitHub/<owner>/<name>` so it can scan for placeholders, apply replacements, and write a fresh README.

## Rules

- Keep the order create, clone, release, settle PRs, cleanup. The release tags the unmodified template before any cleanup commits, so `v0.0.1` marks the pristine state, and PRs settle before cleanup so it starts from the merged default branch.
