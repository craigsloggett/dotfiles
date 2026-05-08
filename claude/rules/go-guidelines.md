---
paths:
  - "**/*.go"
  - "**/go.mod"
  - "**/go.sum"
---

# Go Guidelines

## Coding Standards

- Follow [Effective Go](https://go.dev/doc/effective_go) and [Go Code Review Comments](https://github.com/golang/go/wiki/CodeReviewComments).
- Prefer the standard library. Only add dependencies when they provide clear value.
- Write clear, idiomatic Go.

## Module Versioning

- Set the `go` directive in `go.mod` to the lowest Go version that successfully builds the project without known security vulnerabilities.
