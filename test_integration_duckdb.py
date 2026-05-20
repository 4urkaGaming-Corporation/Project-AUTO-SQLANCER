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
