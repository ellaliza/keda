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
| `primary_key` | `False` | Marks the column as `PRIMARY KEY`.                 |
| `unique`      | `False` | Adds a `UNIQUE` constraint to the column.          |

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

### `IntDataField(max_value=None, **options)`

| Parameter   | Description                              |
|-------------|------------------------------------------|
| `max_value` | Optional upper bound, stored on the field as `max_value`. |

### `BooleanDataField(**options)`

Renamed from `BoolDataField`. The column type is now `BOOLEAN` (it was
`INTEGER`). A boolean column can never be a primary key: `primary_key` is always
reset to `False`.

### `FloatDataField(**options)`

Floating point column, stored as `REAL`.

### `DateDataField(**options)` and `DatetimeDataField(**options)`

Date and date-time columns. SQLite has no date type, so both are stored as
`TEXT`.

## Properties and methods

Every field provides:

- `sql_datatype`: the SQLite type name used for the column
- `py_representation_type`: the Python type the column maps to (`str`, `int`,
  `bool`, `float`, `date` or `datetime`)
- `column_sql`: the column definition used in `CREATE TABLE`, for example
  `id INTEGER PRIMARY KEY`
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

These will be addressed with field value validation in the next update:

- `max_length`, `max_value` and `default` are not checked or applied when a
  value is set or saved.
- `py_representation()` is a plain type conversion. An unset `CharDataField`
  is written as the text `"None"`, and `DateDataField` / `DatetimeDataField`
  currently always convert to `None` because `date(...)` and `datetime(...)`
  are called with a single value instead of being parsed.
- The `py_representation(field_value_obj)` methods defined on the date and
  datetime fields are not used by `DataModel`; it calls
  `FieldValue.py_representation()`.
- Values read back from SQLite are not converted: a `BOOLEAN` column comes back
  as `1` / `0`, and dates as text.

## Examples

```python
CharDataField(max_length=200, unique=True)
IntDataField(primary_key=True)
BooleanDataField()
FloatDataField()
```

## Writing a new field type

Subclass the base field class in `fields.py`, call `super().__init__(**kwargs)`,
and implement the three abstract properties `sql_datatype`,
`py_representation_type` and `column_sql`.
