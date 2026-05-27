---
paths:
  - "**/*.sh"
  - "install"
  - "**/*.yml"
  - "**/*.yaml"
---

# yq Guidelines

## Select Queries

- In a `select()` query like `select(.uses | test("..."))`, the `// ""` is redundant. `yq` silently returns false when `test()` gets `null`. Prefer to write `select()` queries with a `test()` like this: `select(.uses | test("..."))`.
