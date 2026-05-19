"""
tests/conftest.py

Shared pytest configuration and fixtures.
"""

import os
import sys

# Ensure project root is on the path so all imports work
# regardless of where pytest is invoked from.
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
