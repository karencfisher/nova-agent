from contextlib import contextmanager
import sqlite3
import importlib.resources
from pathlib import Path

class NovaDB:
    def __init__(self, db='nova.db'):
        self.db_path = Path(__file__).parent / db
        self.ext_path = importlib.resources.files("sqlite_vector.binaries") / "vector"

    @contextmanager
    def _conn(self, use_vectors=False):
        conn = sqlite3.connect(self.db_path)  # default check_same_thread=True is fine here
        try:
            conn.execute("PRAGMA foreign_keys = ON;")
            conn.execute("PRAGMA busy_timeout = 5000;")  # wait for locks instead of instantly failing
            conn.execute("PRAGMA journal_mode = WAL;")   # better concurrency (one writer, many readers)

            if use_vectors:
                conn.enable_load_extension(True)
                conn.load_extension(str(self.ext_path))
                conn.enable_load_extension(False)
                conn.execute(
                    "SELECT vector_init('memory_items', 'embedding', 'type=FLOAT32, dimension=384')"
                )

            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

    def execute_sql(self, sql_batch, params=None, returns_data=False, 
                    use_vectors=False):
        if not isinstance(sql_batch, list):
            sql_batch = [(sql_batch, params)]

        data = []
        error = None

        with self._conn(use_vectors=use_vectors) as CONN:
            CONN.row_factory = sqlite3.Row
            cursor = CONN.cursor()

            try:
                for sql, params in sql_batch:
                    if params is None:
                        result = cursor.execute(sql)
                    else:
                        result = cursor.execute(sql, params)
        
            except Exception as err:
                error = str(err)
                CONN.rollback()

            if returns_data:
                if len(sql_batch) > 1:
                    raise ValueError('SELECT statements must be singular')
                rows = result.fetchall()
                data = [dict(row) for row in rows]
        return {'data': data, 'error': error}
    