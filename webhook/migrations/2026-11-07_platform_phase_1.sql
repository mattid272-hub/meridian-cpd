-- Platform Phase 1 (series pages, My certificates, in-app completion, sign-in from the
-- thank-you page). Run once in Supabase → SQL Editor. Safe to run again.
--
-- The thank-you page after checkout offers a "Go to My CPD" button that signs the buyer
-- in from the checkout session id, so they never have to open the email first. It works
-- once: the app marks the order's purchase rows here before it signs anyone in, and
-- refuses if the mark is already set or cannot be written.
alter table public.purchases add column if not exists thanks_signin_at timestamptz;
