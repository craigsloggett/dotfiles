---
paths:
  - '**/*.go'
  - '**/go.mod'
  - '**/go.sum'
---

Write code a reviewer can understand one piece at a time.

## Sources

- Follow [Google Go Style Guide](https://google.github.io/styleguide/go/).

## Design

- Make invalid states unrepresentable. Parse input into trusted types at the
  boundary; inner code does not revalidate.
- Prefer fewer, deeper modules. No pass-through layers or
  speculative abstractions.
- Interfaces belong to the consumer and appear only when a consumer needs one.
  Return concrete types.
- Standard library first. A new dependency needs a reason.
- Each package does one job and has a short, specific name.
- A method that does not use its receiver does not belong on the type: make it
  a function or a constant. Leave the receiver unnamed only when the method
  exists to satisfy an interface. Never silence the linter by dropping the name.

## Readability

- Optimise for local reasoning: a function should make sense without opening
  other files.
- Small functions, early returns, blank lines between logical steps.
- Comments explain why. Don't explain the language or the framework.

## Errors

- Return errors as values. Add context when wrapping, and handle each error
  once.

## Domain Types

- Give identifiers and other domain values their own types rather than
  passing bare `string` or `int`.
- Any signature that takes more than one kind of ID must use distinct types.
- When a value has a real format or comes from untrusted input, make the
  type opaque with a constructor.
- Implement `UnmarshalText` by calling the parser so decoding can't skip
  validation.
- Convert raw strings to domain types once, at the boundary (handlers,
  decoders, config loading).
- Provide `IsZero()` on opaque types and reject zero values at boundaries.
- Don't write tests for what these types already guarantee.

## Tests

- Test behaviour through the exported API, so tests read like a spec.
- Use a table with named subtests once three or more cases share a shape. Name
  each case for the behaviour it checks; a case that needs its own setup is its
  own test.
- If a test is hard to write cleanly, fix the design instead of adding
  scaffolding.
- Test only what the type system and linters can’t prove. That means pure logic
  (does it compute what I intend) and boundaries (does the external system
  behave as we assume).
- Prefer encoding invariants in types over testing for
  them. Every test is maintenance cost and must justify itself.

## Scope

- Where the repo's conventions differ from these rules, follow the repo.
- Leave formatting and mechanical style to the formatter and linters.
- When a change removes the reason a declaration has its shape, change the
  shape in the same step (e.g. a method that no longer uses its receiver, a
  function that now returns a constant, a parameter every caller passes the
  same value for, or an interface left with one implementation).
- Finishing a refactor is part of the task.
