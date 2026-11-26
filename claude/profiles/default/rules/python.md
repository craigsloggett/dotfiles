---
paths:
  - '**/*.py'
  - '**/*.pyi'
  - '**/pyproject.toml'
---

## Design

- Make invalid states unrepresentable. Parse input into trusted types at the
  boundary. Inner code does not revalidate.
- Prefer functions and modules over classes. A class earns its place by holding
  state or satisfying a protocol.
- Prefer fewer, deeper modules. No pass-through layers or speculative
  abstractions.
- Declare a `Protocol` in the module that consumes it, and only when a consumer
  needs one. Return concrete types.
- Standard library first. A new dependency needs a reason.
- Keep import time free of side effects. Module scope holds definitions and
  constants, and the entrypoint runs under `if __name__ == "__main__":`.

## Types

- Don't annotate local variables. The type checker infers them.
- Take `object` for a value of unknown shape and narrow it.
- Model a record as a `@dataclass(frozen=True, slots=True)`. Never pass a bare
  `dict` or `tuple` between functions.
- Model fixed alternatives as an `Enum` or a union of record types, and close
  every `match` over one with `assert_never`.
- Give identifiers and other domain values their own types with `NewType`
  rather than passing bare `str` or `int`.
- When a value has a real format or comes from untrusted input, construct it
  only through a `@classmethod` named `parse`.
- Accept the widest type that works (`Iterable`, `Mapping`, `Sequence`).
- Mark an overriding method with `@override`.
- Give each suppression comment its reason on the same line.

## Readability

- Optimise for local reasoning: a function should make sense without opening
  other files.
- Small functions, early returns, blank lines between logical steps.
- Comments explain why. Don't explain the language or the framework.
- Write a docstring only when the name and signature leave a question open.
- Use a comprehension for one transform or one filter. Use a loop once there is
  a second condition or a side effect.

## Errors

- Raise a specific exception class that subclasses the closest built-in.
- Catch the narrowest exception the handler can act on, and handle each error
  once. Never log and re-raise.
- Return `None` only when absence is an expected answer. Raise on failure.

## Tests

- Test behaviour through the public API with `pytest`, so tests read like a
  spec.
- Use `pytest.mark.parametrize` once three or more cases share a shape. Name
  each case with `pytest.param(..., id=...)` for the behaviour it checks. A case
  that needs its own setup is its own test.
- If a test is hard to write cleanly, fix the design instead of adding
  scaffolding.
- Test only what the type checker and linters can't prove: pure logic (does it
  compute what I intend) and boundaries (does the external system behave as we
  assume). Every test is maintenance cost and must justify itself.

## Projects

- Manage every project with `uv`. Add packages with `uv add` (`--dev` for
  tools). Do not call `pip` or `python -m venv`, and leave `uv.lock` for `uv` to
  write.
- Run everything through the project environment: `uv run pytest`,
  `uv run python`.
- A single-file script declares its dependencies inline (PEP 723) and runs with
  `uv run`.
- Keep tool configuration in `ruff.toml` and `ty.toml` at the project root.

## Scope

- Where the repo's conventions differ from these rules, follow the repo.
- When a change removes the reason a declaration has its shape, change the
  shape in the same step (e.g. a class left with one method, a parameter every
  caller passes the same value for, or a `Protocol` left with one
  implementation), and finish the refactor.
