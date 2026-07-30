"""Pytest configuration and fixtures."""

import os
import sys
import tempfile
import time
from pathlib import Path

import pytest

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from openunderstand.oudb import api
from openunderstand.oudb.models import KindModel


@pytest.fixture
def temp_db():
    """Create a temporary database for testing."""
    with tempfile.NamedTemporaryFile(suffix='.oudb', delete=False) as f:
        db_path = f.name

    # Create database with tables
    db = api.create_db(db_path)

    # Ensure default kinds exist
    default_kinds = ["Class", "Method", "Variable", "File", "Package", "Interface", "Unknown"]
    for kind_name in default_kinds:
        KindModel.get_or_create(_name=kind_name, is_ent_kind=True)

    yield db_path

    # Close database connection if possible
    if hasattr(db, 'close'):
        try:
            db.close()
        except AttributeError:
            # Database doesn't have close method
            pass
        except OSError as e:
            # File system error
            print(f"Warning: Could not close database: {e}")

    # Cleanup - try to delete the file
    if os.path.exists(db_path):
        try:
            os.unlink(db_path)
        except PermissionError:
            # File might still be locked, wait and retry
            time.sleep(0.5)
            try:
                if os.path.exists(db_path):
                    os.unlink(db_path)
            except PermissionError:
                # Give up on cleanup - file will be deleted by OS eventually
                pass


@pytest.fixture
def db_connection(temp_db):
    """Get database connection using api.open."""
    return api.open(temp_db)


@pytest.fixture
def class_kind():
    """Get or create Class kind."""
    kind, _ = KindModel.get_or_create(_name="Class", is_ent_kind=True)
    return kind


@pytest.fixture
def method_kind():
    """Get or create Method kind."""
    kind, _ = KindModel.get_or_create(_name="Method", is_ent_kind=True)
    return kind