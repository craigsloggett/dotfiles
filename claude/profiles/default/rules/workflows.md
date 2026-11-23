---
paths:
  - .github/workflows/**
---

## Workflows

- Pin every action to a full commit SHA with a trailing `# vX.Y.Z` comment.
  Never pin to a tag or branch.
- Pin `runs-on` to the specific runner image that `ubuntu-latest` currently
  resolves to (`ubuntu-24.04` per the `actions/runner-images` README), and bump
  it when `latest` moves. Never use `ubuntu-latest` itself.
- Declare an explicit least-privilege `permissions:` block at the top of each
  workflow.
- Give the workflow, every job, and every step a Title Case `name:`; name the
  checkout step `Checkout`.
- In `mikefarah/yq` (v4), `select(.uses | test(...))` works without a `// ""`
  guard, since `test()` on null returns false.
