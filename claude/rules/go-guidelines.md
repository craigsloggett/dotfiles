---
paths:
  - "**/*.go"
  - "**/go.mod"
  - "**/go.sum"
---

# Go Guidelines

## Coding Standards

- Follow [Effective Go](https://go.dev/doc/effective_go) and [Go Code Review Comments](https://github.com/golang/go/wiki/CodeReviewComments).
- Use `gofmt` for formatting. No exceptions.
- Prefer the standard library. Only add dependencies when they provide clear value.
- Write clear, idiomatic Go. Avoid clever tricks.

## Naming

- Exported: `PascalCase`. Unexported: `camelCase`. Never `snake_case` or `SCREAMING_SNAKE_CASE`.
- Acronyms use consistent case: `userID` not `userId`, `APIKey` not `ApiKey`, `URL` not `Url`.
- Don't include the type in the name: `fullName` not `fullNameString`, `score` not `scoreInt`.
- Don't shadow Go builtins (`len`, `cap`, `min`, `max`, `new`, `make`, `error`, etc.).
- Avoid clashing with standard library package names you are importing.
- Stick to ASCII letters in identifiers.
- Shorter names are preferred when the meaning is clear from context. Read the standard library for precedent.

### Variable Name Length

- Short names for narrow scope: `i`, `n`, `r`, `w`, `ctx`, `err`, `buf`.
- Longer, descriptive names as scope widens: `customerCount` not `c` at package scope.
- Common short names: `i`, `j`, `k` (indices), `n` (counts), `v` (values), `k` (keys), `s` (strings), `b` (byte slices), `r` (readers), `w` (writers), `ctx` (context), `err` (errors), `mu` (mutexes), `wg` (wait groups), `ok` (boolean checks).

### Receivers

- One or two letter names derived from the type: `(s *Server)`, `(c *Client)`.
- Never use `self` or `this`.
- Keep receiver names consistent across all methods of a type.

### Functions and Methods

- Functions that return something use noun-like names.
- Methods should not repeat the receiver type name: `(*Config).WriteTo` not `(*Config).WriteConfigTo`.
- Don't repeat parameter names or types in the function name.
- Honor canonical method signatures: `Read`, `Write`, `Close`, `Flush`, `String`, `Error`, `Len`, `Less`, `Swap`.

### Getters and Setters

- Getters omit the `Get` prefix: `(*Customer).Address()` not `(*Customer).GetAddress()`.
- Setters use the `Set` prefix: `(*Customer).SetAddress(addr string)`.
- Prefer direct field access when no additional logic is needed.

### Packages

- Lowercase ASCII, no underscores or camelCase. Short, ideally single-word nouns.
- Multi-word names are concatenated lowercase: `ordermanager` not `order_manager`.
- Don't use generic utility names: avoid `util`, `common`, `helpers`, `misc`, `shared`, `base`, `lib`.
- Avoid stuttering: `user.Admin` not `user.UserAdmin`.

### Constants

- Follow the same `camelCase`/`PascalCase` rules as other identifiers. No `SCREAMING_SNAKE_CASE`.
- Group related constants in a `const` block.

### Test Names

- Test functions: `TestFunctionName`, `TestType_Method`.
- Benchmarks: `BenchmarkFunctionName`.
- Examples: `ExampleFunctionName`, `ExampleType_Method`.

## Error Handling

- Always handle errors. Never use `_` to discard them without justification.
- Wrap errors with context: `fmt.Errorf("reading config: %w", err)`.
- Use sentinel errors for expected conditions: `var ErrNotFound = errors.New("not found")`.
- Sentinel error variables use `Err` prefix (exported) or `err` prefix (unexported).
- Error type names use `Error` suffix: `PathError`, `LinkError`.
- Error strings are lowercase and do not end with punctuation.
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

- Define interfaces where they are used, not where they are implemented. Don't create them preemptively.
- Keep interfaces small. One or two methods is ideal.
- Accept interfaces, return concrete types.

## Tooling

- `gofmt` / `goimports` — Formatting.
- `go vet` — Static analysis (always run).
- `staticcheck` — Extended static analysis.
- `golangci-lint` — Aggregated linter runner.
- `go test -race` — Race condition detection. Run in CI.

## Module Versioning

- Set the `go` directive in `go.mod` to the lowest Go version that successfully builds the project without known security vulnerabilities — not necessarily the latest release.
- Run `go mod tidy` after any version change to reconcile `go.sum`.
