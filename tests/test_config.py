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


# ---------------------------------------------------------------------------
# Loading
# ---------------------------------------------------------------------------

class TestConfigLoading:
    def test_valid_config_loads(self, tmp_path):
        cfg_path = _write_config(tmp_path / "config.json", _make_config())
        with open(cfg_path) as f:
            cfg = json.load(f)
        assert cfg["dbms"] == "sqlite"

    def test_missing_file_raises(self, tmp_path):
        with pytest.raises(FileNotFoundError):
            with open(tmp_path / "nonexistent.json") as f:
                json.load(f)

    def test_malformed_json_raises(self, tmp_path):
        bad = tmp_path / "bad.json"
        bad.write_text("{not valid json")
        with pytest.raises(json.JSONDecodeError):
            with open(bad) as f:
                json.load(f)


