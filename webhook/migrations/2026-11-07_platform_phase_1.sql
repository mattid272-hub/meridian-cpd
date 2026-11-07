-- Platform Phase 1 (series pages, My certificates, in-app completion, sign-in from the
-- thank-you page). Run once in Supabase → SQL Editor. Safe to run again.

-- 1. The thank-you page after checkout offers a "Go to My CPD" button that signs the buyer
--    in from the checkout session id, so they never have to open the email first. It works
--    once: the app marks the order's purchase rows here before it signs anyone in, and
--    refuses if the mark is already set or cannot be written.
alter table public.purchases add column if not exists thanks_signin_at timestamptz;

-- 2. One certificate per member per course, enforced by the database as well as the app
--    (the app checks before issuing and marks the completion row conditionally; this is
--    the backstop for two requests landing at the same instant).
--
--    If the table already holds a member with two certificates for one course, the index
--    cannot be created: the block below then lists them as a NOTICE and leaves the table
--    as it is, so the rest of this file still applies. Decide what to do with those rows
--    (nothing is deleted here), then run this file again.
do $$
declare
  dup record;
  n int := 0;
begin
  for dup in
    select member_id, course_id, count(*) as certificates, string_agg(cert_number, ', ' order by cert_number) as numbers
    from public.certificates
    group by member_id, course_id
    having count(*) > 1
  loop
    n := n + 1;
    raise notice 'certificates: member % holds % certificates for % (%)', dup.member_id, dup.certificates, dup.course_id, dup.numbers;
  end loop;
  if n > 0 then
    raise notice 'idx_certificates_member_course NOT created: % member/course pair(s) hold more than one certificate (see above)', n;
  else
    create unique index if not exists idx_certificates_member_course
      on public.certificates (member_id, course_id);
    raise notice 'idx_certificates_member_course is in place';
  end if;
end $$;
