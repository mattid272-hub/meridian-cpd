-- Briefs for news items (webhook/news.py get_brief). Run once in Supabase → SQL Editor.
-- Safe to run again.
alter table news_items add column if not exists brief text;
alter table news_items add column if not exists brief_kind text;      -- ai | extract | feed | none
alter table news_items add column if not exists brief_at timestamptz;
