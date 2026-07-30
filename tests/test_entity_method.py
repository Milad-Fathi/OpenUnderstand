"""Tests for Method entity in OpenUnderstand."""

import pytest
import tempfile
import os
import sys
from pathlib import Path

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
    
    try:
        if hasattr(db, 'close'):
            db.close()
    except:
        pass
    
    if os.path.exists(db_path):
        try:
            os.unlink(db_path)
        except PermissionError:
            import time
            time.sleep(0.5)
            try:
                os.unlink(db_path)
            except:
                pass


def test_create_method_entity(temp_db):
    """Test creating a method entity."""
    method_kind, _ = KindModel.get_or_create(_name="Method", is_ent_kind=True)
    
    entity = EntityModel.create(
        _name="add",
        _kind=method_kind._id,
        _longname="Calculator.add",
        _parent=None
    )
    
    assert entity is not None
    assert entity._name == "add"
    assert entity._kind._name == "Method"
    assert entity._longname == "Calculator.add"


def test_method_belongs_to_class(temp_db):
    """Test method belongs to a class."""
    class_kind, _ = KindModel.get_or_create(_name="Class", is_ent_kind=True)
    method_kind, _ = KindModel.get_or_create(_name="Method", is_ent_kind=True)
    
    # Create class
    calc = EntityModel.create(
        _name="Calculator",
        _kind=class_kind._id,
        _longname="Calculator"
    )
    
    # Create method
    method = EntityModel.create(
        _name="add",
        _kind=method_kind._id,
        _longname="Calculator.add",
        _parent=calc
    )
    
    assert method._parent == calc
    
    # Verify method is child of class
    class_methods = EntityModel.select().where(
        (EntityModel._parent == calc) &
        (EntityModel._kind == method_kind._id)
    )
    assert class_methods.count() >= 1
    assert class_methods[0]._name == "add"


def test_method_parameters(temp_db):
    """Test method with parameters."""
    method_kind, _ = KindModel.get_or_create(_name="Method", is_ent_kind=True)
    
    method = EntityModel.create(
        _name="add",
        _kind=method_kind._id,
        _longname="Calculator.add",
        _type="int,int -> int",
        _value="a,b"
    )
    
    assert method._type == "int,int -> int"
    assert method._value == "a,b"


def test_constructor_method(temp_db):
    """Test constructor method."""
    method_kind, _ = KindModel.get_or_create(_name="Method", is_ent_kind=True)
    
    constructor = EntityModel.create(
        _name="Calculator",
        _kind=method_kind._id,
        _longname="Calculator.Calculator",
        _parent=None
    )
    
    assert constructor._name == "Calculator"
    assert constructor._kind._name == "Method"


def test_unresolved_method(temp_db):
    """Test unresolved/unknown method."""
    unknown_kind, _ = KindModel.get_or_create(_name="Unknown", is_ent_kind=True)
    
    unresolved = EntityModel.create(
        _name="unknownMethod",
        _kind=unknown_kind._id,
        _longname="unknownMethod",
        _parent=None
    )
    
    assert unresolved._name == "unknownMethod"
    assert unresolved._kind._name == "Unknown"


def test_method_with_contents(temp_db):
    """Test method with source contents."""
    method_kind, _ = KindModel.get_or_create(_name="Method", is_ent_kind=True)
    
    method = EntityModel.create(
        _name="add",
        _kind=method_kind._id,
        _longname="Calculator.add",
        _contents="public int add(int a, int b) { return a + b; }"
    )
    
    assert method._contents is not None
    assert "return a + b" in method._contents


def test_multiple_methods_in_class(temp_db):
    """Test multiple methods in a class."""
    class_kind, _ = KindModel.get_or_create(_name="Class", is_ent_kind=True)
    method_kind, _ = KindModel.get_or_create(_name="Method", is_ent_kind=True)
    
    # Create class
    calc = EntityModel.create(
        _name="Calculator",
        _kind=class_kind._id,
        _longname="Calculator"
    )
    
    # Create multiple methods
    method_names = ["add", "subtract", "multiply", "divide"]
    for name in method_names:
        EntityModel.create(
            _name=name,
            _kind=method_kind._id,
            _longname=f"Calculator.{name}",
            _parent=calc
        )
    
    # Verify all methods are in the class
    class_methods = EntityModel.select().where(
        (EntityModel._parent == calc) &
        (EntityModel._kind == method_kind._id)
    )
    assert class_methods.count() >= 4
    found_names = [m._name for m in class_methods]
    for name in method_names:
        assert name in found_names


def test_method_visibility(temp_db):
    """Test method visibility."""
    method_kind, _ = KindModel.get_or_create(_name="Method", is_ent_kind=True)
    
    public_method = EntityModel.create(
        _name="publicMethod",
        _kind=method_kind._id,
        _longname="publicMethod",
        _type="public"
    )
    assert public_method._type == "public"
    
    private_method = EntityModel.create(
        _name="privateMethod",
        _kind=method_kind._id,
        _longname="privateMethod",
        _type="private"
    )
    assert private_method._type == "private"


def test_method_return_type(temp_db):
    """Test method return type."""
    method_kind, _ = KindModel.get_or_create(_name="Method", is_ent_kind=True)
    
    method = EntityModel.create(
        _name="add",
        _kind=method_kind._id,
        _longname="Calculator.add",
        _type="int"
    )
    
    assert method._type == "int"


def test_method_name_uniqueness(temp_db):
    """Test multiple methods with same name but different classes."""
    class_kind, _ = KindModel.get_or_create(_name="Class", is_ent_kind=True)
    method_kind, _ = KindModel.get_or_create(_name="Method", is_ent_kind=True)
    
    # Create two classes
    class1 = EntityModel.create(
        _name="Class1",
        _kind=class_kind._id,
        _longname="Class1"
    )
    
    class2 = EntityModel.create(
        _name="Class2",
        _kind=class_kind._id,
        _longname="Class2"
    )
    
    # Create methods with same name in different classes
    EntityModel.create(
        _name="sameMethod",
        _kind=method_kind._id,
        _longname="Class1.sameMethod",
        _parent=class1
    )
    
    EntityModel.create(
        _name="sameMethod",
        _kind=method_kind._id,
        _longname="Class2.sameMethod",
        _parent=class2
    )
    
    # Verify both methods exist
    methods = EntityModel.select().where(EntityModel._name == "sameMethod")
    assert methods.count() >= 2