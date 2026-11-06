-- Free-course follow-up emails (webhook/followup.py). Run once in Supabase → SQL Editor
-- (choose "Run and enable RLS"). Safe to run again. Running it sends nothing: the sender
-- only runs when FREE_FOLLOWUP is set to dry_run or on, and it defaults to off.

create table if not exists free_course_followup_sends (
  id uuid primary key default gen_random_uuid(),
  member_id uuid not null references members(id),
  email text not null,                          -- the address it went to, for bounce handling
  step text not null,                           -- nudge | next | price | monthly:<edition>
  status text not null default 'sent',          -- sent | delivered | bounced | complained | failed
  resend_id text,
  note text,                                    -- why it failed
  sent_at timestamptz not null default now(),
  unique (member_id, step)                      -- each email once per person, ever
);
create index if not exists idx_followup_sends_sent_at on free_course_followup_sends (sent_at);
create index if not exists idx_followup_sends_member on free_course_followup_sends (member_id);

alter table free_course_followup_sends enable row level security;

-- For the Friday review: by week and email, how many went, bounced or complained, how
-- many of those people unsubscribed afterwards, and how many paid for anything after it
-- (test checkouts excluded). Counts are per email: someone who got two emails and then
-- bought shows under both, so for people rather than emails use Admin → Follow-up.
-- Read it with: free_course_followup_stats?select=*
create or replace view free_course_followup_stats with (security_invoker = true) as
select
  date_trunc('week', s.sent_at at time zone 'Europe/London')::date as week_starting,
  s.step,
  count(*) filter (where s.status <> 'failed')            as sent,
  count(*) filter (where s.status = 'delivered')          as delivered,
  count(*) filter (where s.status = 'bounced')            as bounced,
  count(*) filter (where s.status = 'complained')         as complained,
  count(*) filter (where s.status = 'failed')             as failed,
  count(*) filter (where exists (
    select 1 from outreach_suppressed x
    where lower(x.email) = lower(s.email) and x.reason = 'unsubscribed' and x.suppressed_at > s.sent_at
  ))                                                      as unsubscribed_after,
  count(*) filter (where exists (
    select 1 from purchases p
    where p.member_id = s.member_id and p.amount_gbp > 0 and p.purchased_at > s.sent_at
      and coalesce(p.stripe_session_id, '') not like 'cs_test_%'
  ))                                                      as bought_after,
  coalesce(sum((
    select sum(p.amount_gbp) from purchases p
    where p.member_id = s.member_id and p.amount_gbp > 0 and p.purchased_at > s.sent_at
      and coalesce(p.stripe_session_id, '') not like 'cs_test_%'
  )), 0)                                                  as paid_after_gbp
from free_course_followup_sends s
group by 1, 2
order by 1 desc, 2;
