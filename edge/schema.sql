CREATE TABLE IF NOT EXISTS business (
  slug TEXT PRIMARY KEY,
  record TEXT NOT NULL,
  version INTEGER NOT NULL DEFAULT 1,
  noindex INTEGER NOT NULL DEFAULT 1,
  updated_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS event (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  slug TEXT NOT NULL,
  ts TEXT NOT NULL,
  event TEXT NOT NULL,
  payload TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS event_by_slug ON event (slug, id);

CREATE TABLE IF NOT EXISTS item (
  id TEXT PRIMARY KEY,
  slug TEXT NOT NULL,
  kind TEXT NOT NULL,
  created_at TEXT NOT NULL,
  data TEXT NOT NULL,
  status TEXT NOT NULL DEFAULT 'received',
  reply TEXT,
  replied_at TEXT
);
CREATE INDEX IF NOT EXISTS item_by_slug ON item (slug, created_at);
