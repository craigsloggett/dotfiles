#!/bin/sh
#
# scripts/configure-repo.sh
#
# Apply the standard settings, topics, and default branch ruleset to a newly
# created GitHub repo. The create-repo and create-repo-from-template skills run
# it right after creating the repo, so every repo starts with the same setup.
#
# Usage: configure-repo.sh <owner>/<name> [<topic>,<topic>,...]

set -euf

repo="${1:?usage: configure-repo.sh <owner>/<name> [topics]}"
topics="${2:-}"

# die prints its message to stderr and exits non-zero.
die() {
  printf '%s\n' "configure-repo.sh: $1" >&2
  exit 1
}

command -v gh >/dev/null 2>&1 || die "gh is not installed"

# Squash is the only merge style. The squash commit takes the PR title and
# body, so branch commit bodies never reach the default branch.
gh api -X PATCH "repos/${repo}" \
  -F has_wiki=false \
  -F has_projects=false \
  -F allow_merge_commit=false \
  -F allow_rebase_merge=false \
  -F allow_squash_merge=true \
  -F allow_update_branch=true \
  -F delete_branch_on_merge=true \
  -f squash_merge_commit_title=PR_TITLE \
  -f squash_merge_commit_message=PR_BODY \
  >/dev/null || die "failed to apply settings to ${repo}"

if [ -n "${topics}" ]; then
  gh repo edit "${repo}" --add-topic "${topics}" ||
    die "failed to add topics to ${repo}"
fi

# Actor 5 is the Repository admin role. GitHub does not document the id.
gh api -X POST "repos/${repo}/rulesets" --input - >/dev/null <<'EOF' ||
{
  "name": "default",
  "target": "branch",
  "enforcement": "active",
  "conditions": {
    "ref_name": { "include": ["~DEFAULT_BRANCH"], "exclude": [] }
  },
  "bypass_actors": [
    { "actor_id": 5, "actor_type": "RepositoryRole", "bypass_mode": "always" }
  ],
  "rules": [
    {
      "type": "pull_request",
      "parameters": {
        "required_approving_review_count": 0,
        "dismiss_stale_reviews_on_push": false,
        "require_code_owner_review": false,
        "require_last_push_approval": false,
        "required_review_thread_resolution": false
      }
    },
    { "type": "required_linear_history" },
    { "type": "required_signatures" },
    { "type": "deletion" },
    { "type": "non_fast_forward" }
  ]
}
EOF
  die "failed to create the default branch ruleset on ${repo}"
