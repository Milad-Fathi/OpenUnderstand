"""Tests for Class entity in OpenUnderstand."""

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
        except AttributeError:
            pass
        except OSError as e:
            print(f"Warning: Could not close database: {e}")

    if os.path.exists(db_path):
        try:
            os.unlink(db_path)
        except PermissionError:
            time.sleep(0.5)
            try:
                if os.path.exists(db_path):
                    os.unlink(db_path)
            except PermissionError:
                pass


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


def test_create_class_entity(temp_db):
    """Test creating a class entity."""
    class_kind, _ = KindModel.get_or_create(_name="Class", is_ent_kind=True)

    entity = EntityModel.create(
        _name="Calculator",
        _kind=class_kind._id,
        _longname="Calculator",
        _parent=None
    )

    assert entity is not None
    assert entity._name == "Calculator"
    assert entity._kind._name == "Class"
    assert entity._longname == "Calculator"
    assert entity._parent is None


def test_class_fully_qualified_name(temp_db):
    """Test class with fully qualified name."""
    class_kind, _ = KindModel.get_or_create(_name="Class", is_ent_kind=True)

    entity = EntityModel.create(
        _name="Calculator",
        _kind=class_kind._id,
        _longname="com.example.Calculator",
        _parent=None
    )

    assert entity._longname == "com.example.Calculator"


def test_class_parent_child_relationship(temp_db):
    """Test parent-child relationships for classes."""
    class_kind, _ = KindModel.get_or_create(_name="Class", is_ent_kind=True)

    parent = EntityModel.create(
        _name="Animal",
        _kind=class_kind._id,
        _longname="Animal"
    )

    child = EntityModel.create(
        _name="Dog",
        _kind=class_kind._id,
        _longname="Dog",
        _parent=parent
    )

    assert child._parent == parent

    children = EntityModel.select().where(EntityModel._parent == parent)
    assert children.count() >= 1
    assert children[0]._name == "Dog"


def test_class_contains_methods(temp_db):
    """Test that classes contain methods."""
    class_kind, _ = KindModel.get_or_create(_name="Class", is_ent_kind=True)
    method_kind, _ = KindModel.get_or_create(_name="Method", is_ent_kind=True)

    calc = EntityModel.create(
        _name="Calculator",
        _kind=class_kind._id,
        _longname="Calculator"
    )

    EntityModel.create(
        _name="add",
        _kind=method_kind._id,
        _longname="Calculator.add",
        _parent=calc
    )

    EntityModel.create(
        _name="subtract",
        _kind=method_kind._id,
        _longname="Calculator.subtract",
        _parent=calc
    )

    methods = EntityModel.select().where(
        (EntityModel._parent == calc) &
        (EntityModel._kind == method_kind._id)
    )
    assert methods.count() >= 2
    method_names = [m._name for m in methods]
    assert "add" in method_names
    assert "subtract" in method_names


def test_unresolved_class(temp_db):
    """Test handling of unresolved/unknown classes."""
    unknown_kind, _ = KindModel.get_or_create(_name="Unknown", is_ent_kind=True)

    unresolved = EntityModel.create(
        _name="UnknownClass",
        _kind=unknown_kind._id,
        _longname="UnknownClass",
        _parent=None
    )

    assert unresolved._name == "UnknownClass"
    assert unresolved._kind._name == "Unknown"


def test_class_value_and_type(temp_db):
    """Test class with value and type attributes."""
    class_kind, _ = KindModel.get_or_create(_name="Class", is_ent_kind=True)

    entity = EntityModel.create(
        _name="Constants",
        _kind=class_kind._id,
        _longname="Constants",
        _value="VALUE",
        _type="String",
        _contents='public class Constants { public static final String VALUE = "test"; }'
    )

    assert entity._value == "VALUE"
    assert entity._type == "String"
    assert entity._contents is not None


