# Models

Defined in `keda/models.py`. A model is a Python class that represents one
database table. Instances of the class represent rows.

```python
from models import DataModel
```

All models share one [`Database`](database.md), created at module level in
`models.py` (`db = Database()`). It is an in-memory database, so its contents
disappear when the program ends, and there is no way yet to point models at a
file.

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

1. fills in the model's `_MetaData`,
2. works out the primary key (see [Primary keys](#primary-keys)),
3. gives every field its name (the attribute name, via `set_field_name`),
4. attaches a [`manager`](#querying) for loading rows.

Subclasses are **not** dataclasses; `DataModel` provides its own `__init__`.
Class attributes that start with `_` are ignored, and so are methods you add to
the model.

## Creating instances

Pass field values as keyword arguments. Keywords that are not fields are
ignored.

```python
ana = Person(name="Ana")
```

Every field is validated when the instance is created (see
[Validation](#validation)). A field you leave out starts as `None`, which is
only accepted when the field was declared with `null=True` or is an
auto-incrementing primary key. Leaving out any other field raises a
`ValueError`.

Each field on an instance is backed by a [`FieldValue`](fields.md#fieldvalue)
holding its current value, old value and modified flag.

- **Reading** `ana.name` returns that `FieldValue`. Use `ana.name.value` for the
  raw value; `str(ana.name)` shows the value too.
- **Writing** `ana.name = "Ana B"` validates the value, sets it and marks the
  field as modified. Assigning to something that is not a field (and does not
  start with `_`) raises `InvalidFieldError`.
- `str(ana)` looks like `Person(id= '1', name= 'Ana')`.

## Validation

Values go through the field's `validate_value()` both when an instance is
created and when a field is assigned. The checks depend on the field type, for
example the type of the value, `max_length`, `max_value` and `min_value`; see
[Fields](fields.md).

- On assignment a failure is raised as `InvalidFieldValueError`.
- On creation the error from the field is raised as it is, so you may see a
  `ValueError` (wrong type, or a required field left out) or an
  `InvalidFieldValueError` (a value that breaks a length or range limit).

## Primary keys

- Mark a column with `primary_key=True` to make it a primary key. More than one
  field can be a primary key; the table then gets a composite key.
- A single `IntDataField` primary key is auto-incrementing by default, so it may
  stay `None` and SQLite assigns the value on insert.
- If no field is a primary key and the model has no field named `id`, an
  `id` `IntDataField` primary key is added for you, after the fields you
  declared, and `MetaData.use_auto_id` is set to `True`.
- If no field is a primary key **and** a field named `id` exists, a
  `NoPrimaryKeyError` is raised when the class is defined.
- Changing a primary key value on a saved object is allowed: the original value
  is remembered, so the next `save_object()` updates the right row.

## `_MetaData`

`MetaData` is a plain class in `models.py`. Each model gets its own instance of
it, stored as `Model._MetaData`, holding information gathered from the
definition:

| Attribute      | Description                                                       |
|----------------|-------------------------------------------------------------------|
| `model_name`   | The model's class name, e.g. `"Person"`.                          |
| `table_name`   | The table name: the class name in lowercase, e.g. `"person"`.     |
| `class_attrs`  | Dict of the model's fields, by name.                              |
| `fields`       | List of field names, in declaration order (an added `id` comes last). |
| `pk`           | List of the names of primary key fields.                          |
| `use_auto_id`  | `True` when Keda added the `id` primary key because the model had none. |

```python
Person._MetaData.fields   # ['id', 'name']
Person._MetaData.pk       # ['id']
```

## `migrate_model(dry_run=False)`

Class method that creates the model's table.

| Parameter | Description                                                      |
|-----------|------------------------------------------------------------------|
| `dry_run` | When `True`, print the SQL instead of running it.                |

The statement is `CREATE TABLE IF NOT EXISTS <table_name> (...)`, with one
column per field in `_MetaData.fields` and the primary key declared as a
table-level `PRIMARY KEY (...)` constraint, so running it twice is safe.

```python
Person.migrate_model(dry_run=True)
```

```sql
CREATE TABLE IF NOT EXISTS person
	(id INTEGER  NOT NULL,
	name TEXT  NOT NULL, PRIMARY KEY (id))
```

It only creates tables. It does not alter an existing table if you change the
model.

## `save_object()`

Writes the instance to the database and returns the instance.

- A new object is inserted with every field (`INSERT ... RETURNING *`). A
  primary key left as `None` is assigned by SQLite.
- An object that was loaded with the manager or already saved is updated
  (`UPDATE ... RETURNING *`). Only the fields modified since the last save are
  written, and the row is found by its primary key (its previous value if you
  changed it).
- The row SQLite returns is written back onto the instance, so values assigned
  by the database, such as a new `id`, are filled in. These are the raw values
  from SQLite, so for example a `BooleanDataField` reads `1` rather than `True`
  until the row is loaded again.

After saving, all fields are marked as unmodified.

```python
ana = Person(name="Ana")
ana.save_object()          # INSERT, ana.id is now set
ana.name = "Ana B"
ana.save_object()          # UPDATE person SET name = :name WHERE id = :old_id
```

`RETURNING` needs SQLite 3.35 or newer.

Current limitations:

- Saving an already saved object with no modified fields fails with an
  `OperationalError` (the `UPDATE` has an empty `SET` list).
- Saving a changed object whose row no longer exists (for example after
  `delete_object()`) fails with an `IndexError`, because the update returns no
  row.

## `delete_object()`

Deletes the row matching the instance's primary key and returns the rows
returned by the statement, which is always an empty list.

## Querying

Every model has a `manager`, a `ModelManager`, for loading rows as model
instances. They come back already marked as saved, so `save_object()` updates
them.

| Method              | Returns                                                         |
|---------------------|-----------------------------------------------------------------|
| `manager.all()`     | A `ResultSet` of every row.                                     |
| `manager.filter(**lookups)` | A `ResultSet` of the rows matching all the lookups.     |
| `manager.get(**lookups)`    | The one matching instance.                              |

```python
Person.manager.all()
Person.manager.filter(name="Ana")
Person.manager.filter(id__gte=20, id__lt=25)
Person.manager.get(id=1)
```

### Lookups

Each keyword is a field name, optionally followed by `__` and an operator.
Several lookups are combined with `AND`. Values are passed to SQLite as bound
parameters.

| Lookup              | SQL                       |
|---------------------|---------------------------|
| `name="Ana"`        | `name = 'Ana'`            |
| `age__gt=18`        | `age > 18`                |
| `age__gte=18`       | `age >= 18`               |
| `age__lt=18`        | `age < 18`                |
| `age__lte=18`       | `age <= 18`               |
| `name__contains="n"`| `name LIKE '%n%'`         |

A keyword that is not a field of the model raises `InvalidFieldError`.
An unknown operator (for example `age__foo`) currently raises an
`AttributeError` instead.

### `get()`

Runs the lookups and returns the single match. It raises `Model.DoesNotExist`
when nothing matches and `MultipleObjectsReturned` when more than one row does.
`DoesNotExist` is one shared exception for all models, so
`Person.DoesNotExist` and `Workplace.DoesNotExist` are the same class.

### `ResultSet`

What `all()` and `filter()` return. It holds the loaded instances and can be
looped over and measured with `len()`:

```python
people = Person.manager.filter(name__contains="Ana")
len(people)
for person in people:
    print(person)
```

| Attribute | Description                                              |
|-----------|----------------------------------------------------------|
| `data`    | The list of model instances.                             |
| `query`   | The SQL that was run.                                    |
| `params`  | The parameters the query was run with.                   |

It cannot be indexed or sliced yet; use `.data` for that. There is no ordering,
limiting or column selection yet.

## Not implemented yet

- Chainable result sets (for example filtering a `ResultSet` further, ordering
  and limiting). These are planned for the next update.
- Relationships between models, also planned.
- Applying a field's `default` value.
- Updating or deleting several rows at once.
- Reliable handling of `NULL`, date and datetime values when saving and loading;
  see the [known limitations](fields.md#known-limitations).
