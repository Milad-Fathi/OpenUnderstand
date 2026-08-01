## Description

The `ReferenceModel.__str__()` method raises a `DoesNotExist` exception when called on a ReferenceModel instance that hasn't had its foreign key fields (`_kind`, `_ent`, `_file`, `_scope`) properly set.

This is problematic because `__str__()` should always return a string representation without raising exceptions.

## Fault Location

**File:** `openunderstand/oudb/models.py`  
**Class:** `ReferenceModel`  
**Method:** `__str__()`


## Reproduction

```python
from openunderstand.oudb.models import ReferenceModel

ref = ReferenceModel()
print(str(ref))
```

## Potential fix:

```python
def __str__(self):
    try:
        return f"{self._kind} {self._ent} {self._file}({self._line}, {self._column})"
    except:
        return f"ReferenceModel(id={self._id})"
```