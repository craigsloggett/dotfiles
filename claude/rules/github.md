---
paths:
  - .github/**
---

# GitHub

## Pull Requests

- PR descriptions should be concise bullet points. No markdown headings (`##`), no test plan sections.
- Keep the PR title under 70 characters. Use the description for details.

## Gotchas

- In mikefarah yq (v4), `select(.uses | test(...))` needs no `// ""` guard, since `test()` on null returns false.
