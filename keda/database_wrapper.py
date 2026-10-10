import sqlite3
import time
from colored import Text

class Database():
    def __init__(self, path=":memory:", echo=True):
        self.path = path
        self.echo = echo
        
        self._create_connection()

    def _create_connection(self):
        self.connection = sqlite3.connect(self.path)
        self.cursor = self.connection.cursor()
        
        print(f"{Text.GREEN}Connection created to {self.path}{Text.RESET}")

    def close(self):
        self.connection.close()
        print(f"Connection closed.")

    def execute(self, statement: str, params: tuple[str] = ()):
        start_time = time.time()
        try:
            result = self.cursor.execute(statement + ";", params)
        except Exception as e:
            raise e
        end_time = time.time()
        output = f"Query finished in {end_time - start_time} seconds"
        
        print(f"{Text.cyan_text(output)}")
        return result

   

        



    


