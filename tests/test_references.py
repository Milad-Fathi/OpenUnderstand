"""Tests for references (calls, imports, inheritance) in OpenUnderstand."""

import os
import sys
import tempfile
from pathlib import Path

import pytest

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from openunderstand.oudb import api
from openunderstand.oudb.models import EntityModel, ReferenceModel, KindModel


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


@pytest.fixture
def interface_kind(temp_db):
    """Get Interface kind."""
    kind, _ = KindModel.get_or_create(_name="Interface", is_ent_kind=True)
    return kind


@pytest.fixture
def call_kind(temp_db):
    """Get Call reference kind."""
    kind, _ = KindModel.get_or_create(_name="Java Call", is_ent_kind=False)
    return kind


@pytest.fixture
def import_kind(temp_db):
    """Get Import reference kind."""
    kind, _ = KindModel.get_or_create(_name="Java Import", is_ent_kind=False)
    return kind


@pytest.fixture
def extend_kind(temp_db):
    """Get Extend reference kind."""
    kind, _ = KindModel.get_or_create(_name="Java Extend", is_ent_kind=False)
    return kind


@pytest.fixture
def implement_kind(temp_db):
    """Get Implement reference kind."""
    kind, _ = KindModel.get_or_create(_name="Java Implement", is_ent_kind=False)
    return kind


def test_create_call_reference(temp_db, class_kind, method_kind, call_kind):
    """Test creating a method call reference between entities."""
    # Create caller class
    caller = EntityModel.create(
        _name="Main",
        _kind=class_kind._id,
        _longname="Main"
    )

    # Create caller method
    caller_method = EntityModel.create(
        _name="main",
        _kind=method_kind._id,
        _longname="Main.main",
        _parent=caller
    )

    # Create callee method
    callee = EntityModel.create(
        _name="add",
        _kind=method_kind._id,
        _longname="Calculator.add"
    )

    # Create call reference
    call_ref = ReferenceModel.create(
        _kind=call_kind._id,
        _file=caller._id,
        _line=10,
        _column=5,
        _ent=callee._id,
        _scope=caller_method._id
    )

    # Verify call reference was created
    assert call_ref is not None
    assert call_ref._kind._name == "Java Call"
    assert call_ref._ent._name == "add"
    assert call_ref._scope._name == "main"


def test_inverse_reference(temp_db, class_kind, method_kind, call_kind):
    """Test inverse references (finding who calls a method)."""
    # Create a target method
    target_method = EntityModel.create(
        _name="compute",
        _kind=method_kind._id,
        _longname="Calculator.compute"
    )

    # Create multiple callers
    callers = []
    for i in range(3):
        caller_class = EntityModel.create(
            _name=f"Caller{i}",
            _kind=class_kind._id,
            _longname=f"Caller{i}"
        )
        caller_method = EntityModel.create(
            _name=f"method{i}",
            _kind=method_kind._id,
            _longname=f"Caller{i}.method{i}",
            _parent=caller_class
        )
        callers.append(caller_method)

        # Create call references from each caller to the target method
        ReferenceModel.create(
            _kind=call_kind._id,
            _file=caller_class._id,
            _line=i * 10 + 1,
            _column=5,
            _ent=target_method._id,
            _scope=caller_method._id
        )

    # Find inverse references (who calls target_method)
    inverse_refs = ReferenceModel.select().where(
        (ReferenceModel._ent == target_method._id) &
        (ReferenceModel._kind == call_kind._id)
    )

    # Verify all 3 callers are found
    assert inverse_refs.count() == 3
    caller_ids = [ref._scope._id for ref in inverse_refs]
    for caller in callers:
        assert caller._id in caller_ids


def test_import_reference(temp_db, class_kind, import_kind):
    """Test import references between files/packages."""
    # Create a class that gets imported
    imported_class = EntityModel.create(
        _name="Utils",
        _kind=class_kind._id,
        _longname="com.example.Utils"
    )

    # Create a class that does the importing
    importer = EntityModel.create(
        _name="Main",
        _kind=class_kind._id,
        _longname="com.example.Main"
    )

    # Create import reference
    import_ref = ReferenceModel.create(
        _kind=import_kind._id,
        _file=importer._id,
        _line=1,
        _column=0,
        _ent=imported_class._id,
        _scope=importer._id
    )

    # Verify import reference
    assert import_ref is not None
    assert import_ref._kind._name == "Java Import"
    assert import_ref._ent._name == "Utils"
    assert import_ref._scope._name == "Main"


def test_extend_reference(temp_db, class_kind, extend_kind):
    """Test inheritance (extends) references."""
    # Create parent class
    parent = EntityModel.create(
        _name="Animal",
        _kind=class_kind._id,
        _longname="Animal"
    )

    # Create child class - set parent to the Entity object
    child = EntityModel.create(
        _name="Dog",
        _kind=class_kind._id,
        _longname="Dog",
        _parent=parent  # Pass the Entity object, not the ID
    )

    # Also create explicit extend reference
    extend_ref = ReferenceModel.create(
        _kind=extend_kind._id,
        _file=child._id,
        _line=1,
        _column=0,
        _ent=parent._id,
        _scope=child._id
    )

    # Verify parent-child relationship - compare objects
    assert child._parent == parent

    # Verify extend reference
    assert extend_ref is not None
    assert extend_ref._kind._name == "Java Extend"
    assert extend_ref._ent._name == "Animal"


def test_implement_reference(temp_db, class_kind, interface_kind, implement_kind):
    """Test interface implementation references."""
    # Create interface
    interface = EntityModel.create(
        _name="Drawable",
        _kind=interface_kind._id,
        _longname="Drawable"
    )

    # Create class implementing interface
    circle = EntityModel.create(
        _name="Circle",
        _kind=class_kind._id,
        _longname="Circle",
        _parent=interface  # Pass the Entity object
    )

    # Create implement reference
    implement_ref = ReferenceModel.create(
        _kind=implement_kind._id,
        _file=circle._id,
        _line=1,
        _column=0,
        _ent=interface._id,
        _scope=circle._id
    )

    # Verify parent-child relationship (implementation) - compare objects
    assert circle._parent == interface

    # Verify implement reference
    assert implement_ref is not None
    assert implement_ref._kind._name == "Java Implement"


def test_multiple_references_same_entity(temp_db, class_kind, method_kind, call_kind):
    """Test multiple references to the same entity."""
    # Create target method
    target = EntityModel.create(
        _name="add",
        _kind=method_kind._id,
        _longname="Calculator.add"
    )

    # Create multiple callers calling the same method
    for i in range(5):
        caller_class = EntityModel.create(
            _name=f"Caller{i}",
            _kind=class_kind._id,
            _longname=f"Caller{i}"
        )
        caller_method = EntityModel.create(
            _name=f"call{i}",
            _kind=method_kind._id,
            _longname=f"Caller{i}.call{i}",
            _parent=caller_class
        )

        ReferenceModel.create(
            _kind=call_kind._id,
            _file=caller_class._id,
            _line=i * 5 + 1,
            _column=5,
            _ent=target._id,
            _scope=caller_method._id
        )

    # Count all references to target
    refs_to_target = ReferenceModel.select().where(
        (ReferenceModel._ent == target._id) &
        (ReferenceModel._kind == call_kind._id)
    )
    assert refs_to_target.count() == 5