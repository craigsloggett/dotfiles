---
paths:
  - '**/action.yml'
  - '**/action.yaml'
---

## Shell Logic

- Extract non-trivial shell logic into scripts in the `src/` directory.
- Reference scripts via `${{ github.action_path }}/src/script_name.sh` with `shell: sh`.
- Never inline multi-line shell logic in `action.yml`.

## README

- Document the action's interface with `## Inputs` and `## Outputs` tables as the final two README sections.

The inputs section columns, in order:

| Column        | Contents                                                                                                                                                                                  |
| ------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `Input`       | Input name in backticks (e.g. `` `base-branch` ``).                                                                                                                                       |
| `Required`    | `Yes` or `No`.                                                                                                                                                                            |
| `Default`     | Blank if required; `Empty` for an empty-string default; literal values in backticks (e.g. `` `${{ github.token }}` ``); computed defaults as prose with backticks around code references. |
| `Description` | One sentence, capitalized, ending with a period.                                                                                                                                          |

The outputs section columns, in order:

| Column        | Contents                                                                                                                                                          |
| ------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `Output`      | Output name in backticks.                                                                                                                                         |
| `Description` | One or more sentences, each capitalized and ending with a period. Note any unset condition in a trailing sentence (e.g. `Empty if no pull request was created.`). |

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
