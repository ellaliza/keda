# Changelog

All notable changes to Keda are recorded here. The format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

## [Unreleased]

### Added
- Row operations on `DataModel`: `save_object()` (insert or update, tracking
  modified fields and changed primary keys), `delete_object()` and
  `select_objects()` (returns every row as a model instance).
- Model instances: `DataModel` now has its own `__init__` taking field values
  as keyword arguments, and a `__str__` such as `Person(id=1, name=Ana)`.
- `FieldValue`, which holds the per-instance value, old value and modified flag
  of a field.
- `FloatDataField`, `DateDataField` and `DatetimeDataField`.
- `py_representation_type` on every field, and `MetaData.table_name` on models.
- `InvalidFieldError` exception.
- `Database.execute()` accepts named (dict) parameters, and fetched rows are
  returned as dictionaries.

### Changed
- `BoolDataField` is now `BooleanDataField` and its column type is `BOOLEAN`
  instead of `INTEGER`.
- Fields no longer accept an initial `value`; pass values when creating the
  model instance.
- `DataModel` subclasses are no longer turned into dataclasses.
- `Database` no longer keeps a shared `cursor`; each `execute()` returns its
  own.
- Assigning a non-field attribute on a model instance raises
  `InvalidFieldValueError`.

### Known gaps (planned for the next update)
- Proper selection and projection: filtering records and choosing columns.
  `update_objects()` is still a stub.
- Enforcing field value validations (`max_length`, `max_value`, `default`,
  type conversion).

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
