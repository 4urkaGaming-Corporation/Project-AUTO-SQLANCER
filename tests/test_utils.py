"""
tests/test_utils.py

Unit tests for utils.py helper functions.
Tests run without Docker — safe for any CI environment.
"""

import logging
import os
import subprocess
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest  # noqa: E402

from utils import run_command, setup_logging  # noqa: E402

# On Windows "python3" may not exist — use the current interpreter instead
PYTHON = sys.executable


# ---------------------------------------------------------------------------
# run_command
# ---------------------------------------------------------------------------

class TestRunCommand:
    def test_simple_echo(self, tmp_path):
        logger = logging.getLogger("test_echo")
        rc = run_command([PYTHON, "-c", "print('hello')"], logger, check=True)
        assert rc == 0

    def test_exit_code_captured(self, tmp_path):
        logger = logging.getLogger("test_exit")
        rc = run_command([PYTHON, "-c", "import sys; sys.exit(0)"], logger, check=False)
        assert rc == 0

    def test_nonzero_raises_when_check_true(self):
        logger = logging.getLogger("test_raise")
        with pytest.raises(subprocess.CalledProcessError):
            run_command([PYTHON, "-c", "import sys; sys.exit(42)"], logger, check=True)

    def test_nonzero_no_raise_when_check_false(self):
        logger = logging.getLogger("test_no_raise")
        rc = run_command(
            [PYTHON, "-c", "import sys; sys.exit(7)"],
            logger,
            check=False,
        )
        assert rc == 7

    def test_stdout_captured_to_logger(self, tmp_path):
        """run_command should forward subprocess stdout to the logger (DEBUG level)."""
        log_file = tmp_path / "out.log"
        logger = logging.getLogger("test_capture")
        logger.setLevel(logging.DEBUG)
        fh = logging.FileHandler(str(log_file))
        fh.setLevel(logging.DEBUG)
        logger.addHandler(fh)

        run_command([PYTHON, "-c", "print('captured_line')"], logger)

        fh.flush()
        fh.close()

        content = log_file.read_text()
        assert "captured_line" in content


# ---------------------------------------------------------------------------
# setup_logging
# ---------------------------------------------------------------------------

class TestSetupLogging:
    def test_returns_four_values(self, tmp_path):
        script_log, docker_log, sqlancer_log, run_dir = setup_logging(str(tmp_path))
        assert script_log is not None
        assert docker_log is not None
        assert sqlancer_log is not None
        assert isinstance(run_dir, str)

    def test_run_dir_is_created(self, tmp_path):
        _, _, _, run_dir = setup_logging(str(tmp_path))
        assert os.path.isdir(run_dir)

    def test_log_files_exist_after_write(self, tmp_path):
        script_log, docker_log, sqlancer_log, run_dir = setup_logging(str(tmp_path))
        script_log.info("script entry")
        docker_log.debug("docker entry")
        sqlancer_log.debug("sqlancer entry")

        for lg in (script_log, docker_log, sqlancer_log):
            for h in lg.handlers:
                h.flush()

        files = os.listdir(run_dir)
        assert "script.log" in files
        assert "docker.log" in files
        assert "sqlancer.log" in files

    def test_run_dir_uses_timestamp_pattern(self, tmp_path):
        import re
        _, _, _, run_dir = setup_logging(str(tmp_path))
        pattern = r"\d{2}-\d{2}-\d{2}-\d{2}-\d{2}-\d{2}$"
        assert re.search(pattern, run_dir), f"run_dir '{run_dir}' doesn't match timestamp pattern"

    def test_multiple_calls_create_separate_dirs(self, tmp_path):
        import time
        _, _, _, run_dir1 = setup_logging(str(tmp_path))
        time.sleep(1)
        _, _, _, run_dir2 = setup_logging(str(tmp_path))
        assert run_dir1 != run_dir2
