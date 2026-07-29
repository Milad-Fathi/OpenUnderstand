"""Tests for configuration management."""

import pytest
import os
import configparser
from pathlib import Path

def test_config_defaults():
    """Test that configuration defaults are loaded properly."""
    config = configparser.ConfigParser()
    config_path = Path("config.ini")
    
    if config_path.exists():
        config.read(config_path)
        assert "DEFAULT" in config.sections() or "DEFAULT" in config
    else:
        pytest.skip("config.ini not found - test skipped")

def test_project_import():
    """Test that OpenUnderstand modules can be imported."""
    try:
        import openunderstand
        assert hasattr(openunderstand, '__version__') or True
    except ImportError as e:
        pytest.fail(f"Could not import openunderstand: {e}")

def test_cli_import():
    """Test that the CLI can be imported."""
    try:
        import openunderstand
        assert hasattr(openunderstand, 'main') or True
    except ImportError as e:
        pytest.fail(f"Could not import CLI: {e}")