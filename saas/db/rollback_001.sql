-- Rollback for 001_accounts_credits.sql — ONLY for a release that never took real customer data.
-- Not needed for a normal code rollback: the tables/functions are additive and the previous code ignores them.
-- Run manually in the Supabase SQL editor after exporting public.accounts / public.ledger if any rows exist.
begin;
drop function if exists public.eva_account(jsonb), public.eva_start_preview(jsonb), public.eva_start_hd(jsonb), public.eva_finish(jsonb),
  public.eva_set_running(jsonb), public.eva_set_duration(jsonb), public.eva_topup(jsonb), public.eva_create_project(jsonb), public.eva_library(jsonb),
  public.eva_version(jsonb), public.eva_update_version(jsonb), public.eva_delete(jsonb), public.eva_expire(jsonb), public.eva_stuck(jsonb);
drop table if exists public.reservations, public.ledger, public.versions, public.projects, public.accounts, public.eva_schema;
commit;
