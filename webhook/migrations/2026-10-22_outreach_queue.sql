-- Outreach from the app (webhook/outreach.py): the queue, the run log, and the first
-- campaign. Run once in Supabase → SQL Editor. Safe to run again: nothing is duplicated.
--
-- The campaign is created PAUSED (status app_paused). Resume it from Admin → Outreach.
-- Never set an outreach_campaigns row to 'active': that word belongs to the old Node
-- service (still deployed, idle), which would start sending its own emails to everyone.

create table if not exists outreach_queue (
  id uuid primary key default gen_random_uuid(),
  campaign_id uuid not null references outreach_campaigns(id),
  contact_id uuid not null references outreach_contacts(id),
  position integer not null default 0,          -- send order; domains interleaved
  status text not null default 'queued',        -- queued | sent | skipped | failed
  note text,                                    -- why skipped or failed
  queued_at timestamptz default now(),
  sent_at timestamptz,
  unique (campaign_id, contact_id)              -- one email per contact per campaign, ever
);
create index if not exists idx_outreach_queue_pick on outreach_queue (campaign_id, status, position);

create table if not exists outreach_runs (
  id uuid primary key default gen_random_uuid(),
  campaign_id uuid references outreach_campaigns(id),
  trigger text,                                 -- scheduler | admin | test
  started_at timestamptz default now(),
  finished_at timestamptz,
  sent integer default 0,
  skipped integer default 0,
  failed integer default 0,
  bounced integer default 0,
  complained integer default 0,
  note text
);

-- Wave 1: contacts whose email domain belongs to a company, public body or organisation
-- (outreach_domain_check), not suppressed, not members, and not among those the June
-- campaign emailed more than three times (they get a separate note from Matt first).
insert into outreach_campaigns (name, product, status, target_assessor_types, from_email, from_name)
select 'Corporate wave 1: scheme CPD rules (Oct 2026)', 'meridian', 'app_paused',
       array['DEA','RA','RC','NDEA'], 'hello@meridiancpd.co.uk', 'Matt Davies, Meridian CPD'
where not exists (select 1 from outreach_campaigns where name = 'Corporate wave 1: scheme CPD rules (Oct 2026)');

with campaign as (
  select id from outreach_campaigns where name = 'Corporate wave 1: scheme CPD rules (Oct 2026)'
),
eligible as (
  select c.id as contact_id, lower(split_part(c.email, '@', 2)) as domain
  from outreach_contacts c
  join outreach_domain_check d on d.domain = lower(split_part(c.email, '@', 2))
  where d.decision like '%ok to email'
    and not c.suppressed
    and c.email ~* '^[^@\s]+@[^@\s]+\.[a-z]{2,}$'
    and not exists (select 1 from outreach_suppressed x where lower(x.email) = lower(c.email))
    and not exists (select 1 from members m where lower(m.email) = lower(c.email))
    and (select count(*) from outreach_sends s where s.contact_id = c.id) < 4
),
ranked as (
  -- spread contacts who share a domain across different days
  select contact_id, row_number() over (partition by domain order by random()) as nth_on_domain
  from eligible
),
ordered as (
  select contact_id, row_number() over (order by nth_on_domain, random()) as position
  from ranked
)
insert into outreach_queue (campaign_id, contact_id, position)
select campaign.id, ordered.contact_id, ordered.position
from ordered, campaign
on conflict (campaign_id, contact_id) do nothing;

-- Check: how many are queued?
select status, count(*) from outreach_queue group by status;
