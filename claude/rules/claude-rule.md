---
paths:
  - '**/.claude/rules/*.md'
  - '**/claude/rules/*.md'
---

## Claude Rule

### Frontmatter

| Field   | Use                                                            |
| ------- | -------------------------------------------------------------- |
| `paths` | Required. List of activation glob(s) and nothing else.         |

Example:

```yaml
---
paths:
  - '<glob>'
---
```

### Headings

- Use `##` for the document title and `###` for sections; do not use `#` (H1).

### New Files

- A topic earns its own rule file only when it activates on a glob no existing rule file owns.
- A glob that is a subset of another's is a section of that file, not a new file.

### Adding Rules

- Phrase rules as a clean imperative bullet matching the voice and format of sibling bullets.
- Do not duplicate an existing rule or contradict one; if a new rule would, change nothing and surface it.
- Append a rule under the best-fitting existing heading; if none fits, add a new one.
