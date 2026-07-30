"""Tests for edge cases in OpenUnderstand."""

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


def test_empty_class(temp_db, class_kind):
    """Test an empty class with no methods."""
    # Create an empty class
    empty = EntityModel.create(
        _name="Empty",
        _kind=class_kind._id,
        _longname="Empty",
        _contents="public class Empty { }"
    )

    assert empty is not None
    assert empty._name == "Empty"
    assert empty._kind._name == "Class"

    # Should have no methods
    methods = EntityModel.select().where(EntityModel._parent == empty._id)
    assert methods.count() == 0


def test_class_with_long_name(temp_db, class_kind):
    """Test class with very long name."""
    long_name = "VeryLongClassName" + "A" * 100

    cls = EntityModel.create(
        _name=long_name,
        _kind=class_kind._id,
        _longname=long_name,
        _contents=f"public class {long_name} {{ }}"
    )

    assert cls is not None
    assert cls._name == long_name


def test_class_with_many_methods(temp_db, class_kind, method_kind):
    """Test class with many methods."""
    # Create class
    cls = EntityModel.create(
        _name="ManyMethods",
        _kind=class_kind._id,
        _longname="ManyMethods"
    )

    # Create 50 methods
    for i in range(50):
        EntityModel.create(
            _name=f"method{i}",
            _kind=method_kind._id,
            _longname=f"ManyMethods.method{i}",
            _parent=cls
        )

    # Verify all methods were created
    methods = EntityModel.select().where(EntityModel._parent == cls._id)
    assert methods.count() == 50


def test_class_with_special_characters(temp_db, class_kind):
    """Test class with special characters in name."""
    special_names = ["MyClass_123", "My-Class", "My$Class", "_PrivateClass"]

    for name in special_names:
        cls = EntityModel.create(
            _name=name,
            _kind=class_kind._id,
            _longname=name,
            _contents=f"public class {name} {{ }}"
        )
        assert cls is not None
        assert cls._name == name


def test_deep_inheritance_chain(temp_db, class_kind):
    """Test deep inheritance chain."""
    # Create 10 levels of inheritance
    parent = None
    for i in range(10):
        cls = EntityModel.create(
            _name=f"Level{i}",
            _kind=class_kind._id,
            _longname=f"Level{i}",
            _parent=parent  # Pass the parent Entity object
        )
        parent = cls

    # Verify chain length
    # Start from root (Level0 has no parent)
    root = EntityModel.get(EntityModel._name == "Level0")
    assert root._parent is None

    # Follow chain down
    current = root
    for i in range(10):
        assert current._name == f"Level{i}"
        # Get next level
        children = EntityModel.select().where(EntityModel._parent == current)
        if i < 9:
            assert children.count() == 1
            current = children[0]
        else:
            assert children.count() == 0


def test_multiple_packages(temp_db, class_kind):
    """Test classes in multiple packages."""
    # Create Package kind
    package_kind, _ = KindModel.get_or_create(_name="Package", is_ent_kind=True)

    # Create packages
    packages = ["com.example", "com.test", "org.open"]
    for pkg_name in packages:
        pkg = EntityModel.create(
            _name=pkg_name,
            _kind=package_kind._id,
            _longname=pkg_name
        )

        # Create a class in each package
        EntityModel.create(
            _name=f"ClassIn{'_'.join(pkg_name.split('.'))}",
            _kind=class_kind._id,
            _longname=f"{pkg_name}.Class",
            _parent=pkg
        )

    # Verify all packages have classes
    for pkg_name in packages:
        pkg = EntityModel.get(EntityModel._name == pkg_name)
        classes = EntityModel.select().where(EntityModel._parent == pkg)
        assert classes.count() == 1