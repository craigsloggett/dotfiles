---
paths:
  - '**/.claude/rules/*.md'
  - '**/claude/profiles/*/rules/*.md'
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

- Use `##` for section headings and omit a document title heading. Do not use
  `#` (H1).

## New Files

- A topic earns its own rule file only when it activates on a glob that no
  existing rule file owns.
- A glob that is a subset of another's is a section of that file.

## Adding Rules

- Phrase rules as a clean imperative bullet matching the voice and format of
  sibling bullets.
- Keep each bullet to a single scannable point (one idea), and split a bullet
  that bundles distinct rules. A rule paired with its rationale or exception
  counts as one idea.
- Do not duplicate an existing rule or contradict one. If a new rule would,
  surface it without changing anything.
- Append a rule under the best-fitting existing heading. If none fits, add a new
  one.
- Always ensure rules are concise and declarative: ask yourself “Would removing
  this cause Claude to make a mistake?”
