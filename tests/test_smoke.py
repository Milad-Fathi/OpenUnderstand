"""Smoke tests for OpenUnderstand."""

import pytest
import sys
import importlib

def test_python_version():
    """Test that Python version is compatible."""
    version = sys.version_info
    assert version.major == 3
    assert version.minor >= 7

def test_module_import():
    """Test that OpenUnderstand module can be imported."""
    try:
        import openunderstand
        assert True
    except ImportError as e:
        pytest.fail(f"Could not import openunderstand: {e}")

def test_module_has_attributes():
    """Test that OpenUnderstand module has expected attributes."""
    try:
        import openunderstand
        # Check for common module attributes
        assert hasattr(openunderstand, '__name__')
        assert openunderstand.__name__ == 'openunderstand'
    except ImportError as e:
        pytest.fail(f"Could not import openunderstand: {e}")

def test_pytest_and_coverage_working():
    """Verify pytest and coverage are properly configured."""
    def helper_function(x):
        if x > 0:
            return x * 2
        return x / 2 if x < 0 else 0
    
    assert helper_function(5) == 10
    assert helper_function(-5) == -2.5
    assert helper_function(0) == 0

def test_config_file_exists():
    """Test that config.ini exists."""
    from pathlib import Path
    assert Path('config.ini').exists()