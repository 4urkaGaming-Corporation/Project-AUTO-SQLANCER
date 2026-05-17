"""
tests/test_utils.py

Unit tests for utils.py helper functions.
Tests run without Docker — safe for any CI environment.
"""

import logging
import os
import subprocess
import sys
import tempfile

import pytest

# Make sure we can import from the project root
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from utils import run_command, setup_logging

# On Windows "python3" may not exist — use the current interpreter instead
PYTHON = sys.executable


# ---------------------------------------------------------------------------
# run_command
# ---------------------------------------------------------------------------

class TestRunCommand:
    def test_simple_echo(self, tmp_path):
        logger = logging.getLogger("test_echo")
        # Use Python to print instead of shell "echo" (works on Windows too)
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


