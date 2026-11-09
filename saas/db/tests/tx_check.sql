-- Staging check against the REAL Supabase Postgres that leaves NOTHING behind: everything below runs in one transaction
-- that ends in ROLLBACK. Applies 001 twice (idempotency), then asserts the privilege lockdown and the money / library
-- rules with throwaway account ids (accounts do not reference auth.users).
--   psql "$SUPABASE_DB_URL" -v ON_ERROR_STOP=1 -f saas/db/tests/tx_check.sql
\set QUIET on
begin;
\echo 'migration 001: first apply'
\ir ../001_accounts_credits.sql
\echo 'migration 001: second apply (must be idempotent)'
\ir ../001_accounts_credits.sql

create temp table _r (n serial, check_name text, ok boolean, detail text) on commit drop;
create or replace function pg_temp.ok(c boolean, name text, detail text default null) returns void language sql as
  $$ insert into _r(check_name, ok, detail) values (name, coalesce(c, false), detail) $$;

-- ── schema + lockdown ──
select pg_temp.ok((select max(version) from public.eva_schema) = 1, 'schema version 1 recorded once',
                  (select count(*)::text from public.eva_schema));
select pg_temp.ok(bool_and(c.relrowsecurity), 'RLS on for every eva table', string_agg(c.relname, ',')) from pg_class c
  join pg_namespace n on n.oid = c.relnamespace where n.nspname = 'public' and c.relname in ('accounts','projects','versions','reservations','ledger','eva_schema');
select pg_temp.ok(not exists (select 1 from pg_policies where schemaname = 'public' and tablename in ('accounts','projects','versions','reservations','ledger','eva_schema')),
                  'no RLS policies (browser gets nothing)');
select pg_temp.ok(not bool_or(has_table_privilege(r, 'public.' || t, 'select') or has_table_privilege(r, 'public.' || t, 'insert')
                              or has_table_privilege(r, 'public.' || t, 'update') or has_table_privilege(r, 'public.' || t, 'delete')),
                  'anon/authenticated have no table privileges')
  from unnest(array['anon','authenticated']) r, unnest(array['accounts','projects','versions','reservations','ledger','eva_schema']) t
 where exists (select 1 from pg_roles where rolname = r);
select pg_temp.ok(not bool_or(has_function_privilege(r, p.oid, 'execute')), 'anon/authenticated cannot execute any eva_* function',
                  (count(*) / 2)::text || ' functions x 2 roles')
  from pg_proc p join pg_namespace n on n.oid = p.pronamespace, unnest(array['anon','authenticated']) r
 where n.nspname = 'public' and p.proname like 'eva\_%' and exists (select 1 from pg_roles where rolname = r);
select pg_temp.ok(bool_and(has_function_privilege('service_role', p.oid, 'execute')), 'service_role can execute every eva_* function')
  from pg_proc p join pg_namespace n on n.oid = p.pronamespace where n.nspname = 'public' and p.proname like 'eva\_%'
   and exists (select 1 from pg_roles where rolname = 'service_role');

