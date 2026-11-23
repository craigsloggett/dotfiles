---
paths:
  - '**/*.swift'
---

## Naming

- Follow the
  [Swift API Design Guidelines](https://www.swift.org/documentation/api-design-guidelines/).
- `UpperCamelCase` for types and protocols; `lowerCamelCase` for everything else
  (functions, methods, properties, enum cases, parameters).
- Name methods and functions as phrases that read at the call site; omit
  needless words and don't repeat type information a parameter already conveys.
- Name booleans as assertions such as `isEmpty` and `hasSuffix`. Never `empty`
  or `suffix`.
- Suffix a capability protocol `-able`/`-ible` (`Equatable`); name a noun
  protocol for what it is (`Collection`).
- Case acronyms uniformly, as in `urlString` and `parseHTML`. Never
  `uRLString`.
- Name a function that returns a transformed value with a past participle
  (merged, regrouped, migrated) and one that acts on its receiver with an
  imperative (merge, save, publish).
- Open a parameter list with a preposition that reads at the call site. The
  allowed ones are of, for, in, from, at, and to. Never with, using, or by.
  Drop the label when the method name already names the argument.
- Construct a session with `static func begin(...)` and end it with an explicit
  method its owner calls. Never clean up in `deinit`.
- A namespace is a caseless enum. Never use a struct with no stored properties.

## Comments

- Do not write comments. Names, types, and structure carry the meaning; the
  design conversation and the record carry the why.
- Only a tunable constant or a platform trap the code cannot show earns a
  `///`. For a constant, say what it bounds and what you measured it against.
  Never summarise what the code does.
- Never write a `// MARK:` by hand. The formatter owns them, and they name a
  type. They do not name a visibility.

## Optionals and Safety

- Never force-unwrap (`!`), force-try (`try!`), or force-cast (`as!`); each
  crashes on bad input. The sole exception is a value a local precondition
  guarantees, with a comment saying why.
- Use `guard let value else { ... }` for early exit and `if let value` for the
  narrow branch; both take the shorthand that omits `= value`.
- Chain with `?.` instead of unwrapping then branching. Prefer `if let` with a
  defaulted `var` over `??` embedded mid-expression (`(f(x) ?? 0) + 1`); a bare
  trailing default (`name ?? "Unknown"`) is fine.
- Avoid implicitly unwrapped optionals (`String!`) outside Interface Builder
  outlets.

## Errors

- Throw a specific `Error`-conforming type (usually an `enum` of cases). Never
  throw a string or an ad-hoc generic error.
- Use typed throws (`throws(SomeError)`) for a closed, known failure set; leave
  throws untyped when callers cannot list the failures.
- Reserve `Result` for stored or deferred outcomes; prefer `throws` for
  synchronous call-and-return.
- Use `try?` only when nil is a meaningful result. Never use it to silence an
  error you should handle.
- An error enum declares cases and payloads. Keep copy and `LocalizedError` out
  of it. The copy is a `+Message` extension in the layer that shows it,
  switching exhaustively.
- Handle an error once: the catch that degrades logs it with `error` and turns
  it into state. Never log and rethrow.
- Wrap `do` around the throwing call alone, and catch `is CancellationError`
  ahead of the general catch.

## Types and Immutability

- Reach for `struct` and `enum` first; choose `class` only when you need
  reference identity, inheritance, or shared mutable state.
- Declare `let` by default; promote to `var` only where the value has to
  change.
- Mark every non-subclassed `class` `final`.
- Model mutually exclusive states as an `enum` with associated values. Avoid
  parallel optionals and boolean flags.
- Prefer protocols and generics over class inheritance for polymorphism.

## Expressions

- Split a dense expression by naming intermediate subexpressions with `let`. Do
  not wrap the single expression across lines; the name documents intent where
  a line break does not.
- Write a multi-clause condition with the keyword alone on its line, one clause
  per line, and `{` or `else {` alone on the last.
- Separate a block from the step after it with a blank line; a return directly
  after a plain statement cuddles it.
- Declare an empty collection with its type on the left: `var x: [T] = []`.
  Never write `[T]()`.
- Give an optional accessor over an enum you own an arm for every nil case;
  never use `default` or `guard case`, so a new case stops the compiler at the
  accessor.

## Concurrency

- Target the Swift 6 language mode with strict concurrency checking on; resolve
  data-race warnings rather than suppressing them.
- Use `async`/`await`; do not add completion-handler APIs or bridge async to
  sync with `DispatchSemaphore`.
- Isolate UI-facing state to `@MainActor`.
- Type a callback the engine will call `@escaping @MainActor (X) -> Void` and
  hop back with `Task { @MainActor in }`.
- Capture `[weak self]` only in a closure that outlives the call and `[self]`
  when the task is the object's lifetime. Never capture `unowned`.
- Expose an `@Observable` class's state as `private(set) var`, and mark a
  non-state member (a player, an observer token) `@ObservationIgnored`.

## Access Control

- Default to the most restrictive access level that compiles; widen only when a
  caller needs it.
- Make stored properties `private`, or `private(set)` when read-only from
  outside, unless they are part of the type's contract.
- Mark a library's intended API surface `public` or `package`; leave everything
  else `internal`.

## Structure

- Declare a struct's stored properties in the order the memberwise initializer
  should read at the call site. Put identity first, then defining facts, then
  content, and omittable overlays last. A `var` with a default becomes an
  omittable trailing parameter; a `let` with a default leaves the initializer
  entirely. Use a defaulted `let` to forbid callers from supplying the value.
- Order every parameter list a caller reads, whether a function, an explicit
  initializer, or a struct's stored properties (its memberwise initializer).
  Put data before closures, required before optional within the data, and
  defaulted last. Closures include view-builder slots, so trailing-closure
  syntax survives; a required parameter never follows an optional one.
- When grouping-by-concept fights call-site readability, prefer the call site,
  because every caller sees the initializer's order, only the file sees the
  grouping, and `let`/`var` already mark each line's role.
- Split protocol conformances into dedicated `extension`s, one per protocol.
- Order a view as dependencies (data lets, bindings, closures, object
  environments, key-path environments), `body`, private state, knowledge and
  builders in the order `body` uses them, then actions.
- A modifier lives in `View+<Feature>.swift`, holding the extension View and one
  private ViewModifier struct named without the prefix.
- A tunable number lives on a sheet, a caseless enum of nested areas of typed
  static lets. Never write one inline in the type that reads it.

## SwiftUI

- A view never starts async work: no `.task`, no `Task { }` in a body. It calls
  a synchronous method on an app object. The app object owns the task.
- A pane-level view reads app objects with `@Environment(T.self)`; a view
  stamped per row, and a `Commands` struct, take values and closures as lets.
- A conditional modifier is `@ViewBuilder` over `if let`, returning `self` when
  it doesn't add anything.
- Do not write a `#Preview`.

## Logging

- Each type stores one `private let logger` from the app's one `Logger` factory;
  never construct a logger inline or share a global.
- `error` for a failure handled by degrading, `notice` for a stage milestone,
  `info` for a measurement, `debug` for chatter, `fault` for data the app cannot
  load or save.
- A log message is a capitalised sentence without a period; names and errors
  interpolate with `privacy: .public`; hoist a member read to a local before the
  call.

## Dependencies

- Reference a dependency's public constants directly instead of mirroring them
  in local literals, and pin each value you rely on with a test so an upstream
  change on a version bump fails CI instead of drifting silently.

## Formatting and Linting

- SwiftFormat owns formatting. Run `swiftformat .` to format and
  `swiftformat --lint .` in CI; keep settings in `.swiftformat` and pin
  `--swift-version`.
- SwiftLint owns semantic lint. Run `swiftlint` locally,
  `swiftlint lint --strict` in CI (warnings become errors), and
  `swiftlint --fix` to autocorrect; keep rules in `.swiftlint.yml`.
- Use `swiftlint analyze` for the compiler-backed rules that need a build log.
- Disable any SwiftLint rule that overlaps SwiftFormat's formatting so the two
  never fight; let SwiftFormat be the single source of formatting truth.
- Indent with 4 spaces.
