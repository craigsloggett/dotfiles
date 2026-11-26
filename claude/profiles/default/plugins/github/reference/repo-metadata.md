## Repo Metadata

The create-repo and create-repo-from-template skills propose a new repo's
topics and description from the corpus that `scripts/repo-corpus.sh` prints.

### Topics

Propose topics from the vocabulary, matching the user's phrasing. Let the user
add, remove, or override them. Accept a topic outside the vocabulary only if
the user types it.

- "composite action" or "GitHub action" becomes `composite-action`.
- "Terraform module/provider" becomes `terraform`.
- A HashiCorp product also gets `hashicorp`.
- "vault plugin" becomes `vault`.
- "shell script" or "POSIX" becomes `shell`.

### Description

Propose one sentence in the style of the descriptions whose topics overlap the
proposed ones, and show the samples you used so the user can check them. Allow
an empty description but discourage it.
