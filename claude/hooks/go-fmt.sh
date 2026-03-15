#!/bin/sh
#
# go-fmt.sh - format all Go files after Claude edits
#
# Called as a PostToolUse hook. Only runs in Go projects
# (repos with a go.mod file).

set -u

# Only run in Go projects.
if [ ! -f "go.mod" ]; then
  exit 0
fi

if ! command -v gofmt >/dev/null 2>&1; then
  exit 0
fi

gofmt -w .

exit 0
