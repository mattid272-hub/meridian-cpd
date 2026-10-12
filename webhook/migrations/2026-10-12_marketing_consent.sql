-- Meridian CPD — 12 October 2026
-- Run once in: Supabase Dashboard > SQL Editor. Safe to run more than once.
--
-- The "keep me in the loop / no thanks" links in the subscriber welcome email write to
-- members.marketing_consent, but the column was never created, so both links returned
-- a server error. NULL means the subscriber has not answered yet.

ALTER TABLE members ADD COLUMN IF NOT EXISTS marketing_consent BOOLEAN;
