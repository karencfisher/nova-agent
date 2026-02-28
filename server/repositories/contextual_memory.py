import json
import struct
from sentence_transformers import SentenceTransformer

from DB.nova_db import NovaDB


class ContexualMemory:
    dbn = NovaDB()
    embed_fn = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
    DIM = 384

    @staticmethod
    def _make_vec_blob(cls, text):
        emb = cls.embed_fn([text])[0]
        return emb.astype("float32").tobytes()

    @classmethod
    def _ensure_vector_init(cls):
        # safe to call on startup (or lazily); must match your DIM
        cls.dbn.execute_sql(
            "SELECT vector_init('memory_items','embedding', ?);",
            params=(f"type=FLOAT32,dimension={cls.DIM}",),
        )

    @classmethod
    def add_memory(cls, text, kind="note", source=None, meta=None):
        cls._ensure_vector_init()

        blob = cls._make_vec_blob(text)
        meta_json = json.dumps(meta or {}, ensure_ascii=False)

        sql = '''
INSERT INTO memory_items (kind, text, source, meta_json, embedding)
VALUES (?, ?, ?, ?, ?)
'''
        result = cls.dbn.execute_sql(
            sql,
            params=(kind, text, source, meta_json, blob),
            returns_data=False
        )
        return result
        

    @classmethod
    def retrieve_memory(cls, query, k=5, kind=None):
        cls._ensure_vector_init()

        q_blob = cls._make_vec_blob(query)

        where = ""
        params = [q_blob, k]
        if kind is not None:
            where = "WHERE m.kind = ?"
            params.append(kind)

        sql = f'''
SELECT m.id, m.text, m.kind, m.created_at, m.source, m.meta_json, v.distance
FROM memory_items AS m
JOIN vector_scan('memory_items','embedding', ?, ?) AS v
    ON m.id = v.rowid
{where}
ORDER BY v.distance ASC
'''
        result = cls.dbn.execute_sql(
            sql,
            params=tuple(params),
            returns_data=True
        )
        return result
    