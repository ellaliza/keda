import sqlite3
import time
from colored import Text
from sqlite3 import Cursor


def dict_factory(cursor: Cursor, row: tuple):
    fields = [column[0] for column in cursor.description]
    return {key: value for key, value in zip(fields, row)}

class Database():
    def __init__(self, path=":memory:", echo=True):
        self.path = path
        self.echo = echo
        
        self._create_connection()

    def _create_connection(self):
        self.connection = sqlite3.connect(self.path)
        self.connection.row_factory = dict_factory
        
        print(f"{Text.GREEN}Connection created to {self.path}{Text.RESET}")

    def close(self):
        self.connection.close()
        print(f"{Text.GREEN}Connection closed.{Text.RESET}")

    def execute(self, statement: str, params: tuple[str] = ()):
        start_time = time.time()
        try:
            
            result = self.connection.execute(statement + ";", params)
            rows = result.fetchall()
            
            self.connection.commit()
        except Exception as e:
            raise e
        end_time = time.time()
        output = f"Query finished in {end_time - start_time} seconds"
        
        print(f"{Text.cyan_text(output)}")
        return rows

    def __enter__(self):
        self._create_connection()
        return self

    def __exit__(self, exc_type, exc, tb):
        self.connection.rollback()
        self.close()
        print(f"{exc_type}: {exc}")


        



    


