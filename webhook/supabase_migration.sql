-- Meridian CPD — Supabase Schema
-- Run this in: Supabase Dashboard → SQL Editor → New Query → Run
-- Project: cpkyloywjmpesmjgqaxm.supabase.co

-- ── Members ──────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS members (
  id                     UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  email                  TEXT UNIQUE NOT NULL,
  name                   TEXT,
  plan                   TEXT CHECK (plan IN ('single', 'subscription')),
  courses_purchased      TEXT[] DEFAULT '{}',
  joined_at              TIMESTAMPTZ DEFAULT NOW(),
  subscription_expires_at TIMESTAMPTZ,
  stripe_customer_id     TEXT
);

-- ── Purchases ─────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS purchases (
  id               UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  member_id        UUID REFERENCES members(id),
  course_id        TEXT,
  stripe_session_id TEXT UNIQUE,
  amount_gbp       NUMERIC(10,2),
  purchased_at     TIMESTAMPTZ DEFAULT NOW()
);

-- ── Completions ───────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS completions (
  id               UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  member_id        UUID REFERENCES members(id),
  course_id        TEXT NOT NULL,
  completed_at     TIMESTAMPTZ,          -- NULL until confirmed by member
  completion_token TEXT UNIQUE NOT NULL  -- single-use link token
);

-- ── Certificates ──────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS certificates (
  id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  cert_number     TEXT UNIQUE NOT NULL,  -- MER-2026-0001
  member_id       UUID REFERENCES members(id),
  course_id       TEXT NOT NULL,
  course_title    TEXT NOT NULL,
  cpd_hours       NUMERIC(4,1) NOT NULL,
  issued_at       TIMESTAMPTZ DEFAULT NOW(),
  issued_for_month TEXT                  -- e.g. '2026-03'
);

-- ── Indexes ───────────────────────────────────────────────────────────────────
CREATE INDEX IF NOT EXISTS idx_members_email        ON members(email);
CREATE INDEX IF NOT EXISTS idx_purchases_member     ON purchases(member_id);
CREATE INDEX IF NOT EXISTS idx_completions_token    ON completions(completion_token);
CREATE INDEX IF NOT EXISTS idx_completions_member   ON completions(member_id);
CREATE INDEX IF NOT EXISTS idx_certificates_number  ON certificates(cert_number);
CREATE INDEX IF NOT EXISTS idx_certificates_member  ON certificates(member_id);

-- ── Row Level Security ────────────────────────────────────────────────────────
-- The webhook uses the service role key (bypasses RLS).
-- RLS is enabled but policies only needed when member dashboard is built.
ALTER TABLE members      ENABLE ROW LEVEL SECURITY;
ALTER TABLE purchases    ENABLE ROW LEVEL SECURITY;
ALTER TABLE completions  ENABLE ROW LEVEL SECURITY;
ALTER TABLE certificates ENABLE ROW LEVEL SECURITY;

-- Service role bypass (already implicit — this documents intent)
-- When dashboard is built, add: CREATE POLICY "member sees own data" ON members
-- FOR SELECT USING (auth.uid()::text = id::text);
