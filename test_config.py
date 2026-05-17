"""
tests/test_config.py

Tests for config.json loading and field validation.
No Docker required — pure Python.
"""

import json
import os
import sys
import tempfile

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))


# ---------------------------------------------------------------------------
# Helpers — minimal valid config templates
# ---------------------------------------------------------------------------

def _make_config(**overrides) -> dict:
    base = {
        "dbms": "sqlite",
        "embedded": "yes",
        "image_name": "auto-sqlancer-sqlite",
        "tag": "latest",
        "container_name": "sqlite-sqlancer",
        "username": "root",
        "password": "",
        "oracle": "NoREC",
        "num_threads": 1,
        "timeout_seconds": 60,
        "env": {},
    }
    base.update(overrides)
    return base


def _write_config(path, data):
    with open(path, "w") as f:
        json.dump(data, f)
    return path


