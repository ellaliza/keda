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
            cursor = self.connection.cursor()
            result = self.connection.execute(statement + ";", params)
        except Exception as e:
            raise e
        end_time = time.time()
        output = f"Query finished in {end_time - start_time} seconds"
        
        print(f"{Text.cyan_text(output)}")
        return result


        



    


