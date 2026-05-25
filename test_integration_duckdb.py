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
