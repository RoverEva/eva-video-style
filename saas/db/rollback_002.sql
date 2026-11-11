-- Rollback for 002_history.sql: removes the read-only history function (no data involved). The previous API code does not call it.
begin;
drop function if exists public.eva_history(jsonb);
delete from public.eva_schema where version = 2;
commit;
