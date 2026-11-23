-- Refer a colleague (webhook/referrals.py). Run once in Supabase → SQL Editor
-- (choose "Run and enable RLS"). Safe to run again. Running it changes nothing a member
-- sees: the scheme stays off until REFERRAL_COUPON_ID is set in Railway.

-- 1. Each member's personal code and the Stripe promotion code behind it, made the first
--    time a subscriber opens My CPD → Refer a colleague.
alter table public.members add column if not exists referral_code text;
alter table public.members add column if not exists referral_promo_id text;
create unique index if not exists idx_members_referral_code on public.members (referral_code)
  where referral_code is not null;
create unique index if not exists idx_members_referral_promo on public.members (referral_promo_id)
  where referral_promo_id is not null;

-- 2. One row per checkout that used a referral code.
--    status: credited | capped | refused_self | refused_existing | refused_duplicate |
--            refused_not_subscription | pending_no_customer | credit_failed | crediting
create table if not exists public.referrals (
  id uuid primary key default gen_random_uuid(),
  referrer_member_id uuid not null references public.members(id),
  referred_member_id uuid references public.members(id),
  stripe_session_id text not null unique,          -- one referral per checkout, ever
  promotion_code_id text,
  code text,
  amount_paid_pence integer,
  status text not null,
  credit_pence integer not null default 0,         -- credit put on the referrer's Stripe balance
  credit_txn_id text,                              -- the Stripe customer balance transaction
  created_at timestamptz not null default now()
);
create index if not exists idx_referrals_referrer on public.referrals (referrer_member_id);
create index if not exists idx_referrals_referred on public.referrals (referred_member_id);
-- A person earns their referrer one credit, once.
create unique index if not exists idx_referrals_one_per_person on public.referrals (referred_member_id)
  where status in ('credited', 'capped');

alter table public.referrals enable row level security;

-- 3. For the Friday review: by week, how many checkouts used a code, how many counted,
--    and the credit given. Read it with: referral_stats?select=*
create or replace view public.referral_stats with (security_invoker = true) as
select
  date_trunc('week', r.created_at at time zone 'Europe/London')::date as week_starting,
  count(*)                                                        as checkouts_with_code,
  count(*) filter (where r.status in ('credited', 'capped'))      as successful,
  count(*) filter (where r.status like 'refused_%')               as refused,
  count(*) filter (where r.status in ('credit_failed', 'pending_no_customer', 'crediting')) as needs_a_look,
  coalesce(sum(r.amount_paid_pence) filter (where r.status in ('credited', 'capped')), 0) / 100.0 as paid_by_newcomers_gbp,
  coalesce(sum(r.credit_pence), 0) / 100.0                        as credit_given_gbp,
  count(distinct r.referrer_member_id)                            as referrers
from public.referrals r
group by 1
order by 1 desc;
