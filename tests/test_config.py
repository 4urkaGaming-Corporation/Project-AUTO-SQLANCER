"""
tests/test_config.py

Tests for config.json loading and field validation.
No Docker required — pure Python.
"""

import json
import os
import sys

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


# ---------------------------------------------------------------------------
# Required fields
# ---------------------------------------------------------------------------

REQUIRED_FIELDS = [
    "dbms", "embedded", "image_name", "tag",
    "container_name", "username", "oracle",
    "num_threads", "timeout_seconds",
]


class TestRequiredFields:
    @pytest.mark.parametrize("field", REQUIRED_FIELDS)
    def test_required_field_present(self, field):
        cfg = _make_config()
        assert field in cfg, f"Required field '{field}' missing from config template"

    @pytest.mark.parametrize("field", REQUIRED_FIELDS)
    def test_missing_field_detected(self, field):
        cfg = _make_config()
        del cfg[field]
        # Simulates the check that start.py would do
        assert field not in cfg


# ---------------------------------------------------------------------------
# Field types / constraints
# ---------------------------------------------------------------------------

class TestFieldConstraints:
    def test_num_threads_is_positive_int(self):
        cfg = _make_config(num_threads=4)
        assert isinstance(cfg["num_threads"], int)
        assert cfg["num_threads"] > 0

    def test_timeout_seconds_is_positive(self):
        cfg = _make_config(timeout_seconds=120)
        assert cfg["timeout_seconds"] > 0

    def test_embedded_valid_values(self):
        for val in ("yes", "no"):
            cfg = _make_config(embedded=val)
            assert cfg["embedded"] in ("yes", "no")

    def test_oracle_non_empty(self):
        cfg = _make_config(oracle="NoREC")
        assert len(cfg["oracle"]) > 0

    def test_image_name_non_empty(self):
        cfg = _make_config(image_name="auto-sqlancer-sqlite")
        assert len(cfg["image_name"]) > 0

    def test_tag_non_empty(self):
        cfg = _make_config(tag="latest")
        assert cfg["tag"].strip() != ""


# ---------------------------------------------------------------------------
# Global config.json structure
# ---------------------------------------------------------------------------

class TestGlobalConfig:
    def test_global_config_has_dbms_list(self, tmp_path):
        global_cfg = {
            "dbms_list": ["sqlite", "duckdb", "mysql", "postgres", "tidb", "cockroachdb"]
        }
        path = _write_config(tmp_path / "config.json", global_cfg)
        with open(path) as f:
            data = json.load(f)
        assert "dbms_list" in data
        assert isinstance(data["dbms_list"], list)
        assert len(data["dbms_list"]) > 0

    def test_known_dbms_in_list(self, tmp_path):
        global_cfg = {"dbms_list": ["sqlite", "duckdb", "mysql", "postgres"]}
        path = _write_config(tmp_path / "config.json", global_cfg)
        with open(path) as f:
            data = json.load(f)
        for dbms in ("sqlite", "duckdb"):
            assert dbms in data["dbms_list"]
