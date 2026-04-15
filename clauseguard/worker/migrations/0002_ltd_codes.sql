-- Migration 0002: LTD (Lifetime Deal) code redemption support

-- Table for marketplace codes (PitchGround, SaaSMantra, DealMirror, etc.)
-- Codes are pre-seeded manually before any listing goes live (see docs/ltd-submission-package.md)
CREATE TABLE ltd_codes (
  code          TEXT PRIMARY KEY,
  redeemed_by   TEXT,                -- user_id of the redeemer, NULL until redeemed
  redeemed_at   INTEGER              -- Unix timestamp, NULL until redeemed
);

-- Track whether a user's Pro tier came from Stripe or an LTD code.
-- NULL  = Stripe subscription (default)
-- 'ltd' = lifetime deal code was redeemed
-- This ensures the customer.subscription.deleted webhook never downgrades an LTD user
-- (those users have no stripe_subscription_id, so the WHERE clause won't match anyway,
-- but this column makes the intent explicit and enables proper UI in the extension).
ALTER TABLE users ADD COLUMN pro_source TEXT;
