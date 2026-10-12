# Exceptions

Defined in `keda/exceptions.py`. All of them inherit from Python's built-in
`Exception`.

| Exception                     | Raised when                                                         |
|-------------------------------|---------------------------------------------------------------------|
| `InvalidFieldConstraintError` | A field is created with an invalid constraint, such as a `CharDataField` with `max_length` above 255. |
| `InvalidFieldValueError`      | A model instance is assigned an attribute that is not one of its fields. Intended for values that break a field's constraints too, such as a string longer than `max_length`, once validation is implemented. |
| `NoPrimaryKeyError`           | A model has no primary key but declares a field named `id` that is not one. |
| `InvalidFieldError`           | Defined for references to unknown fields. Nothing raises it yet. |

```python
from exceptions import InvalidFieldConstraintError

try:
    CharDataField(max_length=500)
except InvalidFieldConstraintError:
    ...
```

Errors from SQLite itself (for example a bad SQL statement passed to
`Database.execute`) are raised as the standard `sqlite3` exceptions.
