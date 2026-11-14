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
- Prefer few deep modules over many shallow ones. No pass-through layers or
  speculative abstractions.
- Interfaces belong to the consumer and appear only when a consumer needs one.
  Return concrete types.
- Standard library first. A new dependency needs a reason.
- Each package does one job and has a short, specific name.

## Readability

- Optimise for local reasoning: a function should make sense without opening
  other files.
- Small functions, early returns, blank lines between logical steps.
- Comments explain why. Don't explain the language or the framework.

## Errors

- Return errors as values. Add context when wrapping, and handle each error
  once.

## Tests

- Test behaviour through the exported API, so tests read like a spec.
- Use a table with named subtests once three or more cases share a shape. Name
  each case for the behaviour it checks; a case that needs its own setup is its
  own test.
- If a test is hard to write cleanly, fix the design instead of adding
  scaffolding.

## Scope

- Change only what the task needs. Note other improvements instead of making
  them.
- Where the repo's conventions differ from these rules, follow the repo.
- Leave formatting and mechanical style to the formatter and linters.
