from contextlib import contextmanager
import sqlite3
import importlib.resources
from pathlib import Path

class NovaDB:
    def __init__(self, db='nova.db'):
        self.db_path = Path(__file__).parent / db
        self.ext_path = importlib.resources.files("sqlite_vector.binaries") / "vector"

    @contextmanager
    def _conn(self):
        conn = sqlite3.connect(self.db_path)  # default check_same_thread=True is fine here
        try:
            conn.execute("PRAGMA foreign_keys = ON;")
            conn.execute("PRAGMA busy_timeout = 5000;")  # wait for locks instead of instantly failing
            conn.execute("PRAGMA journal_mode = WAL;")   # better concurrency (one writer, many readers)

            conn.enable_load_extension(True)
            conn.load_extension(str(self.ext_path))
            conn.enable_load_extension(False)

            conn.execute("""
                SELECT vector_init(
                    'memory_items','embedding',
                    'type=FLOAT32,dimension=768,distance=COSINE'
                )
            """)
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

    def execute_sql(self, sql, returns_data=False):
        try:
            data = []
            error = None
    
            with self._conn() as CONN:
                CONN.row_factory = sqlite3.Row
                cursor = CONN.cursor()
                result = cursor.execute(sql)
                if returns_data:
                    rows = result.fetchall()
                    data = [dict(row) for row in rows]
        except Exception as err:
            error = str(err)
        finally:
            return {'data': data, 'error': error}
    