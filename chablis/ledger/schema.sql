-- Chablis shared ledger. One SQLite file, kept in the private repo claude1-data at ledger/ledger.db.
-- Create: sqlite3 ledger/ledger.db < claude1/chablis/ledger/schema.sql   (safe to re-run)
PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS freshness_class (
  class      TEXT PRIMARY KEY,           -- reference | structural | ecosystem | signal | realtime
  ttl_days   REAL NOT NULL,              -- realtime uses fractions of a day
  rationale  TEXT
);
INSERT OR IGNORE INTO freshness_class VALUES
  ('reference', 365, 'legal identifiers, historical filings'),
  ('structural', 90, 'org structure, rosters, catalogs, tool registry entries'),
  ('ecosystem', 30, 'partnerships, affiliations'),
  ('signal', 7, 'pricing, hiring, competitive moves; or event-driven'),
  ('realtime', 0.04, 'market and live feeds; intraday');

CREATE TABLE IF NOT EXISTS source (
  source_id          TEXT PRIMARY KEY,   -- e.g. SRC-0001
  name               TEXT NOT NULL,
  base_url           TEXT,
  access_class       TEXT NOT NULL CHECK (access_class IN ('PUBLIC','CREDENTIALED','LICENSED')),
  auth_ref           TEXT,               -- whose credential and where it lives; never the secret
  license            TEXT,               -- license id and use limits, if LICENSED
  scope              TEXT NOT NULL,      -- what it records; must contain 'Silent on:'
  freshness_class    TEXT NOT NULL REFERENCES freshness_class(class),
  load_mode          TEXT NOT NULL DEFAULT 'append' CHECK (load_mode IN ('append','upsert')),
  robots_checked_at  TEXT,
  CHECK (scope LIKE '%Silent on:%')
);

CREATE TABLE IF NOT EXISTS pull (
  pull_id            TEXT PRIMARY KEY,   -- e.g. PULL-2026-11-18-001
  source_id          TEXT NOT NULL REFERENCES source(source_id),
  project            TEXT NOT NULL,      -- which 1+Claude project asked for it
  started_at         TEXT NOT NULL,
  finished_at        TEXT,
  status             TEXT NOT NULL CHECK (status IN ('running','complete','partial','failed')),
  route              TEXT,               -- route chosen and the two rejected, one line
  authorization_ref  TEXT,               -- required unless the source is PUBLIC
  rows_in            INTEGER DEFAULT 0,
  rows_quarantined   INTEGER DEFAULT 0,
  last_cursor        TEXT,               -- so a run resumes rather than restarts
  missing            TEXT                -- what this pull did NOT get; never left blank on 'partial'
);

CREATE TABLE IF NOT EXISTS deadletter (
  id          INTEGER PRIMARY KEY,
  pull_id     TEXT NOT NULL REFERENCES pull(pull_id),
  payload     TEXT,
  error       TEXT NOT NULL,
  at          TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS quarantine (
  id          INTEGER PRIMARY KEY,
  pull_id     TEXT NOT NULL REFERENCES pull(pull_id),
  payload     TEXT,
  reason      TEXT NOT NULL,
  at          TEXT NOT NULL
);

-- Curated tables are created per dataset and must carry these lineage columns:
--   _source_id TEXT, _pull_id TEXT, _retrieved_at TEXT, _source_class TEXT, _valid_until TEXT, _current INTEGER
-- Mark stale rows (run before any read):
--   UPDATE <table> SET _current = 0 WHERE _current = 1 AND _valid_until < strftime('%Y-%m-%dT%H:%M:%SZ','now');

-- Forward edges: which findings depend on which rows, so a changed fact can invalidate them.
CREATE TABLE IF NOT EXISTS depends_on (
  finding_ref  TEXT NOT NULL,            -- file#anchor or id of the finding / deliverable line
  pull_id      TEXT NOT NULL REFERENCES pull(pull_id),
  row_key      TEXT,                     -- dedup key of the specific row, if narrower than the pull
  recorded_at  TEXT NOT NULL,
  PRIMARY KEY (finding_ref, pull_id, row_key)
);
