# Keda

A small hobby ORM for SQLite, written in Python from scratch.

Keda lets you describe a table as a Python class, create it in a SQLite
database, and save, load and delete rows as model instances. It is built on top of the standard library's `sqlite3` module and has
no third-party dependencies.

> **Status: early development.** Keda is a learning project and the API will
> change. It is not ready for production use.

## Features (so far)

- A `Database` wrapper around `sqlite3` that times each query, commits it and
  returns the rows as dictionaries. It also works as a context manager.
- Typed field classes: `CharDataField`, `IntDataField`, `BooleanDataField`,
  `FloatDataField`, `DateDataField` and `DatetimeDataField`, with `default`,
  `primary_key`, `unique` and `null` options, plus `max_length`, `max_value`
  and `min_value` where they make sense.
- Field value validation when an instance is created or a field is assigned.
- A `DataModel` base class: declare fields as class attributes, then create
  instances with keyword arguments (`Person(name="Ana")`). Models without a
  primary key get an `id`, and composite primary keys are supported.
- `migrate_model()` to generate and run `CREATE TABLE IF NOT EXISTS` for a model,
  with a `dry_run` mode that only prints the SQL.
- `save_object()` (insert or update) and `delete_object()` to write rows.
- A `manager` on every model with `all()`, `filter()` and `get()`, and lookups
  such as `age__gte=18` or `name__contains="an"`. Queries return a `ResultSet`.

## Requirements

- Python 3.12 or newer (developed on Python 3.14)
- SQLite 3.35 or newer (needed for `RETURNING`), which ships with Python

## Getting started

Keda is not packaged on PyPI yet. Clone the repository and work from inside the
`keda/` folder, since the modules import each other directly (`from fields import ...`).

```bash
git clone https://github.com/ellaliza/keda.git
cd keda/keda
```

Create a model and see the SQL it generates:

```python
from models import DataModel
from fields import IntDataField, CharDataField, BooleanDataField


class Person(DataModel):
    id = IntDataField(primary_key=True)
    name = CharDataField(max_length=200)
    active = BooleanDataField()


Person.migrate_model(dry_run=True)   # only prints the SQL
Person.migrate_model()               # creates the table

ana = Person(name="Ana", active=True)
ana.save_object()                    # INSERT; ana.id is filled in
ana.name = "Ana B"
ana.save_object()                    # UPDATE of the changed fields only

for person in Person.manager.filter(name__contains="Ana"):
    print(person)                    # Person(id= '1', name= 'Ana B', active= 'True')

Person.manager.get(id=1)             # the one match, or Person.DoesNotExist
ana.delete_object()                  # DELETE
```

The dry run prints:

```sql
CREATE TABLE IF NOT EXISTS person
	(id INTEGER  NOT NULL,
	name TEXT  NOT NULL,
	active BOOLEAN  NOT NULL, PRIMARY KEY (id))
```

Models share one in-memory database created in `models.py`, so the data is gone
when the program ends. Fields are `NOT NULL` unless declared with `null=True`,
and a value is required for them when creating an instance.

## Project layout

```
.
├── keda/
│   ├── database_wrapper.py   # Database: sqlite3 connection + execute()
│   ├── fields.py             # Field types and their validation
│   ├── models.py             # DataModel, ModelManager, ResultSet
│   ├── exceptions.py         # Custom exception types
│   ├── colored.py            # ANSI colour helpers for terminal output
│   ├── api.py                # Placeholder for the future public API
│   └── utils.py              # Placeholder for helpers
├── docs/                     # Detailed documentation
├── CHANGELOG.md
├── CONTRIBUTING.md
└── LICENSE
```

## Documentation

- [Database](docs/database.md): connecting to SQLite and running statements
- [Fields](docs/fields.md): field types and their options
- [Models](docs/models.md): defining models, `migrate_model()`, saving and deleting rows, and querying with the manager
- [Exceptions](docs/exceptions.md): the errors Keda raises

## Not implemented yet

- **Chainable result sets**: a `ResultSet` cannot be filtered further, ordered,
  limited or indexed yet, and there is no column selection. This is planned
  for the next update.
- **Relationships** between models (foreign keys and the like), also planned
  for the next update.
- Applying a field's `default`, and reliable conversion of `NULL`, date and
  datetime values to and from the database (see the limitations in
  [Fields](docs/fields.md#known-limitations)).
- Choosing the database a model uses, schema changes to existing tables, and
  transactions beyond committing every statement.

## Contributing

This is a solo hobby project and I'm not accepting code contributions at the
moment. Issues and ideas are welcome. See [CONTRIBUTING.md](CONTRIBUTING.md).

## License

Keda is released under the [MIT License](LICENSE). Anyone is free to use, copy,
modify and distribute it.
