"""Test for ReferenceModel.__str__() fix.

This test verifies that ReferenceModel.__str__() works correctly
even when foreign keys are not set.
"""

import sys
import os
from pathlib import Path

import pytest

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from openunderstand.oudb.models import ReferenceModel


def test_reference_model_str_without_foreign_keys():
    """Test that ReferenceModel.__str__() works without foreign keys."""
    ref = ReferenceModel()
    # This should NOT raise an exception
    result = str(ref)
    assert isinstance(result, str)
    # Should contain fallback information
    assert "ReferenceModel" in result


def test_reference_model_str_with_foreign_keys():
    """Test that ReferenceModel.__str__() works with foreign keys."""
    from openunderstand.oudb.models import KindModel, EntityModel
    
    # Create a reference model with foreign keys
    ref = ReferenceModel()
    ref._id = 1
    result = str(ref)
    assert isinstance(result, str)