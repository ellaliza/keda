# Fields

Defined in `keda/fields.py`. A field describes one column of a model's table.

```python
from fields import CharDataField, IntDataField, BoolDataField
```

## Options shared by every field

All field types accept these keyword arguments:

| Option        | Default | Description                                        |
|---------------|---------|----------------------------------------------------|
| `default`     | `None`  | Default value for the column.                      |
| `primary_key` | `False` | Marks the column as `PRIMARY KEY`.                 |
| `unique`      | `False` | Adds a `UNIQUE` constraint to the column.          |

## Field types

### `CharDataField(max_length=255, value=None, **options)`

Text column. Stored as SQLite `TEXT`.

| Parameter    | Description                                                              |
|--------------|--------------------------------------------------------------------------|
| `max_length` | Maximum length. Must be 255 or less, otherwise `InvalidFieldConstraintError` is raised. |
| `value`      | Optional initial value. Raises `InvalidFieldValueError` if longer than `max_length`. |

### `IntDataField(value=None, max_value=None, **options)`

Integer column. Stored as SQLite `INTEGER`.

| Parameter   | Description                              |
|-------------|------------------------------------------|
| `value`     | Optional initial value.                  |
| `max_value` | Optional upper bound, stored on the field as `max_value`. |

### `BoolDataField(value=None, **options)`

Boolean column. Stored as SQLite `INTEGER`.

| Parameter | Description              |
|-----------|--------------------------|
| `value`   | Optional initial value.  |

## Properties and methods

Every field provides:

- `sql_datatype`: the SQLite type name used for the column (`"TEXT"` or `"INTEGER"`)
- `column_sql`: the column definition used in `CREATE TABLE`, for example
  `id INTEGER PRIMARY KEY`
- `set_field_name(name)`: sets `field_name`. `DataModel` calls this for you
  with the attribute name, so you rarely need to call it yourself.

## Examples

```python
CharDataField(max_length=200, unique=True)
IntDataField(primary_key=True)
BoolDataField(default=True)
```

## Writing a new field type

Subclass the base field class in `fields.py`, call `super().__init__(**kwargs)`,
and implement the two abstract properties `sql_datatype` and `column_sql`.
