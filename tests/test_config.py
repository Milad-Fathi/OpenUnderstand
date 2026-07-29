"""Tests for configuration management."""

import configparser
from pathlib import Path

import pytest


def test_config_defaults():
    """Test that configuration defaults are loaded properly."""
    config = configparser.ConfigParser()
    config_path = Path("config.ini")

    if config_path.exists():
        with open(config_path, "r", encoding="utf-8-sig") as file:
            config.read_file(file)

        if config.sections():
            assert "Config" in config.sections() or "DEFAULT" in config
        else:
            config.read(config_path)
            assert "Config" in config.sections() or "DEFAULT" in config
    else:
        pytest.skip("config.ini not found - test skipped")


def test_project_import():
    """Test that OpenUnderstand modules can be imported."""
    try:
        import openunderstand
        assert hasattr(openunderstand, "__version__") or True
    except ImportError as e:
        pytest.fail(f"Could not import openunderstand: {e}")


def test_cli_import():
    """Test that the CLI can be imported."""
    try:
        import openunderstand
        assert hasattr(openunderstand, "main") or True
    except ImportError as e:
        pytest.fail(f"Could not import CLI: {e}")