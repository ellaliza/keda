# Keda

A small hobby ORM for SQLite, written in Python from scratch.

Keda lets you describe a table as a Python class and create it in a SQLite
database. It is built on top of the standard library's `sqlite3` module and has
no third-party dependencies.

> **Status: early development.** Keda is a learning project and the API will
> change. It is not ready for production use.

## Features (so far)

- A `Database` wrapper around `sqlite3` that times each query and prints the
  result.
- Typed field classes: `CharDataField`, `IntDataField`, `BoolDataField`, with
  `default`, `primary_key` and `unique` options.
- A `DataModel` base class: declare fields as class attributes and Keda collects
  them into the model's metadata.
- `migrate_model()` to generate and run `CREATE TABLE IF NOT EXISTS` for a model,
  with a `dry_run` mode that only prints the SQL.

## Requirements

- Python 3.12 or newer (developed on Python 3.14)
- SQLite, which ships with Python

## Getting started

Keda is not packaged on PyPI yet. Clone the repository and work from inside the
`keda/` folder, since the modules import each other directly (`from fields import ...`).

```bash
git clone https://github.com/ellaliza/keda.git
cd keda/keda
```

Create a model and see the SQL it generates:

```python
from database_wrapper import Database
from models import DataModel
from fields import IntDataField, CharDataField, BoolDataField


class Person(DataModel):
    id = IntDataField(primary_key=True)
    name = CharDataField(max_length=200)
    active = BoolDataField(default=True)


db = Database("people.db")

Person.migrate_model(db, dry_run=True)   # only prints the SQL
Person.migrate_model(db)                 # creates the table

db.close()
```

The dry run prints:

```sql
CREATE TABLE IF NOT EXISTS person
	(id INTEGER PRIMARY KEY ,
	name TEXT  ,
	active INTEGER  )
```

Pass no path (`Database()`) to use an in-memory database.

## Project layout

```
.
├── keda/
│   ├── database_wrapper.py   # Database: sqlite3 connection + execute()
│   ├── fields.py             # CharDataField, IntDataField, BoolDataField
│   ├── models.py             # DataModel base class and migrate_model()
│   ├── exceptions.py         # Custom exception types
│   ├── colored.py            # ANSI colour helpers for terminal output
│   ├── api.py                # Placeholder for the future public API
│   ├── utils.py              # Placeholder for helpers
│   └── tests.py              # Scratch script exercising the library
├── docs/                     # Detailed documentation
├── CHANGELOG.md
├── CONTRIBUTING.md
└── LICENSE
```

## Documentation

- [Database](docs/database.md): connecting to SQLite and running statements
- [Fields](docs/fields.md): field types and their options
- [Models](docs/models.md): defining models, `MetaData` and `migrate_model()`
- [Exceptions](docs/exceptions.md): the errors Keda raises

## Not implemented yet

Keda currently stops at creating tables. Things that do not exist yet include
inserting, querying, updating and deleting records, mapping rows back to model
instances, and field types beyond text, integer and boolean.

## Contributing

This is a solo hobby project and I'm not accepting code contributions at the
moment. Issues and ideas are welcome. See [CONTRIBUTING.md](CONTRIBUTING.md).

## License

Keda is released under the [MIT License](LICENSE). Anyone is free to use, copy,
modify and distribute it.
