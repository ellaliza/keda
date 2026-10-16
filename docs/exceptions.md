# Exceptions

Defined in `keda/exceptions.py`. All of them inherit from Python's built-in
`Exception`.

| Exception                     | Raised when                                                         |
|-------------------------------|---------------------------------------------------------------------|
| `InvalidFieldConstraintError` | A field is created with an invalid constraint, such as a `CharDataField` with `max_length` above 255. |
| `InvalidFieldValueError`      | A value breaks a field's constraints, such as a string longer than `max_length` or a number outside `min_value` / `max_value`. Also raised when assigning to a field a value that fails validation for any reason. |
| `NoPrimaryKeyError`           | A model has no primary key but declares a field named `id` that is not one. |
| `InvalidFieldError`           | A name that is not a field of the model is used: assigning a non-field attribute on an instance, or using one in a `filter()` / `get()` lookup. |
| `DoesNotExist`                | `manager.get()` matched no row. Available as `Model.DoesNotExist`, though it is the same class for every model. |
| `MultipleObjectsReturned`     | `manager.get()` matched more than one row.                          |

Field validation can also raise a plain `ValueError`, for example when a value
has the wrong type or a required field is left out when creating an instance
(see [Models](models.md#validation)).

```python
from exceptions import InvalidFieldConstraintError

try:
    CharDataField(max_length=500)
except InvalidFieldConstraintError:
    ...
```

```python
try:
    person = Person.manager.get(id=99)
except Person.DoesNotExist:
    ...
```

Errors from SQLite itself (for example a bad SQL statement passed to
`Database.execute`) are raised as the standard `sqlite3` exceptions.
