---
paths:
  - '**/*.go'
  - '**/go.mod'
  - '**/go.sum'
---

## Sources

- Follow [Effective Go](https://go.dev/doc/effective_go), [Go Code Review Comments](https://go.dev/wiki/CodeReviewComments), [Go Test Comments](https://go.dev/wiki/TestComments), and the [Google Go Style Guide](https://google.github.io/styleguide/go/). The [Uber Go Style Guide](https://github.com/uber-go/guide/blob/master/style.md) fills the gaps.
- Prefer the standard library. Only add dependencies when they provide clear value.

## Formatting

- A list-shaped statement goes one item per line: a slog call with two or more pairs puts the message and then each `"key", value` pair on its own line; an `append` statement puts each argument on its own line; a returned slice literal with two or more elements puts each element on its own line. A struct literal that is an item in such a list has one field per line.
- Positional arguments, format arguments, a struct literal assigned on its own, and values inside a composite literal stay on one line. Line length never decides.
- `gofumpt` is the formatter, run through `golangci-lint fmt`. It is a superset of `gofmt`.
- No line length limit, no function length limit, and no magic-number rule. Refactor by meaning, not by count.
- Keep `if`, `for`, `switch`, and function signatures on one line; extract a local instead of wrapping.
- `if err := f(); err != nil` is the preferred shape when the result is not needed afterwards.

## Blank Lines

The house grammar for blank lines inside a function is wsl_v5's default grammar. It is applied by hand, not linted.

- A blank line follows every block (`if`, `for`, `switch`, `select`, `go func`) before the next statement.
- A statement may sit directly above a block only when it is a single assignment whose variable the block's condition or first statement uses. Two assignments above a block get a blank line between them.
- An error check sits directly under the assignment that produced the error.
- `defer` sits directly under the statement that acquired what it releases, or under that statement's error check.
- An assignment cuddles only with another assignment; a call cuddles only with an assignment it uses or another call.
- `x = append(x, y)` cuddles only with another append or with a line that assigns something the append uses.
- A blank line precedes `return`, `break`, and `continue` unless the enclosing block is two lines or fewer.
- `var` and `const` get a blank line above; consecutive declarations become one `var (...)` group. A `var x T` may sit directly above an `if` that uses `x`.
- No blank line at the start or end of a block, and none before a simple `if err != nil`.

## Naming

- MixedCaps only. Initialisms keep one case: `ID`, `URL`, `HTTP`, `appID`, never `Id` or `Url`.
- Name length grows with scope. `i`, `r`, `w`, `ctx`, `t` are fine where the guides bless them; anything read more than a few lines from its declaration gets a word. In table tests the row variable is `test`.
- Receivers are one or two letters from the type name, the same in every method, never `this` or `self`.
- Getters have no `Get` prefix. Printf-style functions end in `f`.
- Sentinel errors are `errFoo` (or `ErrFoo` when exported); error types end in `Error`. No unit suffix on a `time.Duration`.
- Package names are lowercase single words, never `util`, `common`, or `helpers`.
- Never reuse a predeclared identifier or an imported package name as a local.

## Comments

- Go code carries no comments: no package comment, no doc comments, no explanations. Names, types, and structure carry the meaning.
- The only exceptions are directives such as `//go:embed` and the reason that follows a `//nolint`.

## Errors

- Error strings are lowercase with no trailing punctuation; `error` is the last result.
- Errors a caller may match are package-level sentinels wrapped with `%w`; put the sentinel first when it names the category: `fmt.Errorf("%w: got %d", errConfig, n)`. Match with `errors.Is`, never on the string.
- Every error that crosses a package boundary is wrapped with the operation that failed, and nothing else: `fmt.Errorf("query verdicts: %w", err)`. No `failed to`, no repeating what the inner error says.
- Handle an error once: wrap and return, or log and degrade, never both.
- Type assertions use the comma-ok form. `os.Exit` and `log.Fatal` are called only from `main`.

## Declarations and Control Flow

- Handle the error first and return early; no `else` after a branch that returns or continues.
- Empty slices are `var x []T`, except where JSON must encode `[]` rather than `null`; empty maps use `make`.
- `context.Context` is the first parameter and never a struct field. Use `any`, not `interface{}`.
- Prefer a distinct type with constants over a `string` or `bool` that steers control flow; a lookup table becomes a method with a `switch` on that type rather than a package-level map.
- No mutable package-level state and no `init()`.
- Named results only where they aid the doc or a deferred update; naked returns only in very short functions.

## Tests

- Standard library only, no assertion libraries. Use `t.Context()`, not `context.Background()`.
- Failure messages name the function and show got before want: `parseReply(%q) = %v, want %v`.
- A helper that takes `*testing.T` calls `t.Helper()` first. Prefer table-row check functions that return an `error` for the test body to report, so they take no `*testing.T`.
- Match expected errors with `errors.Is` against a sentinel, not a substring.

## Imports

- Two groups: standard library, then everything else. No dot imports; blank imports only in `main` or tests.
- Alias an import only on collision or when its name does not match the path.

## Linting

- Every Go repo carries a `.golangci.yml` in the v2 format enabling `gofumpt` as the formatter and, beyond the standard set: `containedctx`, `embeddedstructfieldcheck`, `err113`, `errname`, `errorlint`, `forcetypeassert`, `gochecknoglobals`, `gochecknoinits`, `godot`, `goprintffuncname`, `nakedret`, `nonamedreturns`, `predeclared`, `revive` (default rules minus `package-comments`, plus `early-return`, `enforce-map-style`, `enforce-slice-style`, `flag-parameter`, `import-shadowing`, `package-naming`, `use-any`), `thelper`, `varnamelen`, `wrapcheck`, staticcheck with `checks: [all]`, and govet `shadow`.
- Fix a finding through the type system first; a `//nolint` needs a trailing comment giving the reason.
- Do not enable `wsl_v5`, `nlreturn`, `lll`, `golines`, `funlen`, `gocognit`, `cyclop`, `mnd`, `goconst`, `noinlineerr`, `tagliatelle`, or `paralleltest`. They enforce rules the canonical guides reject or stay silent on.

## Module Versioning

- Set the `go` directive in `go.mod` to the lowest Go version that successfully builds the project without known security vulnerabilities.
