"""
tests/test_integration_duckdb.py

Integration tests that actually exercise the full pipeline using DuckDB
(the lightest embedded-friendly DBMS in the project).

Requirements:
  - Docker daemon running
  - sqlancer:latest image built  (`python3 start.py build --sqlancer`)
  - auto-sqlancer-duckdb:latest built  (`python3 start.py build --dbms duckdb`)
  - Docker network `sqlancer-net` exists

These tests are skipped automatically when Docker is unavailable so the
lint / unit-test job stays fast.
"""

import json
import logging
import os
import subprocess
import sys
import time

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from utils import run_command, setup_logging


# ---------------------------------------------------------------------------
# Helpers / fixtures
# ---------------------------------------------------------------------------

def _docker_available() -> bool:
    try:
        result = subprocess.run(
            ["docker", "info"],
            capture_output=True,
            timeout=10,
        )
        return result.returncode == 0
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return False


def _image_exists(name: str) -> bool:
    result = subprocess.run(
        ["docker", "image", "inspect", name],
        capture_output=True,
    )
    return result.returncode == 0


def _network_exists(name: str) -> bool:
    result = subprocess.run(
        ["docker", "network", "inspect", name],
        capture_output=True,
    )
    return result.returncode == 0


def _container_running(name: str) -> bool:
    result = subprocess.run(
        ["docker", "ps", "--filter", f"name={name}", "--format", "{{.Names}}"],
        capture_output=True,
        text=True,
    )
    return name in result.stdout


requires_docker = pytest.mark.skipif(
    not _docker_available(),
    reason="Docker daemon not available",
)

requires_sqlancer_image = pytest.mark.skipif(
    not _image_exists("sqlancer:latest"),
    reason="sqlancer:latest image not built — run: python3 start.py build --sqlancer",
)

requires_duckdb_image = pytest.mark.skipif(
    not _image_exists("auto-sqlancer-duckdb:latest"),
    reason="auto-sqlancer-duckdb:latest not built — run: python3 start.py build --dbms duckdb",
)


DUCKDB_CONFIG = {
    "dbms": "duckdb",
    "embedded": "yes",
    "image_name": "auto-sqlancer-duckdb",
    "tag": "latest",
    "container_name": "duckdb-sqlancer-ci",
    "username": "root",
    "password": "",
    "oracle": "NoREC",
    "num_threads": 1,
    # Short timeout — enough to validate the run starts and doesn't crash
    "timeout_seconds": 30,
    "env": {},
}


@pytest.fixture(scope="module")
def logging_setup(tmp_path_factory):
    log_base = str(tmp_path_factory.mktemp("logs"))
    script_log, docker_log, sqlancer_log, run_dir = setup_logging(log_base)
    return script_log, docker_log, sqlancer_log, run_dir


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

@requires_docker
def test_docker_network_exists():
    """sqlancer-net must exist before any container test runs."""
    assert _network_exists("sqlancer-net"), (
        "Docker network 'sqlancer-net' not found. "
        "Create it with: docker network create sqlancer-net"
    )


@requires_docker
@requires_sqlancer_image
def test_sqlancer_image_present():
    assert _image_exists("sqlancer:latest")


@requires_docker
@requires_duckdb_image
def test_duckdb_image_present():
    assert _image_exists("auto-sqlancer-duckdb:latest")
