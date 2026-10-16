# Database

Defined in `keda/database_wrapper.py`. A thin wrapper around a single
`sqlite3` connection.

```python
from database_wrapper import Database
```

Models do not take a `Database`: they all use the one created in `models.py`
(`db = Database()`, an in-memory database). Use `Database` directly when you
want to run your own statements.

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

## `execute(statement, params=())`

Runs one SQL statement, fetches all of its rows, commits, and returns the rows
as a list of dictionaries (an empty list for statements that return nothing).

- A trailing `;` is appended to `statement` for you, so leave it off.
- `params` is a tuple of values bound to `?` placeholders, or a dict bound to
  `:name` placeholders (which is what `DataModel` uses). Always pass values this
  way rather than building SQL strings yourself.
- The statement is committed straight away, so every call is its own
  transaction.
- The time the query took is printed to the terminal.
- Any exception raised by `sqlite3` is re-raised unchanged.

```python
db = Database()
db.execute("CREATE TABLE pet (id INTEGER PRIMARY KEY, name TEXT)")
db.execute("INSERT INTO pet (name) VALUES (?)", ("Rex",))
rows = db.execute("SELECT name FROM pet")   # [{'name': 'Rex'}]
db.execute("UPDATE pet SET name = :name WHERE id = :id", {"name": "Max", "id": 1})
```

`execute()` used to return the cursor. Because the rows are fetched before the
commit, statements with `RETURNING` work (SQLite refuses to commit while a
statement still has rows to read).

## `close()`

Closes the connection and prints a message in green. The `Database` object cannot run
statements afterwards.

## Using `Database` in a `with` block

```python
with Database("people.db") as db:
    db.execute("CREATE TABLE IF NOT EXISTS pet (name TEXT)")
```

On leaving the block, any uncommitted work is rolled back, the connection is
closed, and the exception type and value are printed (`None: None` when there
was no error). Exceptions are not suppressed.

Entering the block opens a new connection, on top of the one `Database()`
already opened. The first one is not closed, so it stays open until the program
ends.
