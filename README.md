# SafeServe TUI

SafeServe's Python terminal client. The repository currently contains the
validated domain values and the remaining module skeleton; restaurant
workflows have yet to be implemented.

## Installation

Prerequisites: Git, Python 3.14, and Poetry. From the repository root:

```bash
poetry install
```

Application and development dependencies are defined in `pyproject.toml` and
locked in `poetry.lock`. Tests do not require a running backend.

## Tests

```bash
poetry run pytest
```

The pytest configuration collects tests from `tests/` and measures coverage
for `safeserve_tui`, reporting uncovered lines. The final requirement is
coverage strictly greater than 90%; a percentage reported for empty modules
does not demonstrate project completion.

The first test runs in a separate process and checks that importing modules
does not read input, write to the terminal, or make HTTP requests through
requests. It characterizes the existing module skeleton.

Shared fixtures in `tests/conftest.py`:

- `scripted_input`: supplies answers to `input()` and records calls;
  exhausting the answers fails the test instead of waiting for interactive input.
- `sample_dish`: provides fresh local sample data for each test; it does not
  represent a JSON payload or an agreed API contract.
- Use pytest's built-in `capsys` fixture to check output.

Develop new behavior using Red → Green → Refactor, checking observable results
and error cases. Replace HTTP calls in application tests with fakes or mocks.

## Continuous integration

GitHub Actions runs `.github/workflows/ci.yml` when a pull request is opened
or updated, on pushes to `main`, and on manual dispatch. The job sets up
Python 3.14 and Poetry 2.5.2, validates the lockfile, installs the locked
application and development dependencies, and runs `poetry run pytest`.
Dependency installation or test failures fail the job. No backend is required.

Coverage is reported using the pytest configuration above. A minimum coverage
threshold is not enforced yet during initial development.

## Domain values

`domain.py` validates values when they are constructed:

| Type | Stored value | Accepted values |
| --- | --- | --- |
| `Price` | `cents` | Integer cents from 1 to 99,999 |
| `Quantity` | `value` | Integer from 1 to 50 |
| `TableNumber` | `value` | Integer from 1 to 99 |
| `SeatCount` | `value` | Integer from 1 to 20 |
| `Category` | `value` | One of the six fixed category strings |

Numeric values are frozen dataclasses. They use explicit `typeguard` checks
and `valid8` range validation in `__post_init__`; validation does not depend
on import hooks or assertions. Boolean values are explicitly rejected.
Wrong numeric types raise `TypeError`, and out-of-range integers raise
`ValueError`. Strings, floats, and decimal values are not converted or rounded.

`Category` is an enum with English member names and the documented values
`ANTIPASTO`, `PRIMO`, `SECONDO`, `CONTORNO`, `DOLCE`, and `BIBITA`.
Unknown values raise `ValueError`; case and whitespace are not normalized.

```python
from safeserve_tui.domain import Category, Price, Quantity, SeatCount, TableNumber

price = Price(850)
quantity = Quantity(2)
table = TableNumber(3)
seats = SeatCount(4)
category = Category("PRIMO")

assert price.cents == 850
assert category is Category.FIRST_COURSE
```

The price limit applies to a dish's unit price, not to an order total. Totals
and rules involving current availability or existing orders belong to the
backend. These values perform no HTTP calls and maintain no simulated data.
Dish-name validation is deferred until the allowed characters are specified.

## Structure

```text
safeserve_tui/
  __main__.py  # future application entry point
  app.py       # application flows
  api.py       # future backend client
  domain.py    # domain values and constraints
  menu.py      # reusable menus
tests/
  conftest.py  # shared fixtures
  test_bootstrap.py
```

An interactive application is not available yet. Tests at this stage require
no server, database, credentials, or changes to the other repositories.
