"""Smoke tests for OpenUnderstand."""

import sys
import pytest


def test_python_version():
    """Test that Python version is compatible."""
    version = sys.version_info
    assert version.major == 3
    assert version.minor >= 7


def test_module_import():
    """Test that OpenUnderstand module can be imported."""
    import openunderstand
    assert openunderstand is not None


def test_pytest_and_coverage_working():
    """Verify pytest and coverage are properly configured."""
    def helper_function(x):
        if x > 0:
            return x * 2
        return x / 2 if x < 0 else 0

    assert helper_function(5) == 10
    assert helper_function(-5) == -2.5
    assert helper_function(0) == 0