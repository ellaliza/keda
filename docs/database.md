# Database

Defined in `keda/database_wrapper.py`. A thin wrapper around a single
`sqlite3` connection.

```python
from database_wrapper import Database
```

## `Database(path=":memory:", echo=True)`

Opens a SQLite connection immediately and prints a confirmation message.
The connection uses a row factory, so every fetched row is a `dict` keyed by
column name instead of a tuple.

| Parameter | Default      | Description                                                      |
|-----------|--------------|------------------------------------------------------------------|
| `path`    | `":memory:"` | Path to the database file. The default is a temporary in-memory database. |
| `echo`    | `True`       | Stored on the instance as `db.echo`.                             |

Attributes:

- `db.path`: the path the database was opened with
- `db.connection`: the underlying `sqlite3.Connection`

There is no shared `db.cursor` any more; each `execute()` call returns its own
cursor.

## `execute(statement, params=())`

Runs one SQL statement and returns the resulting cursor.

- A trailing `;` is appended to `statement` for you, so leave it off.
- `params` is a tuple of values bound to `?` placeholders, or a dict bound to
  `:name` placeholders (which is what `DataModel` uses). Always pass values this
  way rather than building SQL strings yourself.
- The time the query took is printed to the terminal.
- Any exception raised by `sqlite3` is re-raised unchanged.

```python
db = Database()
db.execute("CREATE TABLE pet (id INTEGER PRIMARY KEY, name TEXT)")
db.execute("INSERT INTO pet (name) VALUES (?)", ("Rex",))
rows = db.execute("SELECT name FROM pet").fetchall()   # [{'name': 'Rex'}]
db.execute("UPDATE pet SET name = :name WHERE id = :id", {"name": "Max", "id": 1})
```

## `close()`

Closes the connection and prints a message in green. The `Database` object cannot run
statements afterwards.
