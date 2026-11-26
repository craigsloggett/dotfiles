#!/bin/sh
#
# scripts/repo-corpus.sh
#
# Print the authenticated user's topic vocabulary and repo descriptions. The
# create-repo and create-repo-from-template skills load it so they can propose
# topics and a description in the style of the existing repos.

set -euf

# die prints its message to stderr and exits non-zero.
die() {
  printf '%s\n' "repo-corpus.sh: $1" >&2
  exit 1
}

command -v gh >/dev/null 2>&1 || die "gh is not installed"
command -v jq >/dev/null 2>&1 || die "jq is not installed"

repos="$(gh repo list --json description,repositoryTopics -L 200)" ||
  die "failed to list repos"

printf '%s\n' 'Topic vocabulary (count, name):'
printf '%s\n' "${repos}" | jq -r '
  [.[].repositoryTopics[]?.name]
  | group_by(.)
  | sort_by(-length)
  | .[]
  | "\(length)\t\(.[0])"
'

printf '\n%s\n' 'Descriptions, tagged with their topics:'
printf '%s\n' "${repos}" | jq -r '
  .[]
  | select(.description != null and .description != "")
  | "[\([.repositoryTopics[]?.name] | join(","))] \(.description)"
'
