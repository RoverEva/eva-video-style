-- EVA Video Studio · accounts, lifetime free previews, credits, My Videos (Supabase Postgres)
-- Applied by CI (saas/db/migrate.py) inside one transaction; safe to re-run (idempotent DDL, version table).
--
-- Security model: the browser never talks to these tables. RLS is ON with NO policies, and every privilege is revoked
-- from anon/authenticated; only the server (service_role key, held in Modal Secrets) calls the functions below.
-- Every function takes one jsonb argument `p` and returns jsonb (PostgREST: POST /rest/v1/rpc/<fn> {"p": {...}}).
--
-- Money rules (all atomic, account row locked FOR UPDATE, so concurrent requests queue and cannot overspend):
--   * 3 free previews per account for life (free_limit). A preview first reserves a free slot (free_held), or credits
--     when none are left; success captures it, failure / cancel / critical QA failure releases it (nothing consumed).
--   * HD export reserves credits up front; released on failure.
--   * Stripe top-ups are recorded once per Checkout Session id (unique ledger ref), so a replayed webhook adds nothing.

create table if not exists public.eva_schema (version int primary key, applied_at timestamptz default now());

create table if not exists public.accounts (
  user_id      uuid primary key,
  email        text,
  created_at   timestamptz not null default now(),
  free_limit   int not null default 3,
  free_used    int not null default 0,
  free_held    int not null default 0,
  credits      int not null default 0,
  constraint credits_nonneg check (credits >= 0),
  constraint free_nonneg check (free_used >= 0 and free_held >= 0),
  constraint free_cap check (free_used + free_held <= free_limit)
);

create table if not exists public.projects (
  id           text primary key,
  user_id      uuid not null references public.accounts(user_id),
  created_at   timestamptz not null default now(),
  title        text not null,
  upload_key   text,                               -- null once the source upload has expired
  upload_bytes bigint,
  duration_s   numeric,
  source_expires_at timestamptz,
  deleted_at   timestamptz
);
create index if not exists projects_user on public.projects(user_id, created_at desc);
alter table public.projects alter column upload_key drop not null;

create table if not exists public.versions (
  id           text primary key,
  project_id   text not null references public.projects(id),
  user_id      uuid not null references public.accounts(user_id),
  kind         text not null check (kind in ('preview', 'hd')),
  n            int not null,                       -- version number within the project (previews); hd = n of its source
  source_version text references public.versions(id),  -- hd: the preview whose saved configuration it exports
  options      jsonb not null,
  status       text not null default 'queued' check (status in ('queued','running','done','failed','qa_failed','canceled')),
  charge       jsonb,                              -- {"type": "free"|"credits", "amount": n}
  video_key    text, thumb_key text, plan_key text, qa_key text,
  qa           jsonb, report jsonb, cost jsonb,
  favorite     boolean not null default false,
  error        text,
  created_at   timestamptz not null default now(),
  finished_at  timestamptz,
  expires_at   timestamptz,
  deleted_at   timestamptz
);
create index if not exists versions_project on public.versions(project_id, created_at);
create index if not exists versions_expiry on public.versions(expires_at) where deleted_at is null;
create unique index if not exists versions_one_hd on public.versions(source_version) where kind = 'hd' and status not in ('failed','qa_failed','canceled') and deleted_at is null;

create table if not exists public.reservations (
  version_id   text primary key references public.versions(id),
  user_id      uuid not null references public.accounts(user_id),
  kind         text not null check (kind in ('free','credits')),
  amount       int not null,
  state        text not null default 'held' check (state in ('held','captured','released')),
  reason       text,
  created_at   timestamptz not null default now(),
  settled_at   timestamptz
);

create table if not exists public.ledger (
  id           bigserial primary key,
  user_id      uuid not null references public.accounts(user_id),
  kind         text not null,          -- topup | reserve | capture | release | adjust
  ref          text not null,          -- stripe session id / version id
  credits      int not null default 0, -- change to the credit balance
  free         int not null default 0, -- change to free previews used (+1 on capture)
  meta         jsonb,
  created_at   timestamptz not null default now(),
  unique (kind, ref)
);
create index if not exists ledger_user on public.ledger(user_id, created_at desc);

-- lock everything down: no browser access at all
alter table public.accounts enable row level security;
alter table public.projects enable row level security;
alter table public.versions enable row level security;
alter table public.reservations enable row level security;
alter table public.ledger enable row level security;
alter table public.eva_schema enable row level security;
do $$ begin
  if exists (select 1 from pg_roles where rolname = 'anon') then
    execute 'revoke all on public.accounts, public.projects, public.versions, public.reservations, public.ledger, public.eva_schema from anon, authenticated';
  end if;
end $$;

