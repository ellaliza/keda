# Changelog

All notable changes to Keda are recorded here. The format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

## [Unreleased]

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
