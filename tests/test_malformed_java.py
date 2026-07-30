"""Tests for handling malformed Java code scenarios."""

import os
import sys
import tempfile
from pathlib import Path

import pytest

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from openunderstand.oudb import api
from openunderstand.oudb.models import EntityModel, KindModel


@pytest.fixture
def temp_db():
    """Create a temporary database for testing."""
    with tempfile.NamedTemporaryFile(suffix='.oudb', delete=False) as f:
        db_path = f.name

    db = api.create_db(db_path)

    default_kinds = ["Class", "Method", "Variable", "File", "Package", "Interface", "Unknown"]
    for kind_name in default_kinds:
        KindModel.get_or_create(_name=kind_name, is_ent_kind=True)

    yield db_path

    if hasattr(db, 'close'):
        try:
            db.close()
        except:
            pass

    if os.path.exists(db_path):
        try:
            os.unlink(db_path)
        except PermissionError:
            pass


@pytest.fixture
def class_kind(temp_db):
    """Get Class kind."""
    kind, _ = KindModel.get_or_create(_name="Class", is_ent_kind=True)
    return kind


@pytest.fixture
def method_kind(temp_db):
    """Get Method kind."""
    kind, _ = KindModel.get_or_create(_name="Method", is_ent_kind=True)
    return kind


def test_malformed_class_missing_brace(temp_db, class_kind):
    """Test handling of malformed class (simulated)."""
    # This simulates a malformed class - missing closing brace
    malformed_class = EntityModel.create(
        _name="MalformedClass",
        _kind=class_kind._id,
        _longname="MalformedClass",
        _contents="public class MalformedClass { public void method() { "  # Missing closing braces
    )

    # Verify the entity was created despite malformed content
    assert malformed_class is not None
    assert malformed_class._name == "MalformedClass"
    # The content should be preserved even if malformed
    assert "{" in malformed_class._contents
    assert "}" not in malformed_class._contents  # Missing closing brace


def test_malformed_missing_semicolon(temp_db, class_kind, method_kind):
    """Test handling of code with missing semicolon."""
    # Create a class
    cls = EntityModel.create(
        _name="Main",
        _kind=class_kind._id,
        _longname="Main"
    )

    # Create a method with missing semicolon in content
    malformed_method = EntityModel.create(
        _name="method",
        _kind=method_kind._id,
        _longname="Main.method",
        _parent=cls._id,
        _contents="public void method() { int x = 5 }"  # Missing semicolon
    )

    # Verify method exists despite malformed content
    assert malformed_method is not None
    assert malformed_method._name == "method"
    # The semicolon is missing
    assert ";" not in malformed_method._contents


def test_malformed_wrong_keyword(temp_db, class_kind):
    """Test handling of code with wrong Java keyword."""
    # Simulate a class with wrong keyword (e.g., "publc" instead of "public")
    malformed_class = EntityModel.create(
        _name="InvalidClass",
        _kind=class_kind._id,
        _longname="InvalidClass",
        _contents="publc class InvalidClass { }"  # Wrong keyword
    )

    # Entity should still be created
    assert malformed_class is not None
    assert malformed_class._name == "InvalidClass"
    # The content should preserve the malformed syntax
    assert "publc" in malformed_class._contents


def test_malformed_extra_brace(temp_db, class_kind, method_kind):
    """Test handling of code with extra braces."""
    cls = EntityModel.create(
        _name="ExtraBraces",
        _kind=class_kind._id,
        _longname="ExtraBraces"
    )

    malformed_method = EntityModel.create(
        _name="method",
        _kind=method_kind._id,
        _longname="ExtraBraces.method",
        _parent=cls._id,
        _contents="public void method() { { { } } }"  # Extra braces
    )

    assert malformed_method is not None
    # Extra braces should be preserved in content
    assert malformed_method._contents.count("{") == 3
    assert malformed_method._contents.count("}") == 3


def test_malformed_unclosed_string(temp_db, class_kind):
    """Test handling of code with unclosed string."""
    malformed_class = EntityModel.create(
        _name="StringError",
        _kind=class_kind._id,
        _longname="StringError",
        _contents='public class StringError { public void method() { String s = "unclosed; } }'
    )

    assert malformed_class is not None
    # The malformed string content should be preserved
    assert '"unclosed;' in malformed_class._contents