-- ───────────────────────────── functions ─────────────────────────────
create or replace function public.eva_account(p jsonb) returns jsonb language plpgsql security definer set search_path = public as $$
declare a accounts;
begin
  insert into accounts(user_id, email) values ((p->>'user_id')::uuid, p->>'email')
    on conflict (user_id) do update set email = coalesce(excluded.email, accounts.email)
    returning * into a;
  return jsonb_build_object('user_id', a.user_id, 'email', a.email, 'credits', a.credits, 'free_left', a.free_limit - a.free_used - a.free_held,
                            'free_used', a.free_used, 'free_held', a.free_held, 'free_limit', a.free_limit);
end $$;

-- new preview version + its reservation, atomically. Free slot first, then credits.
create or replace function public.eva_start_preview(p jsonb) returns jsonb language plpgsql security definer set search_path = public as $$
declare a accounts; uid uuid := (p->>'user_id')::uuid; vid text := p->>'version_id'; pid text := p->>'project_id';
        cost int := (p->>'cost')::int; nn int; r reservations; ckind text;
begin
  select * into r from reservations where version_id = vid;
  if found then return jsonb_build_object('ok', true, 'duplicate', true, 'charge', jsonb_build_object('type', r.kind, 'amount', r.amount)); end if;
  select * into a from accounts where user_id = uid for update;                 -- serialises concurrent requests
  if not found then return jsonb_build_object('ok', false, 'reason', 'no_account'); end if;
  if not exists (select 1 from projects where id = pid and user_id = uid and deleted_at is null) then
    return jsonb_build_object('ok', false, 'reason', 'no_project'); end if;
  if exists (select 1 from versions where project_id = pid and kind = 'preview' and status in ('queued','running')) then
    return jsonb_build_object('ok', false, 'reason', 'busy'); end if;            -- one preview at a time per project
  if a.free_used + a.free_held < a.free_limit then ckind := 'free';
    update accounts set free_held = free_held + 1 where user_id = uid;
  elsif a.credits >= cost then ckind := 'credits';
    update accounts set credits = credits - cost where user_id = uid;
  else return jsonb_build_object('ok', false, 'reason', 'insufficient_credits', 'need', cost, 'have', a.credits); end if;
  select coalesce(max(n), 0) + 1 into nn from versions where project_id = pid and kind = 'preview';
  insert into versions(id, project_id, user_id, kind, n, options, charge)
    values (vid, pid, uid, 'preview', nn, p->'options', jsonb_build_object('type', ckind, 'amount', case when ckind = 'free' then 0 else cost end));
  insert into reservations(version_id, user_id, kind, amount) values (vid, uid, ckind, case when ckind = 'free' then 1 else cost end);
  insert into ledger(user_id, kind, ref, credits, meta) values (uid, 'reserve', vid, case when ckind = 'free' then 0 else -cost end, jsonb_build_object('for', 'preview', 'type', ckind));
  return jsonb_build_object('ok', true, 'n', nn, 'charge', jsonb_build_object('type', ckind, 'amount', case when ckind = 'free' then 0 else cost end));
end $$;

-- HD export of a saved preview version: credits reserved up front; one live HD per source version
create or replace function public.eva_start_hd(p jsonb) returns jsonb language plpgsql security definer set search_path = public as $$
declare a accounts; uid uuid := (p->>'user_id')::uuid; vid text := p->>'version_id'; src versions; cost int := (p->>'cost')::int; ex versions; r reservations;
begin
  select * into r from reservations where version_id = vid;
  if found then return jsonb_build_object('ok', true, 'duplicate', true); end if;
  select * into a from accounts where user_id = uid for update;
  if not found then return jsonb_build_object('ok', false, 'reason', 'no_account'); end if;
  select * into src from versions where id = p->>'source_version' and user_id = uid and kind = 'preview' and status = 'done' and deleted_at is null;
  if not found then return jsonb_build_object('ok', false, 'reason', 'no_source'); end if;
  if not exists (select 1 from projects where id = src.project_id and upload_key is not null and deleted_at is null) then
    return jsonb_build_object('ok', false, 'reason', 'source_expired'); end if;     -- HD is rendered from the original upload
  select * into ex from versions where source_version = src.id and kind = 'hd' and status not in ('failed','qa_failed','canceled') and deleted_at is null;
  if found then return jsonb_build_object('ok', true, 'existing', ex.id, 'status', ex.status); end if;   -- already bought: free replay/download
  if a.credits < cost then return jsonb_build_object('ok', false, 'reason', 'insufficient_credits', 'need', cost, 'have', a.credits); end if;
  update accounts set credits = credits - cost where user_id = uid;
  insert into versions(id, project_id, user_id, kind, n, source_version, options, charge)
    values (vid, src.project_id, uid, 'hd', src.n, src.id, src.options, jsonb_build_object('type', 'credits', 'amount', cost));
  insert into reservations(version_id, user_id, kind, amount) values (vid, uid, 'credits', cost);
  insert into ledger(user_id, kind, ref, credits, meta) values (uid, 'reserve', vid, -cost, jsonb_build_object('for', 'hd', 'source', src.id));
  return jsonb_build_object('ok', true, 'charge', jsonb_build_object('type', 'credits', 'amount', cost));
