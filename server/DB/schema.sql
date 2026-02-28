PRAGMA foreign_keys = ON;

/* ---------------------------
   Conversations & messages
--------------------------- */
CREATE TABLE IF NOT EXISTS conversations (
  id            INTEGER PRIMARY KEY AUTOINCREMENT,
  title         TEXT,
  created_at    TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ','now')),
  updated_at    TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ','now')),
  deleted       INTEGER NOT NULL DEFAULT 0
);

CREATE TABLE IF NOT EXISTS messages (
  id              INTEGER PRIMARY KEY AUTOINCREMENT,
  conversation_id INTEGER NOT NULL REFERENCES conversations(id) ON DELETE CASCADE,
  role            TEXT NOT NULL CHECK (role IN ('system','user','assistant','tool')),
  content         TEXT NOT NULL,
  created_at      TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ','now')),
  meta_json       TEXT,
  evicted         INTEGER NOT NULL DEFAULT 0
);

CREATE INDEX IF NOT EXISTS idx_messages_convo_time
  ON messages(conversation_id, created_at);


/* ---------------------------
   Contextual memory (vectorized)
--------------------------- */
CREATE TABLE IF NOT EXISTS memory_items (
  id          INTEGER PRIMARY KEY AUTOINCREMENT,
  kind        TEXT NOT NULL DEFAULT 'note',      -- e.g., note|fact|preference|observation|summary
  text        TEXT NOT NULL,
  source      TEXT,                               -- e.g., 'user', 'tool:web', 'system'
  created_at  TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ','now')),
  meta_json   TEXT,

  -- sqlite-vector expects BLOBs for vectors (encoded via vector_as_* helpers). :contentReference[oaicite:1]{index=1}
  embedding   BLOB
);

CREATE INDEX IF NOT EXISTS idx_memory_kind_time
  ON memory_items(kind, created_at);


/* ---------------------------
   Core memory (curated, stable)
--------------------------- */
CREATE TABLE IF NOT EXISTS core_memories (
  id          INTEGER PRIMARY KEY AUTOINCREMENT,
  role        TEXT NOT NULL CHECK (role IN ('user','agent')),
  key         TEXT NOT NULL,
  value       TEXT NOT NULL,
  is_active   INTEGER NOT NULL DEFAULT 1,
  created_at  TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ','now')),
  updated_at  TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ','now'))
);

CREATE UNIQUE INDEX IF NOT EXISTS idx_core_memories_role_key
ON core_memories(role, key);

/* ---------------------------
   Optional: tool/run log (debug flight recorder)
--------------------------- */
CREATE TABLE IF NOT EXISTS tool_runs (
  id              INTEGER PRIMARY KEY AUTOINCREMENT,
  conversation_id INTEGER REFERENCES conversations(id) ON DELETE CASCADE,
  tool_name       TEXT NOT NULL,
  input_json      TEXT,
  output_json     TEXT,
  status          TEXT NOT NULL DEFAULT 'ok',
  started_at      TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ','now')),
  ended_at        TEXT
);