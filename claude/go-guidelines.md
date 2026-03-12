# Go Guidelines

## Coding Standards

- Follow [Effective Go](https://go.dev/doc/effective_go) and [Go Code Review Comments](https://github.com/golang/go/wiki/CodeReviewComments).
- Use `gofmt` for formatting. No exceptions.
- Prefer the standard library. Only add dependencies when they provide clear value.
- Write clear, idiomatic Go. Avoid clever tricks.

## Naming

- Packages: short, lowercase, single-word. No underscores or camelCase.
- Exported: `MixedCaps`. Unexported: `mixedCaps`.
- Interfaces: single-method interfaces use the `-er` suffix (`Reader`, `Writer`).
- Avoid stuttering: `http.Client`, not `http.HTTPClient`.
- Acronyms are all caps: `ID`, `URL`, `HTTP`.

## Error Handling

- Always handle errors. Never use `_` to discard them without justification.
- Wrap errors with context: `fmt.Errorf("reading config: %w", err)`.
- Use sentinel errors for expected conditions: `var ErrNotFound = errors.New("not found")`.
- Use custom error types when callers need to inspect error fields.
- Don't log and return the same error. Do one or the other.

## Project Layout

- `cmd/<name>/main.go` — Entry points. Keep thin: parse flags, wire dependencies, call `run()`.
- `internal/` — Private packages. Use freely to encapsulate implementation details.
- `pkg/` — Only when providing a public library API. Most projects don't need this.
- Test files live alongside the code they test: `foo.go` / `foo_test.go`.

## Testing

- Use table-driven tests with `t.Run` for named subtests.
- Use `t.Helper()` in test helper functions.
- Use `t.Cleanup()` for teardown instead of `defer` when possible.
- Use `testdata/` for golden files and test fixtures.
- Prefer `_test` package suffix for black-box testing of exported APIs.
- Test behavior, not implementation details.

## Concurrency

- Don't start goroutines without a shutdown strategy.
- Use `errgroup.Group` for concurrent operations that can fail.
- Use `context.Context` for cancellation and timeouts. Pass as first parameter.
- Prefer channels for communication, mutexes for state protection.

## Interfaces

- Define interfaces where they are used, not where they are implemented.
- Keep interfaces small. One or two methods is ideal.
- Accept interfaces, return concrete types.

## Tooling

- `gofmt` / `goimports` — Formatting.
- `go vet` — Static analysis (always run).
- `staticcheck` — Extended static analysis.
- `golangci-lint` — Aggregated linter runner.
- `go test -race` — Race condition detection. Run in CI.