end $$;

-- finish a version: capture its reservation on success, release it on failure / cancel / critical QA failure
create or replace function public.eva_finish(p jsonb) returns jsonb language plpgsql security definer set search_path = public as $$
declare r reservations; vid text := p->>'version_id'; st text := p->>'status'; ok boolean := (p->>'status') = 'done'; v versions;
begin
  if st not in ('done','failed','qa_failed','canceled') then raise exception 'bad status %', st; end if;
  select * into r from reservations where version_id = vid for update;
  if not found then return jsonb_build_object('ok', false, 'reason', 'no_reservation'); end if;
  perform 1 from accounts where user_id = r.user_id for update;
  update versions set status = st, finished_at = now(), error = p->>'error',
         video_key = coalesce(p->>'video_key', video_key), thumb_key = coalesce(p->>'thumb_key', thumb_key),
         plan_key = coalesce(p->>'plan_key', plan_key), qa_key = coalesce(p->>'qa_key', qa_key),
         qa = coalesce(p->'qa', qa), report = coalesce(p->'report', report), cost = coalesce(p->'cost', cost),
         expires_at = case when ok then now() + make_interval(days => (p->>'retain_days')::int) else expires_at end
   where id = vid and status in ('queued','running') returning * into v;
  if r.state <> 'held' then return jsonb_build_object('ok', true, 'duplicate', true, 'reservation', r.state); end if;
  if ok then
    update reservations set state = 'captured', settled_at = now() where version_id = vid;
    if r.kind = 'free' then update accounts set free_held = free_held - 1, free_used = free_used + 1 where user_id = r.user_id; end if;
    insert into ledger(user_id, kind, ref, credits, free) values (r.user_id, 'capture', vid, 0, case when r.kind = 'free' then 1 else 0 end);
  else
    update reservations set state = 'released', settled_at = now(), reason = st where version_id = vid;
    if r.kind = 'free' then update accounts set free_held = free_held - 1 where user_id = r.user_id;
    else update accounts set credits = credits + r.amount where user_id = r.user_id; end if;
    insert into ledger(user_id, kind, ref, credits, meta) values (r.user_id, 'release', vid, case when r.kind = 'free' then 0 else r.amount end, jsonb_build_object('status', st));
  end if;
  return jsonb_build_object('ok', true, 'reservation', case when ok then 'captured' else 'released' end);
end $$;

create or replace function public.eva_set_running(p jsonb) returns jsonb language sql security definer set search_path = public as $$
  update versions set status = 'running' where id = p->>'version_id' and status = 'queued' returning jsonb_build_object('ok', true);
$$;

-- Stripe Checkout top-up, once per session id
create or replace function public.eva_topup(p jsonb) returns jsonb language plpgsql security definer set search_path = public as $$
declare uid uuid := (p->>'user_id')::uuid; c int := (p->>'credits')::int; n int; bal int;
begin
  perform 1 from accounts where user_id = uid for update;
  if not found then return jsonb_build_object('ok', false, 'reason', 'no_account'); end if;
  insert into ledger(user_id, kind, ref, credits, meta) values (uid, 'topup', p->>'session_id', c, jsonb_build_object('amount_cents', p->'amount_cents', 'livemode', p->'livemode'))
    on conflict (kind, ref) do nothing;
  get diagnostics n = row_count;
  if n = 1 then update accounts set credits = credits + c where user_id = uid; end if;
  select credits into bal from accounts where user_id = uid;
  return jsonb_build_object('ok', true, 'duplicate', n = 0, 'credits', bal);
end $$;

create or replace function public.eva_create_project(p jsonb) returns jsonb language plpgsql security definer set search_path = public as $$
begin
  insert into projects(id, user_id, title, upload_key, upload_bytes, source_expires_at)
    values (p->>'id', (p->>'user_id')::uuid, coalesce(nullif(p->>'title', ''), 'Untitled video'), p->>'upload_key', (p->>'upload_bytes')::bigint,
            now() + make_interval(days => (p->>'source_days')::int));
  return jsonb_build_object('ok', true, 'id', p->>'id');
end $$;

