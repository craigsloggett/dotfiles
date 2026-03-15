#!/bin/sh
#
# go-fix.sh - run Go analysis and auto-fix tools at session end
#
# Called as a Stop hook. Only runs in Go projects
# (repos with a go.mod file).

set -u

# Only run in Go projects.
if [ ! -f "go.mod" ]; then
  exit 0
fi

if ! command -v go >/dev/null 2>&1; then
  exit 0
fi

go vet ./... && go fix ./...

if command -v golangci-lint >/dev/null 2>&1; then
  golangci-lint run --fix ./...
fi

exit 0
