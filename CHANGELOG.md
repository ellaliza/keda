# Changelog

All notable changes to Keda are recorded here. The format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

## [Unreleased]

### Added
- Row operations on `DataModel`: `save_object()` (insert or update, tracking
  modified fields and changed primary keys) and `delete_object()`.
- Querying through a `manager` on every model: `all()`, `filter(**lookups)` and
  `get(**lookups)`. Lookups take a field name, optionally with an operator:
  `__gt`, `__gte`, `__lt`, `__lte` or `__contains`; several are combined with
  `AND`. Queries return a `ResultSet` that supports iteration and `len()`.
- `DoesNotExist` and `MultipleObjectsReturned` exceptions, raised by `get()`.
- `DeletedObjectError`: `delete_object()` now marks the instance as deleted, and
  saving it, assigning to its fields or deleting it again raises this error.
- `get_db_representation()` and `get_py_representation()` on every field.
  Date and date-time fields are written as ISO text and parsed back into
  `date` / `datetime` objects when loaded.
- Field value validation: every field has `allowed_types` and
  `validate_value()`, which run when an instance is created or a field is
  assigned and enforce types, `max_length`, `max_value` and `min_value`.
- Field options: `null` on every field, `min_value` on `IntDataField`,
  `max_value` and `min_value` on `FloatDataField`, and `auto_increment` on
  `IntDataField`.
- Composite primary keys, and an automatic auto-incrementing `id` primary key
  for models that declare none.
- `Database` can be used in a `with` block.
- Model instances: `DataModel` now has its own `__init__` taking field values
  as keyword arguments, and a `__str__` such as `Person(id= '1', name= 'Ana')`.
- `FieldValue`, which holds the per-instance value, old value and modified flag
  of a field.
- `FloatDataField`, `DateDataField` and `DatetimeDataField`.
- `py_representation_type` on every field, and `MetaData.table_name` on models.
- `InvalidFieldError` exception.
- `Database.execute()` accepts named (dict) parameters, and fetched rows are
  returned as dictionaries.

### Changed
- Models use one shared `Database`, created in `models.py`. `migrate_model()`,
  `save_object()` and `delete_object()` no longer take a `db` argument.
- `Database.execute()` fetches all rows, commits, and returns them as a list of
  dictionaries instead of returning the cursor.
- `save_object()` uses `INSERT`/`UPDATE ... RETURNING *` and writes the stored
  row back onto the instance, so database-assigned values such as a new `id`
  are filled in. This needs SQLite 3.35 or newer.
- Columns are `NOT NULL` unless the field has `null=True`, and the primary key
  is declared as a table-level `PRIMARY KEY (...)` constraint instead of on the
  column. A field left out when creating an instance now raises `ValueError`
  unless it accepts `None`.
- `MetaData` is now a module-level class and each model holds its own instance
  as `_MetaData`.
- `BoolDataField` is now `BooleanDataField` and its column type is `BOOLEAN`
  instead of `INTEGER`.
- Fields no longer accept an initial `value`; pass values when creating the
  model instance.
- `DataModel` subclasses are no longer turned into dataclasses.
- `Database` no longer keeps a shared `cursor`.
- Loaded rows are converted with each field's `py_representation_type`.
- Assigning a non-field attribute on a model instance raises
  `InvalidFieldError`; a value that fails validation raises
  `InvalidFieldValueError`.
- `save_object()` on a saved object with no modified fields now does nothing
  instead of failing, and `delete_object()` returns `None`.
- `min_value` / `max_value` are converted to `int` / `float` and compared
  against the converted value, so numeric strings work. `FloatDataField` raises
  `TypeError` instead of `ValueError` for a value of the wrong type.
- `BooleanDataField` validation no longer uses date functions.
- `save_object()` prints the SQL statement and its parameters.

### Removed
- `select_objects(db)`, replaced by `manager.all()` and `manager.filter()`.
- The empty `update_objects()` stub.

### Known gaps
- Chainable result sets: filtering, ordering, limiting and indexing a
  `ResultSet`, and choosing columns. Planned for the next update, along with
  the start of relationships between models.
- `default` is not applied, and `NULL` is not loaded reliably from text,
  integer, float and boolean columns.
- After `save_object()` the instance holds the raw values SQLite returned (for
  example `1` for a boolean, ISO text for a date) until it is loaded again.
- Saving a changed object whose row was deleted through another instance raises
  an `IndexError`.
- `Database.__enter__` opens a second connection and leaves the first open.
- Models cannot be pointed at a database file; they always use an in-memory
  database.

## [0.1.0-dev] - 2026-10-10

Initial development snapshot.

### Added
- `Database` wrapper around `sqlite3` with timed query execution.
- Field types: `CharDataField`, `IntDataField`, `BoolDataField`, with the
  shared `default`, `primary_key` and `unique` options.
- `DataModel` base class: subclasses are turned into keyword-only dataclasses,
  collect their fields into `MetaData`, and can create their table with
  `migrate_model()` (including a `dry_run` mode that prints the SQL).
- Custom exceptions: `InvalidFieldConstraintError`, `InvalidFieldValueError`,
  `NoPrimaryKeyError`.
- Coloured terminal output helper (`colored.Text`).
