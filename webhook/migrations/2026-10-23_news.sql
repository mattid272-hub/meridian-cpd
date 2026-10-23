-- News and insights for the admin sidebar (webhook/news.py). Run once in Supabase →
-- SQL Editor (choose "Run and enable RLS"). Safe to run again.

create table if not exists news_items (
  id uuid primary key default gen_random_uuid(),
  key text unique not null,              -- the entry's link, or page link + content hash
  source text not null,                  -- display name, e.g. "Elmhurst Energy"
  kind text not null default 'feed',     -- feed | page
  title text not null,
  url text not null,
  published_at timestamptz,
  summary text,
  tags text[] default '{}',
  fetched_at timestamptz default now(),
  read_at timestamptz,
  dismissed boolean not null default false
);
create index if not exists idx_news_items_latest on news_items (dismissed, published_at desc);

create table if not exists news_sources (
  source_id text primary key,            -- matches SOURCES[i]["id"] in news.py
  url text,
  last_checked timestamptz,
  last_ok timestamptz,
  last_error text,
  last_added integer default 0,
  page_hash text,                        -- watched pages only
  page_title text,
  last_item_at timestamptz
);

alter table news_items enable row level security;
alter table news_sources enable row level security;
