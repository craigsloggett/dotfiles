---
paths:
  - '**/.claude/rules/*.md'
  - '**/claude/rules/*.md'
---

## Frontmatter

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

## Headings

- Use `##` for section headings; omit a document title heading. Do not use `#` (H1).

## New Files

- A topic earns its own rule file only when it activates on a glob no existing rule file owns.
- A glob that is a subset of another's is a section of that file, not a new file.

## Adding Rules

- Phrase rules as a clean imperative bullet matching the voice and format of sibling bullets.
- Keep each bullet to a single scannable point (one idea); split a bullet that bundles distinct rules. A rule paired with its rationale or exception is one idea, not two.
- Do not duplicate an existing rule or contradict one; if a new rule would, change nothing and surface it.
- Append a rule under the best-fitting existing heading; if none fits, add a new one.
