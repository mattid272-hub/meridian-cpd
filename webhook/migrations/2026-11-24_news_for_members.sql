-- News and insights on My CPD (webhook/news.py member_items). Adds the per-item switch an
-- admin turns on in Admin -> News ("Show to members"). Off for every item, old and new.
-- Run once in Supabase -> SQL Editor. Safe to run again. Until it is run, members see no
-- news panel and the admin switch says the migration is needed.

alter table news_items add column if not exists member_visible boolean not null default false;
alter table news_items add column if not exists member_approved_at timestamptz;
create index if not exists idx_news_items_members on news_items (published_at desc) where member_visible and not dismissed;