def test_class_inheritance_chain(temp_db):
    """Test inheritance chain (multi-level)."""
    class_kind, _ = KindModel.get_or_create(_name="Class", is_ent_kind=True)

    animal = EntityModel.create(
        _name="Animal",
        _kind=class_kind._id,
        _longname="Animal"
    )

    mammal = EntityModel.create(
        _name="Mammal",
        _kind=class_kind._id,
        _longname="Mammal",
        _parent=animal
    )

    dog = EntityModel.create(
        _name="Dog",
        _kind=class_kind._id,
        _longname="Dog",
        _parent=mammal
    )

    assert mammal._parent == animal
    assert dog._parent == mammal

    children_of_animal = EntityModel.select().where(EntityModel._parent == animal)
    assert children_of_animal.count() >= 1
    assert children_of_animal[0]._name == "Mammal"

    children_of_mammal = EntityModel.select().where(EntityModel._parent == mammal)
    assert children_of_mammal.count() >= 1
    assert children_of_mammal[0]._name == "Dog"


def test_multiple_classes_same_parent(temp_db):
    """Test multiple classes with same parent."""
    class_kind, _ = KindModel.get_or_create(_name="Class", is_ent_kind=True)
    package_kind, _ = KindModel.get_or_create(_name="Package", is_ent_kind=True)

    package = EntityModel.create(
        _name="com.example",
        _kind=package_kind._id,
        _longname="com.example"
    )

    class_names = ["ClassA", "ClassB", "ClassC"]
    for name in class_names:
        EntityModel.create(
            _name=name,
            _kind=class_kind._id,
            _longname=f"com.example.{name}",
            _parent=package
        )

    package_classes = EntityModel.select().where(
        (EntityModel._parent == package) &
        (EntityModel._kind == class_kind._id)
    )
    assert package_classes.count() >= 3


def test_class_with_contents(temp_db):
    """Test class with source contents."""
    class_kind, _ = KindModel.get_or_create(_name="Class", is_ent_kind=True)

    entity = EntityModel.create(
        _name="Calculator",
        _kind=class_kind._id,
        _longname="Calculator",
        _contents='public class Calculator { public int add(int a, int b) { return a + b; } }'
    )

    assert entity._contents is not None
    assert "add" in entity._contents


def test_class_parent_retrieval(temp_db):
    """Test retrieving parent of a class."""
    class_kind, _ = KindModel.get_or_create(_name="Class", is_ent_kind=True)

    parent = EntityModel.create(
        _name="Animal",
        _kind=class_kind._id,
        _longname="Animal"
    )

    child = EntityModel.create(
        _name="Dog",
        _kind=class_kind._id,
        _longname="Dog",
        _parent=parent
    )

    retrieved_parent = child._parent
    assert retrieved_parent._name == "Animal"
    assert retrieved_parent == parent


def test_multiple_children_same_parent(temp_db):
    """Test multiple children with same parent."""
    class_kind, _ = KindModel.get_or_create(_name="Class", is_ent_kind=True)

    parent = EntityModel.create(
        _name="Animal",
        _kind=class_kind._id,
        _longname="Animal"
    )

    children_names = ["Dog", "Cat", "Bird"]
    for name in children_names:
        EntityModel.create(
            _name=name,
            _kind=class_kind._id,
            _longname=name,
            _parent=parent
        )

    children = EntityModel.select().where(EntityModel._parent == parent)
    assert children.count() >= 3
    child_names = [c._name for c in children]
    for name in children_names:
        assert name in child_names


def test_class_interface_implementation(temp_db):
    """Test class implementing an interface."""
    class_kind, _ = KindModel.get_or_create(_name="Class", is_ent_kind=True)
    interface_kind, _ = KindModel.get_or_create(_name="Interface", is_ent_kind=True)

    interface = EntityModel.create(
        _name="Drawable",
        _kind=interface_kind._id,
        _longname="Drawable"
    )

    circle = EntityModel.create(
        _name="Circle",
        _kind=class_kind._id,
        _longname="Circle",
        _parent=interface
    )

    assert circle._parent == interface