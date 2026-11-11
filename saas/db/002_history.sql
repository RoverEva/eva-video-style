-- EVA Video Studio · read-only purchase/charge history for My Account (GET /api/v2/history).
-- Why: the API read public.ledger directly through PostgREST, but 001 grants the server role (service_role) EXECUTE on
-- the eva_* functions only, never table privileges; on this Supabase project new tables get no automatic grants, so the
-- read failed with 42501 "permission denied for table ledger" (HTTP 403 → API 500). Instead of opening the table, this
-- adds one read-only SECURITY DEFINER function in the same style as 001: the caller passes a user id and gets only that
-- user's rows. No table, column, balance or ledger change; safe to re-run.
create or replace function public.eva_history(p jsonb) returns jsonb language sql stable security definer set search_path = public as $$
  select coalesce(jsonb_agg(to_jsonb(x) order by x.created_at desc, x.id desc), '[]'::jsonb) from (
    select id, kind, ref, credits, free, meta, created_at from ledger
     where user_id = (p->>'user_id')::uuid
     order by created_at desc, id desc
     limit least(greatest(coalesce((p->>'limit')::int, 100), 1), 500)) x;
$$;

do $$ begin
  revoke all on function public.eva_history(jsonb) from public;
  if exists (select 1 from pg_roles where rolname = 'anon') then revoke all on function public.eva_history(jsonb) from anon, authenticated; end if;
  if exists (select 1 from pg_roles where rolname = 'service_role') then grant execute on function public.eva_history(jsonb) to service_role; end if;
end $$;

insert into public.eva_schema(version) values (2) on conflict do nothing;
