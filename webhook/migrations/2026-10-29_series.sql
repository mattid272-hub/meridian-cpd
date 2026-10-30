-- Series product: one Field Work purchase (£39.99) is recorded as three purchase rows,
-- one per course, all carrying the same Stripe checkout session id.
--
-- RUN THIS IN SUPABASE → SQL EDITOR BEFORE DEPLOYING THE SERIES PRODUCT. The original
-- schema (supabase_migration.sql) declares purchases.stripe_session_id UNIQUE, so with
-- the old constraint in place the second row of a series purchase is refused: the buyer
-- gets one course of three, and Stripe's retries of the event run into the same error.
-- The app's test stubs do not exercise the constraint, so nothing warns of this before
-- the first real sale. Safe to run again.

-- 1. Drop the one-row-per-session constraint, whatever Postgres named it.
do $$
declare
  con record;
begin
  for con in
    select c.conname
    from pg_constraint c
    where c.conrelid = 'public.purchases'::regclass
      and c.contype = 'u'
      and c.conkey = array[(select attnum from pg_attribute
                            where attrelid = 'public.purchases'::regclass
                              and attname = 'stripe_session_id')]
  loop
    execute format('alter table public.purchases drop constraint %I', con.conname);
  end loop;
end $$;

-- 2. One row per course per session: a Stripe redelivery can still never double-record.
create unique index if not exists idx_purchases_session_course
  on public.purchases (stripe_session_id, course_id);

-- 3. Which series a row was bought as part of (null for a single course or subscription).
alter table public.purchases add column if not exists series_id text;

-- 4. When the course email for this row went. The webhook records each part before
--    sending its email and marks it here afterwards, so a Stripe redelivery of the event
--    finishes only the parts that are not yet done and never sends a part twice.
alter table public.purchases add column if not exists emailed_at timestamptz;
