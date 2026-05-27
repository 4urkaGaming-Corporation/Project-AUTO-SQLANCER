# Project AUTO-SQLANCER – Contribution Report

**Project Title:** Support Automated Testing of Scripts via GitHub Actions  
**Organization:** [sqlancer/auto-sqlancer](https://github.com/sqlancer/auto-sqlancer)  
**Issue:** [#23 – Support Automated Testing of Scripts via GitHub Actions](https://github.com/sqlancer/auto-sqlancer/issues/23)  
**Contributors:** Maxim Starostyn (IPZ-32), Bogdan Voznenko (IPZ-32)  
**Repository:** [4urkaGaming-Corporation/Project-AUTO-SQLANCER](https://github.com/4urkaGaming-Corporation/Project-AUTO-SQLANCER)

---

##  Goals of the Project

The goal was to implement a full automated testing infrastructure for the `auto-sqlancer` project as requested in [issue #23](https://github.com/sqlancer/auto-sqlancer/issues/23). The work involved:

- **GitHub Actions CI pipeline** – Set up a multi-job workflow that runs on every push and pull request to `main`, covering lint, unit tests, and full Docker integration tests.
- **Unit tests (no Docker required)** – Write isolated tests for configuration loading/validation (`test_config.py`) and utility functions (`test_utils.py`) that execute purely in Python with no external dependencies.
- **Integration tests (Docker-based)** – Write an end-to-end test suite (`test_integration_duckdb.py`) that exercises the full SQLancer pipeline using DuckDB as the embedded DBMS.
- **Modular entry point** – Implement a clean CLI (`start.py`) with `build` and `test` sub-commands driven by per-DBMS `config.json` files.
- **Docker image build helpers** – Implement `build.py` with functions to build/pull the SQLancer image, DBMS images, and Docker networks, supporting a `--cache` flag.

---

##  Completed Work

### 1. GitHub Actions Workflow (`.github/workflows/ci.yml`)

A three-job CI pipeline was created:

| Job | Purpose | Requires Docker |
|---|---|---|
| `lint` | Runs `flake8` with strict syntax and complexity checks | No |
| `test-sqlite` | Runs `test_utils.py` + `test_config.py` with pytest | No |
| `test-docker` | Builds SQLancer + DuckDB images and runs `test_integration_duckdb.py` | Yes |

The `test-docker` job includes Docker layer caching (keyed to `duckdb/Dockerfile`), Docker Buildx setup, and automatic log upload on failure via `actions/upload-artifact`.

### 2. Unit Tests – `tests/test_config.py`

Tests for loading and validating `config.json` files used by `start.py`:

- `TestConfigLoading` – Valid load, missing file raises `FileNotFoundError`, malformed JSON raises `JSONDecodeError`.
- `TestRequiredFields` – Parametrized checks that all 9 required fields are present; simulates detection of missing fields.
- `TestFieldConstraints` – Type and value checks: `num_threads` is a positive int, `timeout_seconds > 0`, `embedded` is `"yes"/"no"`, `oracle`/`image_name`/`tag` are non-empty.
- `TestGlobalConfig` – Validates the top-level `config.json` with `dbms_list`, checking it is a non-empty list containing expected DBMS names.

### 3. Unit Tests – `tests/test_utils.py`

Tests for the two helper functions in `utils.py`:

- `TestRunCommand` – Verifies correct exit code capture, that `check=True` raises `CalledProcessError` on non-zero exit, that `check=False` returns the raw exit code, and that stdout is forwarded to the logger at DEBUG level.
- `TestSetupLogging` – Verifies the function returns four values (three loggers + run directory path), that the run directory is created on disk, that all three log files appear after writing, that the directory name matches the timestamp pattern `YY-MM-DD-HH-MM-SS`, and that repeated calls create distinct directories.

### 4. Integration Tests – `tests/test_integration_duckdb.py`

End-to-end tests covering the full DuckDB pipeline:

- All tests are annotated with `@requires_docker`, `@requires_sqlancer_image`, `@requires_duckdb_image` skip markers, so the unit-test job stays fast.
- `test_docker_network_exists` – Confirms the `sqlancer-net` network is present.
- `test_sqlancer_image_present` / `test_duckdb_image_present` – Image existence checks.
- `test_full_duckdb_run` – Launches the SQLancer container with DuckDB config via `docker run --rm`, mounts a host log directory, and asserts exit code 0.
- `test_container_cleanup_after_run` – Confirms no stale containers remain after the `--rm` flag is applied.

### 5. CLI Entry Point – `start.py`

A clean `argparse`-based CLI with two sub-commands:

```
python3 start.py build --sqlancer            # Build SQLancer Docker image
python3 start.py build --dbms duckdb         # Pull/build a DBMS image
python3 start.py build --dbms all            # Build all DBMS images

python3 start.py test --dbms sqlite --config sqlite/config.json
python3 start.py test --dbms all
python3 start.py test --dockerfile path/Dockerfile --config path/config.json
```

All commands support `--cache` to reuse Docker layer cache. Logging is initialised via `setup_logging()` and output is written to a timestamped directory under `logs/`.

### 6. Build Helpers – `build.py`

- `build_sqlancer_image` – Builds `sqlancer:latest` from `./sqlancer/Dockerfile`; supports embedded-DBMS mode (uses a per-DBMS Dockerfile) and skips rebuild if the image already exists.
- `build_network` – Idempotently creates the `sqlancer-net` Docker bridge network.
- `build_db_image` – Pulls or builds a DBMS image by `image_name:tag` from `config.json`; custom Dockerfiles are supported.
- `build_environment` – Orchestrates the above three steps before any test run.

### 7. Utility Helpers – `utils.py`

- `run_command(cmd, logger, check)` – Runs a subprocess, streams stdout line-by-line to the logger at DEBUG level, and optionally raises `CalledProcessError` on non-zero exit.
- `setup_logging(log_dir)` – Creates a timestamped run directory and returns three independent `logging.Logger` instances (`script`, `docker`, `sqlancer`) each writing to their own `.log` file; `script` also prints to stdout.

---

##  Pull Requests & Key Commits

| Commit | Description |
|---|---|
| `b55afbb` | Initial commit – project scaffold |
| `cdcd6de` | Add `ci.yml` – initial GitHub Actions workflow |
| `b0962ab`, `6ad943f`, `4fd89ce`, `d3c3737` | Iterate and fix CI workflow jobs |
| `1d4de85` | Upload core source files (`start.py`, `build.py`, `utils.py`, `test.py`, `config.json`) |
| `b051565` | Create `test_integration_duckdb.py` |
| `7d6015a` | Finalize `test_integration_duckdb.py` |
| `c436621`–`fc3ae9a` | Iterative fixes to integration test |
| `c1412fd` (HEAD) | Final fixes across test suite and CI config |

Full history: [github.com/4urkaGaming-Corporation/Project-AUTO-SQLANCER/commits/main](https://github.com/4urkaGaming-Corporation/Project-AUTO-SQLANCER/commits/main)

---

##  Repository Structure

```
Project-AUTO-SQLANCER/
├── .github/
│   └── workflows/
│       └── ci.yml            # CI pipeline (lint + unit + Docker integration)
├── tests/
│   ├── conftest.py
│   ├── test_config.py        # Unit tests: config.json loading & validation
│   ├── test_utils.py         # Unit tests: run_command & setup_logging
│   └── test_integration_duckdb.py  # Integration tests: full DuckDB pipeline
├── start.py                  # CLI entry point (build / test sub-commands)
├── build.py                  # Docker image & network build helpers
├── test.py                   # Container launch & cleanup logic
├── utils.py                  # run_command + setup_logging helpers
├── config.json               # Global config with dbms_list
├── pytest.ini
└── requirements*.txt
```

---

##  Running the Tests

**Unit tests (no Docker needed):**
```bash
pip install pytest
python -m pytest tests/test_utils.py tests/test_config.py -v
```

**Integration tests (Docker required):**
```bash
# Build required images first
python3 start.py build --sqlancer
python3 start.py build --dbms duckdb
docker network create sqlancer-net

# Run integration tests
python -m pytest tests/test_integration_duckdb.py -v --timeout=300
```

---

##  Summary

This contribution fully resolves [issue #23](https://github.com/sqlancer/auto-sqlancer/issues/23) by delivering a production-ready automated testing infrastructure for `auto-sqlancer`. The solution provides **37 pytest test cases** across three test modules, a **three-job GitHub Actions pipeline** that automatically lints Python code, runs Docker-free unit tests, and executes a real end-to-end DuckDB integration test on every push and pull request.

The unit tests require no external services and run in under 5 seconds, making them ideal for fast feedback on PRs. The integration test suite skips gracefully when Docker is unavailable, ensuring the fast CI job is never blocked. Docker layer caching is used to keep the integration job under 3 minutes in steady state.

The modular CLI (`start.py`) and build helpers (`build.py`) provide the foundation described in the issue for extending coverage to additional DBMS targets such as MySQL, PostgreSQL, TiDB, CockroachDB, and SQLite — each requiring only a `config.json` file and optionally a custom Dockerfile.
