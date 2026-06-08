-- NHL Player Guess — shared stats / leaderboard
-- Run this once in your Supabase project: SQL Editor -> New query -> paste -> Run.

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

alter table public.player_stats enable row level security;

-- Anyone (even signed-out visitors) can read rows -> powers the public leaderboard.
-- If you'd rather only let signed-in users see it, change `using (true)`
-- to `using (auth.role() = 'authenticated')`.
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
