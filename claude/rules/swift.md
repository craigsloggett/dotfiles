---
paths:
  - '**/*.swift'
---

## Naming

- Follow the [Swift API Design Guidelines](https://www.swift.org/documentation/api-design-guidelines/).
- `UpperCamelCase` for types and protocols; `lowerCamelCase` for everything else (functions, methods, properties, enum cases, parameters).
- Name methods and functions as phrases that read at the call site; omit needless words and don't repeat type information a parameter already conveys.
- Name booleans as assertions: `isEmpty`, `hasSuffix`, not `empty` or `suffix`.
- Suffix a capability protocol `-able`/`-ible` (`Equatable`); name a noun protocol for what it is (`Collection`).
- Case acronyms uniformly: `urlString`, `parseHTML`, never `uRLString`.

## Optionals and Safety

- Never force-unwrap (`!`), force-try (`try!`), or force-cast (`as!`); each crashes on bad input. The sole exception is a value a local precondition guarantees, with a comment saying why.
- Use `guard let value else { ... }` for early exit and `if let value` for the narrow branch; both take the shorthand that omits `= value`.
- Coalesce with `??` and chain with `?.` instead of unwrapping then branching.
- Avoid implicitly unwrapped optionals (`String!`) outside Interface Builder outlets.

## Error Handling

- Throw a specific `Error`-conforming type (usually an `enum` of cases), never a string or an ad-hoc generic error.
- Use typed throws (`throws(SomeError)`) when the failure set is closed and known; leave throws untyped when callers genuinely cannot enumerate the failures.
- Reserve `Result` for stored or deferred outcomes; prefer `throws` for synchronous call-and-return.
- Use `try?` only when nil is a meaningful result, not to silence an error you should handle.

## Types and Immutability

- Reach for `struct` and `enum` first; choose `class` only when you need reference identity, inheritance, or shared mutable state.
- Declare `let` by default; promote to `var` only where mutation is required.
- Mark every non-subclassed `class` `final`.
- Model mutually exclusive states as an `enum` with associated values, not parallel optionals or boolean flags.
- Prefer protocols and generics over class inheritance for polymorphism.

## Expressions

- Split a dense expression by naming intermediate subexpressions with `let`, not by wrapping the single expression across lines; the name documents intent where a line break does not.

## Concurrency

- Target the Swift 6 language mode with strict concurrency checking on; resolve data-race warnings rather than suppressing them.
- Use `async`/`await`; do not add completion-handler APIs or bridge async to sync with `DispatchSemaphore`.
- Protect shared mutable state with an `actor`; mark types that cross concurrency domains `Sendable`.
- Isolate UI-facing state to `@MainActor`.
- Prefer structured concurrency (`async let`, `TaskGroup`) over a detached `Task` unless the work must outlive its scope.

## Access Control

- Default to the most restrictive access level that compiles; widen only when a caller needs it.
- Make stored properties `private`, or `private(set)` when read-only from outside, unless they are part of the type's contract.
- Mark a library's intended API surface `public` or `package`; leave everything else `internal`.

## Structure

- One primary type per file, named after that type (`UserSession.swift`).
- Split protocol conformances into dedicated `extension`s, one per protocol.
- Lay out a SwiftPM package as `Sources/<Target>/` and `Tests/<Target>Tests/`; pin `swift-tools-version` in `Package.swift`.
- Document symbols with `///` comments using the standard `- Parameter`, `- Returns`, and `- Throws` fields.

## Dependencies

- Reference a dependency's public constants directly instead of mirroring them in local literals, and pin each value you rely on with a test so an upstream change on a version bump fails CI instead of drifting silently.

## Formatting and Linting

- SwiftFormat owns formatting: run `swiftformat .` to format, `swiftformat --lint .` in CI; keep settings in `.swiftformat` and pin `--swift-version`.
- SwiftLint owns semantic lint: run `swiftlint` locally, `swiftlint lint --strict` in CI (warnings become errors), and `swiftlint --fix` to autocorrect; keep rules in `.swiftlint.yml`.
- Use `swiftlint analyze` for the compiler-backed rules that need a build log.
- Disable any SwiftLint rule that overlaps SwiftFormat's formatting so the two never fight; let SwiftFormat be the single source of formatting truth.
- Indent with 4 spaces.
