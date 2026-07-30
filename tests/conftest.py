"""Pytest configuration and fixtures."""

import sys
import os
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

import pytest
import tempfile

from openunderstand.oudb import api
from openunderstand.oudb.models import KindModel, EntityModel


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
    
    # Close database connection
    try:
        if hasattr(db, 'close'):
            db.close()
    except:
        pass
    
    # Cleanup
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


@pytest.fixture
def db_connection(temp_db):
    """Get database connection using api.open."""
    return api.open(temp_db)


@pytest.fixture
def class_kind(temp_db):
    """Get or create Class kind."""
    kind, _ = KindModel.get_or_create(_name="Class", is_ent_kind=True)
    return kind


@pytest.fixture
def method_kind(temp_db):
    """Get or create Method kind."""
    kind, _ = KindModel.get_or_create(_name="Method", is_ent_kind=True)
    return kind


@pytest.fixture
def sample_java_code():
    """Sample Java code snippets for testing."""
    return {
        "simple_class": """
public class Calculator {
    private int result;
    
    public Calculator() {
        this.result = 0;
    }
    
    public int add(int a, int b) {
        return a + b;
    }
    
    public int subtract(int a, int b) {
        return a - b;
    }
}
""",
        "inheritance": """
public class Animal {
    public void eat() { }
}

public class Dog extends Animal {
    public void bark() { }
}
""",
        "interface": """
public interface Drawable {
    void draw();
}

public class Circle implements Drawable {
    public void draw() { }
}
""",
        "nested_class": """
public class Outer {
    public class Inner {
        public void innerMethod() { }
    }
}
"""
    }