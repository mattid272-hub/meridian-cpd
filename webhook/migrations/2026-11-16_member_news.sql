-- Member news emails to paying members (webhook/member_news.py). Run once in Supabase → SQL
-- Editor (choose "Run and enable RLS"). Safe to run again. Running it sends nothing: the
-- sender only runs when MEMBER_NEWS is set to dry_run or on, and it defaults to off.

create table if not exists member_news_sends (
  id uuid primary key default gen_random_uuid(),
  member_id uuid not null references members(id),
  email text not null,                          -- the address it went to, for bounce handling
  edition text not null,                        -- for example 2026-11-thank-you
  version text not null default '',             -- A (subscribers) | B (buyers) | '' when held
  status text not null default 'sent',          -- sent | delivered | bounced | complained | failed | held
  resend_id text,
  note text,                                    -- why it failed, or why it was held
  sent_at timestamptz not null default now(),
  unique (member_id, edition)                   -- each edition once per member, ever
);
create index if not exists idx_member_news_sent_at on member_news_sends (sent_at);
create index if not exists idx_member_news_member on member_news_sends (member_id);

alter table member_news_sends enable row level security;
