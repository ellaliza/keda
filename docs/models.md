# Models

Defined in `keda/models.py`. A model is a Python class that represents one
database table.

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

1. applies `@dataclass(kw_only=True)` to the subclass,
2. fills in the model's `MetaData`,
3. gives every field its name (the attribute name, via `set_field_name`).

Class attributes that start with `_` are ignored, and so are methods you add to
the model.

## Primary keys

- Mark a column with `primary_key=True` to make it a primary key.
- If no field is a primary key and the model has no field named `id`,
  `MetaData.use_auto_id` is set to `True`.
- If no field is a primary key **and** a field named `id` exists, a
  `NoPrimaryKeyError` is raised when the class is defined.

## `MetaData`

Each model has a `MetaData` class holding information gathered from its
definition:

| Attribute      | Description                                                       |
|----------------|-------------------------------------------------------------------|
| `model_name`   | The model's class name, e.g. `"Person"`.                          |
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

The statement is `CREATE TABLE IF NOT EXISTS <model name in lowercase> (...)`,
with one column per field in `MetaData.fields`, so running it twice is safe.

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
