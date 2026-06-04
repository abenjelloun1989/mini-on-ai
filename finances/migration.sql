-- Finances — D1 schema
-- Run once:  wrangler d1 execute finances-db --file=migration.sql
-- (add --remote to apply to the deployed DB; omit for local --local dev DB)

CREATE TABLE IF NOT EXISTS budget_lines (
  id            TEXT PRIMARY KEY DEFAULT (lower(hex(randomblob(16)))),
  name          TEXT NOT NULL,
  monthly_limit REAL NOT NULL,
  color         TEXT NOT NULL DEFAULT '#3498db',
  emoji         TEXT,
  is_active     INTEGER NOT NULL DEFAULT 1,
  sort_order    INTEGER NOT NULL DEFAULT 0,
  created_at    TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS transactions (
  id             TEXT PRIMARY KEY DEFAULT (lower(hex(randomblob(16)))),
  date           TEXT NOT NULL,
  label          TEXT NOT NULL,
  amount         REAL NOT NULL,  -- negative = expense, positive = income
  budget_line_id TEXT REFERENCES budget_lines(id) ON DELETE SET NULL,
  notes          TEXT,
  created_at     TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE INDEX IF NOT EXISTS idx_tx_date   ON transactions(date);
CREATE INDEX IF NOT EXISTS idx_tx_budget ON transactions(budget_line_id);

CREATE TABLE IF NOT EXISTS config (
  id         INTEGER PRIMARY KEY DEFAULT 1,
  data       TEXT NOT NULL DEFAULT '{}',
  updated_at TEXT NOT NULL DEFAULT (datetime('now'))
);

-- config.data JSON structure:
-- {
--   "monthly_income": 0,        total recurring net income / month
--   "budget_note": "",           free text for personal context
--   "cash": 0,                   liquid cash available now
--   "savings_invested": 0,       invested savings (do not break)
--   "savings_pending": 0,        savings becoming liquid on a future date
--   "savings_pending_date": "",  ISO date e.g. "2026-09-01"
--   "minimum_reserve": 0,        floor to always protect
--   "one_time_events": [         future cash injections or big expenses
--     { "date": "", "label": "", "amount": 0 }
--   ]
-- }

CREATE TABLE IF NOT EXISTS chat_messages (
  id         TEXT PRIMARY KEY DEFAULT (lower(hex(randomblob(16)))),
  role       TEXT NOT NULL CHECK(role IN ('user','assistant')),
  content    TEXT NOT NULL,
  created_at TEXT NOT NULL DEFAULT (datetime('now'))
);

INSERT OR IGNORE INTO config (id, data) VALUES (1, '{}');

-- Optional starter budget lines (uncomment to seed):
-- INSERT INTO budget_lines (name, monthly_limit, color, emoji, sort_order) VALUES
--   ('Vie courante', 600, '#3498db', '🛒', 0),
--   ('Restaurants',  200, '#e74c3c', '🍽️', 1),
--   ('Transport',    120, '#f39c12', '🚗', 2),
--   ('Loisirs',      150, '#9b59b6', '🎮', 3),
--   ('Logement',     900, '#27ae60', '🏠', 4),
--   ('Santé',        80,  '#1F3864', '💊', 5);
