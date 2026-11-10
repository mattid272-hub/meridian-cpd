-- One certificate per member per course, enforced by the database. Run once in Supabase
-- → SQL Editor, AFTER the duplicate MER-DEA-001 pair has been resolved (Phase 1's file
-- skipped this index because that pair exists). Safe to run again.
--
-- This file never deletes or changes a row. If any member still holds two certificates
-- for one course it lists them as a NOTICE and creates nothing; resolve those rows (a
-- decision for Matt) and run it again.
--
-- The app already shows one certificate per course (the earliest) in My certificates, the
-- hours tally and the CPD record, so hours are never counted twice while the index is
-- missing; /verify answers for every number that exists.
do $$
declare
  dup record;
  n int := 0;
begin
  for dup in
    select member_id, course_id, count(*) as certificates,
           string_agg(cert_number || ' (' || to_char(issued_at, 'YYYY-MM-DD HH24:MI') || ')', ', ' order by issued_at) as numbers
    from public.certificates
    group by member_id, course_id
    having count(*) > 1
  loop
    n := n + 1;
    raise notice 'certificates: member % holds % certificates for % : %', dup.member_id, dup.certificates, dup.course_id, dup.numbers;
  end loop;
  if n > 0 then
    raise notice 'idx_certificates_member_course NOT created: % member/course pair(s) still hold more than one certificate', n;
  else
    create unique index if not exists idx_certificates_member_course
      on public.certificates (member_id, course_id);
    raise notice 'idx_certificates_member_course is in place';
  end if;
end $$;

-- Check afterwards (should return one row):
-- select indexname from pg_indexes where tablename = 'certificates' and indexname = 'idx_certificates_member_course';
