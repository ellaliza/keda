# Fields

Defined in `keda/fields.py`. A field describes one column of a model's table.
It is a schema only: the value of a column for a particular row lives in a
[`FieldValue`](#fieldvalue) on the model instance, not on the field.

```python
from fields import (
    CharDataField, IntDataField, BooleanDataField,
    FloatDataField, DateDataField, DatetimeDataField,
)
```

## Options shared by every field

All field types accept these keyword arguments:

| Option        | Default | Description                                        |
|---------------|---------|----------------------------------------------------|
| `default`     | `None`  | Default value for the column. Stored on the field but not applied yet. |
| `primary_key` | `False` | Makes the column part of the table's `PRIMARY KEY`. |
| `unique`      | `False` | Adds a `UNIQUE` constraint to the column.          |
| `null`        | `False` | Allows `NULL` (and `None`) in the column. Without it the column is `NOT NULL` and a value is required. Stored on the field as `allow_null`. |

Fields no longer take an initial `value`. Pass values when you create a model
instance instead (`Person(name="Ana")`, see [Models](models.md)).

## Field types

| Field                | SQLite type | Python type          |
|----------------------|-------------|----------------------|
| `CharDataField`      | `TEXT`      | `str`                |
| `IntDataField`       | `INTEGER`   | `int`                |
| `BooleanDataField`   | `BOOLEAN`   | `bool`               |
| `FloatDataField`     | `REAL`      | `float`              |
| `DateDataField`      | `TEXT`      | `datetime.date`      |
| `DatetimeDataField`  | `TEXT`      | `datetime.datetime`  |

### `CharDataField(max_length=255, **options)`

| Parameter    | Description                                                              |
|--------------|--------------------------------------------------------------------------|
| `max_length` | Maximum length. Must be 255 or less, otherwise `InvalidFieldConstraintError` is raised. |

### `IntDataField(max_value=None, min_value=None, **options)`

| Parameter        | Description                              |
|------------------|------------------------------------------|
| `max_value`      | Optional upper bound. A larger value raises `InvalidFieldValueError`. |
| `min_value`      | Optional lower bound. A smaller value raises `InvalidFieldValueError`. |
| `auto_increment` | Option, not a positional argument. Lets the value stay `None` so SQLite assigns it. A single `IntDataField` primary key gets `auto_increment=True` unless you pass it yourself; with a composite key it is turned off. |

### `BooleanDataField(**options)`

Renamed from `BoolDataField`. The column type is now `BOOLEAN` (it was
`INTEGER`). A boolean column can never be a primary key: `primary_key` is always
reset to `False`.

### `FloatDataField(max_value=None, min_value=None, **options)`

Floating point column, stored as `REAL`. `max_value` and `min_value` are
converted to `float` and enforced like on `IntDataField`; a bound that cannot be
converted raises `ValueError`.

### `DateDataField(**options)` and `DatetimeDataField(**options)`

Date and date-time columns. SQLite has no date type, so both are stored as
`TEXT`.

## Validation

Every field has `allowed_types` and a `validate_value(value)` method. `DataModel`
calls it whenever an instance is created or a field is assigned (see
[Models](models.md#validation)). It returns `True` or raises.

`None` is accepted only when the field has `null=True` (an `IntDataField` with
`auto_increment` also accepts it). Otherwise the value's exact type must be one
of `allowed_types`, or a `ValueError` is raised. Subclasses of these types, such
as a `bool` given to an `IntDataField`, are rejected.

| Field                | `allowed_types`                      | Further checks                                  |
|----------------------|--------------------------------------|-------------------------------------------------|
| `CharDataField`      | `str`                                | length at most `max_length`                     |
| `IntDataField`       | `float`, `int`, `str`                | `min_value` / `max_value`                       |
| `FloatDataField`     | `float`, `int`, `str`                | `min_value` / `max_value`                       |
| `BooleanDataField`   | `bool`, `int`, `float`               | none beyond the type                            |
| `DateDataField`      | `date`, `datetime`, `str`, `int`, `float` | strings must be ISO dates, numbers must be valid timestamps |
| `DatetimeDataField`  | `datetime`, `date`, `str`, `int`, `float` | strings must be ISO date-times, numbers must be valid timestamps |

A value that breaks `max_length`, `min_value` or `max_value` raises
`InvalidFieldValueError`. `default` is still not applied.

## Properties and methods

Every field provides:

- `sql_datatype`: the SQLite type name used for the column
- `py_representation_type`: the Python type the column maps to (`str`, `int`,
  `bool`, `float`, `date` or `datetime`)
- `column_sql`: the column definition used in `CREATE TABLE`, for example
  `name TEXT UNIQUE NOT NULL`. The primary key is declared separately by
  `migrate_model()`, not here.
- `validate_value(value)`: see [Validation](#validation)
- `set_field_name(name)`: sets `field_name`. `DataModel` calls this for you
  with the attribute name, so you rarely need to call it yourself.

## `FieldValue`

`FieldValue(py_representation_type, value=None)` holds the value of one field
on one model instance. Every instance of a model gets its own set, so two rows
never share a value.

| Attribute / method   | Description                                                      |
|----------------------|------------------------------------------------------------------|
| `value`              | The current value.                                               |
| `old_value`          | The value as of the last save or load. Used to find the row when a primary key changes. |
| `_modified`          | `True` when the value changed since the last save; decides which columns an update writes. |
| `py_representation()`| Converts `value` with `py_representation_type`, returning `None` if that raises `TypeError`. This is what gets written to the database. |

`str(field_value)` is `str(field_value.value)`.

## Known limitations

- `default` is not applied when a value is left out.
- `py_representation()` is a plain type conversion. A `None` value becomes the
  text `"None"` in a `CharDataField`, and `DateDataField` /
  `DatetimeDataField` currently always convert to `None` because `date(...)`
  and `datetime(...)` are called with a single value instead of being parsed.
  A date column therefore always saves as `NULL`, which a `NOT NULL` column
  rejects, so give date fields `null=True` until this is fixed.
- Rows loaded by the manager are converted with `py_representation_type`
  (for example `bool(1)` gives `True`). The same plain conversion applies:
  `NULL` in an `INTEGER` or `REAL` column makes `int(None)` / `float(None)`
  raise `TypeError`, `NULL` in a `TEXT` column becomes the string `"None"`, and
  loading a date or datetime column raises `TypeError` because the stored text
  is not parsed.
- `BooleanDataField.validate_value` checks numbers and strings with date
  functions, copied from `DateDataField`, so large integers or floats can be
  rejected and some of its error messages mention dates.
- The `max_value` / `min_value` checks compare the raw value, so a numeric
  string given to an `IntDataField` or `FloatDataField` with a bound raises a
  `TypeError`.

## Examples

```python
CharDataField(max_length=200, unique=True)
IntDataField(primary_key=True)
IntDataField(min_value=0, max_value=150, null=True)
BooleanDataField()
FloatDataField(min_value=0)
```

## Writing a new field type

Subclass the base field class in `fields.py`, call `super().__init__(**kwargs)`,
set `allowed_types`, and implement the abstract properties `sql_datatype`,
`py_representation_type` and `column_sql` and the abstract method
`validate_value`.