-- My Videos: projects with their versions (newest first), owner only
create or replace function public.eva_library(p jsonb) returns jsonb language sql security definer set search_path = public as $$
  select coalesce(jsonb_agg(x order by x->>'created_at' desc), '[]'::jsonb) from (
    select jsonb_build_object('id', pr.id, 'title', pr.title, 'created_at', pr.created_at, 'duration_s', pr.duration_s, 'upload_key', pr.upload_key,
             'source_expires_at', pr.source_expires_at,
             'versions', coalesce((select jsonb_agg(to_jsonb(v) - 'user_id' order by v.created_at desc) from versions v
                                    where v.project_id = pr.id and v.deleted_at is null), '[]'::jsonb)) x
      from projects pr where pr.user_id = (p->>'user_id')::uuid and pr.deleted_at is null
       and (p->>'project_id' is null or pr.id = p->>'project_id')) t;
$$;

create or replace function public.eva_version(p jsonb) returns jsonb language sql security definer set search_path = public as $$
  select to_jsonb(v) || jsonb_build_object('upload_key', pr.upload_key, 'project_title', pr.title)
    from versions v join projects pr on pr.id = v.project_id
   where v.id = p->>'version_id' and (p->>'user_id' is null or v.user_id = (p->>'user_id')::uuid) and v.deleted_at is null;
$$;

create or replace function public.eva_update_version(p jsonb) returns jsonb language sql security definer set search_path = public as $$
  update versions set favorite = coalesce((p->>'favorite')::boolean, favorite)
   where id = p->>'version_id' and user_id = (p->>'user_id')::uuid and deleted_at is null returning jsonb_build_object('ok', true, 'favorite', favorite);
$$;

-- user deletion: soft-delete rows now (keys returned so the server deletes the R2 objects); in-flight versions refused
create or replace function public.eva_delete(p jsonb) returns jsonb language plpgsql security definer set search_path = public as $$
declare uid uuid := (p->>'user_id')::uuid; keys jsonb;
begin
  if p ? 'version_id' then
    if exists (select 1 from versions where id = p->>'version_id' and user_id = uid and status in ('queued','running')) then
      return jsonb_build_object('ok', false, 'reason', 'busy'); end if;
    select jsonb_agg(k) into keys from (select unnest(array[video_key, thumb_key, plan_key, qa_key]) k from versions
      where id = p->>'version_id' and user_id = uid and deleted_at is null) s where k is not null;
    update versions set deleted_at = now() where id = p->>'version_id' and user_id = uid and deleted_at is null;
  else
    if exists (select 1 from versions where project_id = p->>'project_id' and user_id = uid and status in ('queued','running')) then
      return jsonb_build_object('ok', false, 'reason', 'busy'); end if;
    select jsonb_agg(k) into keys from (select unnest(array[video_key, thumb_key, plan_key, qa_key]) k from versions
      where project_id = p->>'project_id' and user_id = uid and deleted_at is null
      union all select upload_key from projects where id = p->>'project_id' and user_id = uid and deleted_at is null) s where k is not null;
    update versions set deleted_at = now() where project_id = p->>'project_id' and user_id = uid and deleted_at is null;
    update projects set deleted_at = now() where id = p->>'project_id' and user_id = uid and deleted_at is null;
  end if;
  return jsonb_build_object('ok', true, 'keys', coalesce(keys, '[]'::jsonb));
end $$;

-- retention (cron): versions and source uploads past their expiry → soft-deleted, keys returned for R2 deletion
create or replace function public.eva_expire(p jsonb) returns jsonb language plpgsql security definer set search_path = public as $$
declare keys jsonb;
begin
  select jsonb_agg(k) into keys from (
    select unnest(array[video_key, thumb_key, plan_key, qa_key]) k from versions where expires_at < now() and deleted_at is null
    union all select upload_key from projects where source_expires_at < now() and deleted_at is null and upload_key is not null) s where k is not null;
  update versions set deleted_at = now() where expires_at < now() and deleted_at is null;
  update projects set upload_key = null where source_expires_at < now() and deleted_at is null and upload_key is not null;
  return jsonb_build_object('ok', true, 'keys', coalesce(keys, '[]'::jsonb));
end $$;

-- stuck versions (worker lost): the server finishes them as failed so reservations are released
create or replace function public.eva_stuck(p jsonb) returns jsonb language sql security definer set search_path = public as $$
  select coalesce(jsonb_agg(id), '[]'::jsonb) from versions
   where status in ('queued','running') and created_at < now() - make_interval(mins => (p->>'minutes')::int);
$$;

do $$
declare f text;
begin
  for f in select p.oid::regprocedure::text from pg_proc p join pg_namespace n on n.oid = p.pronamespace
            where n.nspname = 'public' and p.proname like 'eva\_%' loop
    execute format('revoke all on function %s from public', f);
    if exists (select 1 from pg_roles where rolname = 'anon') then execute format('revoke all on function %s from anon, authenticated', f); end if;
    if exists (select 1 from pg_roles where rolname = 'service_role') then execute format('grant execute on function %s to service_role', f); end if;
  end loop;
end $$;

insert into public.eva_schema(version) values (1) on conflict do nothing;
