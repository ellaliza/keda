# Exceptions

Defined in `keda/exceptions.py`. All of them inherit from Python's built-in
`Exception`.

| Exception                     | Raised when                                                         |
|-------------------------------|---------------------------------------------------------------------|
| `InvalidFieldConstraintError` | A field is created with an invalid constraint, such as a `CharDataField` with `max_length` above 255. |
| `InvalidFieldValueError`      | A value given to a field breaks its constraints, such as a string longer than `max_length`. |
| `NoPrimaryKeyError`           | A model has no primary key but declares a field named `id` that is not one. |

```python
from exceptions import InvalidFieldConstraintError

try:
    CharDataField(max_length=500)
except InvalidFieldConstraintError:
    ...
```

Errors from SQLite itself (for example a bad SQL statement passed to
`Database.execute`) are raised as the standard `sqlite3` exceptions.
