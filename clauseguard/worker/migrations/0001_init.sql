-- ClauseGuard D1 Schema

CREATE TABLE users (
  id TEXT PRIMARY KEY,
  email TEXT,
  tier TEXT NOT NULL DEFAULT 'free',
  stripe_customer_id TEXT,
  stripe_subscription_id TEXT,
  created_at TEXT NOT NULL DEFAULT (datetime('now')),
  updated_at TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE analyses (
  id TEXT PRIMARY KEY,
  user_id TEXT NOT NULL REFERENCES users(id),
  risk_score INTEGER,
  clause_count INTEGER,
  red_flag_count INTEGER,
  contract_type TEXT,
  summary TEXT,
  created_at TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE usage_tracking (
  user_id TEXT NOT NULL REFERENCES users(id),
  month TEXT NOT NULL,
  analysis_count INTEGER NOT NULL DEFAULT 0,
  PRIMARY KEY (user_id, month)
);

CREATE TABLE saved_clauses (
  id TEXT PRIMARY KEY,
  user_id TEXT NOT NULL REFERENCES users(id),
  category TEXT NOT NULL,
  title TEXT NOT NULL,
  clause_text TEXT NOT NULL,
  notes TEXT,
  created_at TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE INDEX idx_analyses_user ON analyses(user_id);
CREATE INDEX idx_usage_user_month ON usage_tracking(user_id, month);
CREATE INDEX idx_clauses_user ON saved_clauses(user_id);
