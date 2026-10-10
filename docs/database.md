# Database

Defined in `keda/database_wrapper.py`. A thin wrapper around a single
`sqlite3` connection and cursor.

```python
from database_wrapper import Database
```

## `Database(path=":memory:", echo=True)`

Opens a SQLite connection immediately and prints a confirmation message.

| Parameter | Default      | Description                                                      |
|-----------|--------------|------------------------------------------------------------------|
| `path`    | `":memory:"` | Path to the database file. The default is a temporary in-memory database. |
| `echo`    | `True`       | Stored on the instance as `db.echo`.                             |

Attributes:

- `db.path`: the path the database was opened with
- `db.connection`: the underlying `sqlite3.Connection`
- `db.cursor`: the underlying `sqlite3.Cursor`

## `execute(statement, params=())`

Runs one SQL statement and returns the cursor result.

- A trailing `;` is appended to `statement` for you, so leave it off.
- `params` is a tuple of values bound to `?` placeholders. Always pass values
  this way rather than building SQL strings yourself.
- The time the query took is printed to the terminal.
- Any exception raised by `sqlite3` is re-raised unchanged.

```python
db = Database()
db.execute("CREATE TABLE pet (id INTEGER PRIMARY KEY, name TEXT)")
db.execute("INSERT INTO pet (name) VALUES (?)", ("Rex",))
rows = db.execute("SELECT name FROM pet").fetchall()
```

## `close()`

Closes the connection and prints a message. The `Database` object cannot run
statements afterwards.
