# Models

Defined in `keda/models.py`. A model is a Python class that represents one
database table. Instances of the class represent rows.

```python
from models import DataModel
```

## Defining a model

Subclass `DataModel` and declare each column as a class attribute assigned to a
field:

```python
from models import DataModel
from fields import IntDataField, CharDataField


class Person(DataModel):
    id = IntDataField(primary_key=True)
    name = CharDataField(max_length=200)
```

When the class is created, `DataModel` automatically:

1. fills in the model's `MetaData`,
2. gives every field its name (the attribute name, via `set_field_name`).

Subclasses are **not** dataclasses any more; `DataModel` provides its own
`__init__`. Class attributes that start with `_` are ignored, and so are
methods you add to the model.

## Creating instances

Pass field values as keyword arguments. Fields you leave out start as `None`,
and keywords that are not fields are ignored.

```python
ana = Person(name="Ana")
```

Each field on an instance is backed by a [`FieldValue`](fields.md#fieldvalue)
holding its current value, old value and modified flag.

- **Reading** `ana.name` returns that `FieldValue`. Use `ana.name.value` for the
  raw value; `str(ana.name)` and `print(ana)` show the value too.
- **Writing** `ana.name = "Ana B"` sets the value and marks the field as
  modified. Assigning to something that is not a field (and does not start with
  `_`) raises `InvalidFieldValueError`.

## Primary keys

- Mark a column with `primary_key=True` to make it a primary key.
- If no field is a primary key and the model has no field named `id`,
  `MetaData.use_auto_id` is set to `True`.
- If no field is a primary key **and** a field named `id` exists, a
  `NoPrimaryKeyError` is raised when the class is defined.
- Changing a primary key value on a saved object is allowed: the original value
  is remembered, so the next `save_object()` updates the right row.

## `MetaData`

Each model has a `MetaData` class holding information gathered from its
definition:

| Attribute      | Description                                                       |
|----------------|-------------------------------------------------------------------|
| `model_name`   | The model's class name, e.g. `"Person"`.                          |
| `table_name`   | The table name: the class name in lowercase, e.g. `"person"`.     |
| `class_attrs`  | Dict of non-underscore class attributes, by name.                 |
| `fields`       | List of field names, in declaration order.                        |
| `pk`           | List of the names of primary key fields.                          |
| `use_auto_id`  | `True` when the model has no primary key and no `id` field.       |

```python
Person.MetaData.fields   # ['id', 'name']
Person.MetaData.pk       # ['id']
```

## `migrate_model(db, dry_run=False)`

Class method that creates the model's table.

| Parameter | Description                                                      |
|-----------|------------------------------------------------------------------|
| `db`      | A [`Database`](database.md) to run the statement on.             |
| `dry_run` | When `True`, print the SQL instead of running it.                |

The statement is `CREATE TABLE IF NOT EXISTS <table_name> (...)`, with one
column per field in `MetaData.fields`, so running it twice is safe.

```python
Person.migrate_model(db, dry_run=True)
```

```sql
CREATE TABLE IF NOT EXISTS person
	(id INTEGER PRIMARY KEY ,
	name TEXT  )
```

It only creates tables. It does not alter an existing table if you change the
model.

## `save_object(db)`

Writes the instance to the database and returns the cursor.

- A new object is inserted with every field. If the model has a single primary
  key and you left it unset, the new row's `lastrowid` is stored in it.
- An object that was loaded with `select_objects()` or already saved is updated.
  Only the fields modified since the last save are written, and the row is
  found by its primary key (its previous value if you changed it).

After saving, all fields are marked as unmodified.

```python
ana = Person(name="Ana")
ana.save_object(db)        # INSERT, ana.id is now set
ana.name = "Ana B"
ana.save_object(db)        # UPDATE person SET name = :name WHERE id = :old_id
```

## `delete_object(db)`

Deletes the row matching the instance's primary key and returns the cursor.

## `select_objects(db)`

Class method. Runs `SELECT * FROM <table_name>` and returns a list of model
instances, one per row, already marked as saved so that `save_object()` updates
them. Each column value is converted with the field's `py_representation_type`,
so a `BOOLEAN` column comes back as `True` / `False` rather than `1` / `0`. See
the [known limitations](fields.md#known-limitations) for what this does not
handle yet (`NULL` values and dates).

```python
people = Person.select_objects(db)
```

This is the only way to load records for now. There is no filtering, column
selection, ordering or limiting; those are planned for the next update.

## Not implemented yet

- `update_objects()` exists on `DataModel` but is an empty stub.
- No `WHERE` filtering or projection (see `select_objects()` above).
- Field constraints are not validated on assignment or save; see the
  [known limitations](fields.md#known-limitations).
