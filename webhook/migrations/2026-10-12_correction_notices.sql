-- Meridian CPD — 12 October 2026
-- Run once in: Supabase Dashboard > SQL Editor. Safe to run more than once.
--
-- Records who has been sent a course correction notice, so nobody can be sent the same
-- notice twice. The admin page at /admin/corrections refuses to send until this exists.
-- Row level security is on with no policies: only the app's service key can read or write.

CREATE TABLE IF NOT EXISTS correction_notices (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  notice_id TEXT NOT NULL,
  member_id UUID NOT NULL REFERENCES members(id),
  course_ids TEXT[] NOT NULL DEFAULT '{}',
  status TEXT NOT NULL DEFAULT 'sending' CHECK (status IN ('sending', 'sent', 'failed')),
  error TEXT,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  sent_at TIMESTAMPTZ,
  UNIQUE (notice_id, member_id)
);

ALTER TABLE correction_notices ENABLE ROW LEVEL SECURITY;