-- ── accounts, 3 lifetime free previews, credits, My Videos (throwaway ids) ──
do $$
declare a uuid := gen_random_uuid(); b uuid := gen_random_uuid(); j jsonb; i int; pid text := 'stg_p_' || substr(md5(random()::text), 1, 8);
begin
  j := public.eva_account(jsonb_build_object('user_id', a, 'email', 'staging-a@example.invalid'));
  perform pg_temp.ok((j->>'free_left')::int = 3 and (j->>'credits')::int = 0, 'new account: 3 free previews, 0 credits', j::text);
  perform public.eva_account(jsonb_build_object('user_id', b, 'email', 'staging-b@example.invalid'));
  perform public.eva_create_project(jsonb_build_object('id', pid, 'user_id', a, 'title', 'staging check', 'upload_key', 'stg/x.mp4',
                                                       'upload_bytes', 1000, 'duration_s', 10, 'source_days', 30));
  -- free preview 1: held → captured
  j := public.eva_start_preview(jsonb_build_object('user_id', a, 'version_id', pid || '_v1', 'project_id', pid, 'cost', 13, 'options', '{}'::jsonb));
  perform pg_temp.ok(j->'charge'->>'type' = 'free', 'preview 1 uses a free preview', j::text);
  j := public.eva_start_preview(jsonb_build_object('user_id', a, 'version_id', pid || '_v1b', 'project_id', pid, 'cost', 13, 'options', '{}'::jsonb));
  perform pg_temp.ok(j->>'reason' = 'busy', 'second preview while one renders is refused', j::text);
  perform public.eva_finish(jsonb_build_object('version_id', pid || '_v1', 'status', 'done', 'retain_days', 30, 'video_key', 'stg/v1.mp4'));
  -- failed preview releases its free slot
  j := public.eva_start_preview(jsonb_build_object('user_id', a, 'version_id', pid || '_v2', 'project_id', pid, 'cost', 13, 'options', '{}'::jsonb));
  perform public.eva_finish(jsonb_build_object('version_id', pid || '_v2', 'status', 'failed', 'error', 'staging'));
  j := public.eva_account(jsonb_build_object('user_id', a));
  perform pg_temp.ok((j->>'free_left')::int = 2 and (j->>'free_used')::int = 1, 'failed preview released its free slot', j::text);
  -- use the remaining two, then the 4th is refused (lifetime, not daily)
  for i in 3..4 loop
    perform public.eva_start_preview(jsonb_build_object('user_id', a, 'version_id', pid || '_v' || i, 'project_id', pid, 'cost', 13, 'options', '{}'::jsonb));
    perform public.eva_finish(jsonb_build_object('version_id', pid || '_v' || i, 'status', 'done', 'retain_days', 30, 'video_key', 'stg/v.mp4'));
  end loop;
  j := public.eva_start_preview(jsonb_build_object('user_id', a, 'version_id', pid || '_v5', 'project_id', pid, 'cost', 13, 'options', '{}'::jsonb));
  perform pg_temp.ok(j->>'reason' = 'insufficient_credits' and (j->>'need')::int = 13, '4th preview refused: lifetime limit reached, 0 credits', j::text);
  -- top-up once per Stripe session (webhook replay ignored)
  j := public.eva_topup(jsonb_build_object('user_id', a, 'credits', 100, 'session_id', 'cs_test_staging_' || pid, 'amount_cents', 999, 'livemode', false));
  perform public.eva_topup(jsonb_build_object('user_id', a, 'credits', 100, 'session_id', 'cs_test_staging_' || pid, 'amount_cents', 999, 'livemode', false));
  j := public.eva_account(jsonb_build_object('user_id', a));
  perform pg_temp.ok((j->>'credits')::int = 100, 'top-up adds 100 credits once (replay ignored)', j::text);
  -- paid preview, then HD export charged once per version
  j := public.eva_start_preview(jsonb_build_object('user_id', a, 'version_id', pid || '_v5', 'project_id', pid, 'cost', 13, 'options', '{}'::jsonb));
  perform pg_temp.ok(j->'charge'->>'type' = 'credits' and (j->'charge'->>'amount')::int = 13, 'preview after the free ones costs credits', j::text);
  perform public.eva_finish(jsonb_build_object('version_id', pid || '_v5', 'status', 'done', 'retain_days', 30, 'video_key', 'stg/v5.mp4'));
  j := public.eva_start_hd(jsonb_build_object('user_id', a, 'version_id', pid || '_hd', 'source_version', pid || '_v5', 'cost', 43));
  perform pg_temp.ok(j->'charge'->>'amount' = '43', 'HD export reserves 43 credits', j::text);
  j := public.eva_start_hd(jsonb_build_object('user_id', a, 'version_id', pid || '_hd2', 'source_version', pid || '_v5', 'cost', 43));
  perform pg_temp.ok(j->>'existing' = pid || '_hd', 'second HD request = same export, no second charge', j::text);
  perform public.eva_finish(jsonb_build_object('version_id', pid || '_hd', 'status', 'done', 'retain_days', 90, 'video_key', 'stg/hd.mp4'));
  j := public.eva_account(jsonb_build_object('user_id', a));
  perform pg_temp.ok((j->>'credits')::int = 44, 'balance 100 - 13 - 43 = 44, never negative', j::text);
  -- My Videos: owner sees 1 project with its versions; another user sees nothing and cannot act on it
  j := public.eva_library(jsonb_build_object('user_id', a));
  perform pg_temp.ok(jsonb_array_length(j) = 1 and jsonb_array_length(j->0->'versions') = 6, 'My Videos: 1 project, 6 versions for the owner',
                     jsonb_array_length(j->0->'versions')::text);
  perform pg_temp.ok(not (j->0->'versions'->0 ? 'user_id'), 'library rows do not expose user ids');
  perform pg_temp.ok(jsonb_array_length(public.eva_library(jsonb_build_object('user_id', b))) = 0, 'other user: empty library');
  perform pg_temp.ok(public.eva_version(jsonb_build_object('version_id', pid || '_v1', 'user_id', b)) is null, 'other user cannot read a version');
  j := public.eva_start_hd(jsonb_build_object('user_id', b, 'version_id', pid || '_hdb', 'source_version', pid || '_v1', 'cost', 43));
  perform pg_temp.ok(j->>'reason' in ('no_source', 'insufficient_credits'), 'other user cannot export the owner''s version', j::text);
  perform public.eva_update_version(jsonb_build_object('version_id', pid || '_v1', 'user_id', a, 'favorite', true));
  perform pg_temp.ok((public.eva_version(jsonb_build_object('version_id', pid || '_v1', 'user_id', a))->>'favorite')::boolean, 'favorite saved');
  j := public.eva_delete(jsonb_build_object('user_id', a, 'version_id', pid || '_v3'));
  perform pg_temp.ok((j->>'ok')::boolean and jsonb_array_length(j->'keys') >= 1, 'delete returns the version''s storage keys', j::text);
  -- retention: expired HD hidden + keys returned
  update public.versions set expires_at = now() - interval '1 day' where id = pid || '_hd';
  j := public.eva_expire('{}'::jsonb);
  perform pg_temp.ok(j->'keys' ? 'stg/hd.mp4', 'retention returns expired files for deletion', j::text);
  -- the constraint itself: credits can never go below zero
  begin
    update public.accounts set credits = -1 where user_id = a;
    perform pg_temp.ok(false, 'negative credits rejected by constraint');
  exception when check_violation then perform pg_temp.ok(true, 'negative credits rejected by constraint');
  end;
end $$;

\set QUIET off
\pset footer off
select n, case when ok then 'PASS' else 'FAIL' end as result, check_name, left(coalesce(detail, ''), 110) as detail from _r order by n;
select count(*) filter (where ok) as passed, count(*) filter (where not ok) as failed from _r;
select (count(*) filter (where not ok) = 0) as all_ok from _r \gset
rollback;
\echo 'ROLLBACK done: nothing was kept'
\if :all_ok
\echo 'TX CHECK: ALL PASS'
\else
\echo 'TX CHECK: FAILURES (see above)'
select 1 / 0;  -- non-zero exit under ON_ERROR_STOP
\endif
