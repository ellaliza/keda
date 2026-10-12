# Keda

A small hobby ORM for SQLite, written in Python from scratch.

Keda lets you describe a table as a Python class, create it in a SQLite
database, and save, load and delete rows as model instances. It is built on top of the standard library's `sqlite3` module and has
no third-party dependencies.

> **Status: early development.** Keda is a learning project and the API will
> change. It is not ready for production use.

## Features (so far)

- A `Database` wrapper around `sqlite3` that times each query and prints the
  result. Rows come back as dictionaries.
- Typed field classes: `CharDataField`, `IntDataField`, `BooleanDataField`,
  `FloatDataField`, `DateDataField` and `DatetimeDataField`, with `default`,
  `primary_key` and `unique` options.
- A `DataModel` base class: declare fields as class attributes, then create
  instances with keyword arguments (`Person(name="Ana")`).
- `migrate_model()` to generate and run `CREATE TABLE IF NOT EXISTS` for a model,
  with a `dry_run` mode that only prints the SQL.
- `save_object()` (insert or update), `delete_object()` and `select_objects()`
  to move rows between the database and model instances.

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
from fields import IntDataField, CharDataField, BooleanDataField


class Person(DataModel):
    id = IntDataField(primary_key=True)
    name = CharDataField(max_length=200)
    active = BooleanDataField()


db = Database("people.db")

Person.migrate_model(db, dry_run=True)   # only prints the SQL
Person.migrate_model(db)                 # creates the table

ana = Person(name="Ana", active=True)
ana.save_object(db)                      # INSERT; ana.id is filled in
ana.name = "Ana B"
ana.save_object(db)                      # UPDATE of the changed fields only

for person in Person.select_objects(db): # SELECT * FROM person
    print(person)                        # Person(id=1, name=Ana B, active=True)

ana.delete_object(db)                    # DELETE

db.close()
```

The dry run prints:

```sql
CREATE TABLE IF NOT EXISTS person
	(id INTEGER PRIMARY KEY ,
	name TEXT  ,
	active BOOLEAN  )
```

Pass no path (`Database()`) to use an in-memory database.

## Project layout

```
.
├── keda/
│   ├── database_wrapper.py   # Database: sqlite3 connection + execute()
│   ├── fields.py             # Field types (Char, Int, Boolean, Float, Date, Datetime)
│   ├── models.py             # DataModel: migrations, save/select/delete
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
- [Models](docs/models.md): defining models, `MetaData`, `migrate_model()` and saving, selecting and deleting rows
- [Exceptions](docs/exceptions.md): the errors Keda raises

## Not implemented yet

- **Selection and projection**: `select_objects()` always returns every row
  with every column. There is no filtering (`WHERE`), column selection,
  ordering or limiting yet, and `update_objects()` is an empty stub.
- **Field value validation**: constraints such as `max_length`, `max_value` and
  `default` are stored on the fields but not enforced when values are set or
  saved, and values are not converted to or from the column's type reliably
  (see the limitations in [Fields](docs/fields.md)).
- Schema changes to existing tables, relationships between models, and
  transactions beyond what `sqlite3` does by default.

These are planned for the next update.

## Contributing

This is a solo hobby project and I'm not accepting code contributions at the
moment. Issues and ideas are welcome. See [CONTRIBUTING.md](CONTRIBUTING.md).

## License

Keda is released under the [MIT License](LICENSE). Anyone is free to use, copy,
modify and distribute it.
