-- JobGuard D1 schema
-- Run: npx wrangler d1 execute jobguard-db --file=schema.sql

CREATE TABLE IF NOT EXISTS users (
  id TEXT PRIMARY KEY,
  tier TEXT NOT NULL DEFAULT 'free',
  stripe_customer_id TEXT,
  stripe_subscription_id TEXT,
  email TEXT,
  pro_source TEXT,
  created_at TEXT DEFAULT (datetime('now')),
  updated_at TEXT DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS usage_tracking (
  user_id TEXT NOT NULL,
  month TEXT NOT NULL,
  analysis_count INTEGER NOT NULL DEFAULT 0,
  UNIQUE(user_id, month)
);

CREATE TABLE IF NOT EXISTS analyses (
  id TEXT PRIMARY KEY,
  user_id TEXT NOT NULL,
  risk_score INTEGER,
  red_flag_count INTEGER DEFAULT 0,
  platform TEXT,
  summary TEXT,
  created_at TEXT DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS ltd_codes (
  code TEXT PRIMARY KEY,
  redeemed_by TEXT REFERENCES users(id),
  redeemed_at INTEGER
);
