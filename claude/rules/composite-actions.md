---
paths:
  - '**/action.yml'
  - '**/action.yaml'
---

## Composite Actions

### Shell Logic

- Extract non-trivial shell logic into scripts in the `src/` directory.
- Reference scripts via `${{ github.action_path }}/src/script_name.sh` with `shell: sh`.
- Never inline multi-line shell logic in `action.yml`.

### README

- Every composite action README documents its interface with an `## Inputs` and an `## Outputs` table, formatted per the Markdown tables rule in `markdown.md`. Place these as the final two sections of the README.
- For the inputs section columns, in order: `Input`, `Required`, `Default`, `Description`:
    - Input: the input name wrapped in backticks (e.g. `` `base-branch` ``).
    - Required: `Yes` or `No`.
    - Default: leave blank when the input is required; write the literal word `Empty` when the default is an empty string; wrap literal default values in backticks (e.g. `` `${{ github.token }}` ``, `` `github-actions[bot]` ``); for computed or composed defaults, write a prose description with backticks around any code references (e.g. `` `title` and `body` joined by a blank line ``).
    - Description: a single sentence starting with a capital letter and ending with a period.
- For the outputs section columns, in order: `Output`, `Description`:
    - Output: the output name wrapped in backticks.
    - Description: one or more sentences, each starting with a capital letter and ending with a period. When the output can be unset, describe that condition in a trailing sentence (e.g. `Empty if no pull request was created.`).

Example:

```markdown
## Inputs

| Input         | Required | Default                                         | Description                                       |
| ------------- | -------- | ----------------------------------------------- | ------------------------------------------------- |
| `title`       | Yes      |                                                 | The pull request title.                           |
| `body`        | No       | Empty                                           | The pull request body.                            |
| `branch`      | No       | `${{ github.event.repository.default_branch }}` | The base branch to open the pull request against. |
| `base-branch` | No       | `${{ github.event.repository.default_branch }}` | The base branch to open the pull request against. |

## Outputs

| Output | Description                                                                |
| ------ | -------------------------------------------------------------------------- |
| `url`  | The URL of the created pull request. Empty if no pull request was created. |
```
