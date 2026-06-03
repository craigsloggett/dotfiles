---
paths:
  - .github/**
---

## Dependabot

- Enable the `github-actions` ecosystem with `directory: /` and `schedule.interval: weekly`.
- Set `commit-message.prefix: chore(ci)` in repos with a release pipeline (Conventional Commits); omit the prefix otherwise.

## CODEOWNERS

- Open with the standard comment explaining that listed owners are the default reviewers, then a single `*` catch-all owner.
- The owner must be a valid GitHub user, not a placeholder (e.g. `@MYGITHUBUSERNAME`); a templated repo must have its placeholder replaced before the file is considered done.

## Workflows

- Pin every action to a full commit SHA with a trailing `# vX.Y.Z` comment, never a tag or branch.
- Pin `runs-on` to the specific runner image that `ubuntu-latest` currently resolves to (`ubuntu-24.04` per the `actions/runner-images` README), never `ubuntu-latest` itself; bump it when `latest` moves.
- Declare an explicit least-privilege `permissions:` block at the top of each workflow.
- Give the workflow, every job, and every step a Title Case `name:`; name the checkout step `Checkout`.
- In mikefarah yq (v4), `select(.uses | test(...))` needs no `// ""` guard, since `test()` on null returns false.
