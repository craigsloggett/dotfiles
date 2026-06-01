---
paths:
  - '**/rules/**/*.md'
---

## Claude Rule

### Headings

- Use `##` for the document title and `###` for sections; do not use `#` (H1).

### New Files

- A topic earns its own rule file only when it activates on a glob no existing rule file owns. A glob that is a subset of another's is a section of that file, not a new file (yq fires on `**/*.sh`, so it belongs in shell). The pattern need not be a file extension; a distinct path counts (`**/action.yml`, `.github/**`).
- Scaffold a new file as frontmatter plus a Title Case title, nothing else. Sections appear as rules are filed; invent none up front.

### Frontmatter

```yaml
---
paths:
  - '<glob>'
---
```

- Frontmatter is the `paths:` list of activation glob(s) and nothing else.

### Adding Rules

- Capture the user's intent; do not author beyond it. Phrase it as a clean imperative bullet matching the voice and format of sibling bullets, and never add scope, caveats, or constraints they did not ask for.
- Do not duplicate an existing rule or contradict one; if a new rule would, change nothing and surface it.
- Append a rule under the best-fitting existing heading; if none fits, add a new one.
