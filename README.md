# SafeServe TUI

SafeServe's Python terminal client. The repository currently contains the
module skeleton; application features have yet to be implemented.

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
threshold is not enforced yet while the application modules are empty.

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
Development instructions are in `../AGENTS.md`, in the shared parent directory
of the three repositories.
