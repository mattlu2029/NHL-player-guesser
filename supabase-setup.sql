-- NHL Player Guess — shared stats / leaderboard
-- Run this once in your Supabase project: SQL Editor -> New query -> paste -> Run.
-- Safe to re-run: it only adds anything missing (e.g. the daily-challenge columns).

create table if not exists public.player_stats (
  user_id        uuid primary key references auth.users(id) on delete cascade,
  name           text,
  played         int  default 0,
  won            int  default 0,
  dist           jsonb default '{}'::jsonb,
  cur_streak     int  default 0,
  max_streak     int  default 0,
  last_daily_date text,
  updated_at     timestamptz default now()
);

-- Daily-challenge replay lock: remembers a signed-in user's finished daily + their guesses,
-- so they can't replay today's puzzle and their previous board is restored.
alter table public.player_stats
  add column if not exists daily_date    text,
  add column if not exists daily_target  bigint,
  add column if not exists daily_guesses jsonb,
  add column if not exists daily_won     boolean;

alter table public.player_stats enable row level security;

-- Anyone (even signed-out visitors) can read rows -> powers the public leaderboard.
drop policy if exists "read all stats" on public.player_stats;
create policy "read all stats" on public.player_stats
  for select using (true);

-- A signed-in user may create only their own row.
drop policy if exists "insert own stats" on public.player_stats;
create policy "insert own stats" on public.player_stats
  for insert with check (auth.uid() = user_id);

-- A signed-in user may update only their own row.
drop policy if exists "update own stats" on public.player_stats;
create policy "update own stats" on public.player_stats
  for update using (auth.uid() = user_id) with check (auth.uid() = user_id);
