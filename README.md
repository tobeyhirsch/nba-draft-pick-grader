# NBA Draft Pick Grading Model

Projects team strength from real market data, simulates NBA seasons and the
draft lottery (both the pre-2027 format and the new 2027+ "3-2-1" format),
resolves every pick a team owns -- including conditional/swap language like
"less favorable of Team A and Team B's picks" -- into a probability
distribution over draft slots, and grades each one 1-10.

**Entry point:** `python run_real_league.py` (optionally followed by one or
more team names to grade just those teams; with no arguments it grades all
30). Takes roughly 10 minutes for the full league at the default trial
count -- up from ~2 minutes before `darko_ratings.py` was wired in, since a
team's picks now run a separate simulation batch per distinct draft year
they span rather than one shared batch (see `run_real_league.py`'s
PERFORMANCE NOTE). Writes `league_pick_grades.md` (pick grades, split by
round) and `projected_standings.md` (the actual projected win-loss
standings, 2027 through 2033, for the exact same ratings that produced
those grades -- see "Projected standings" below).

## Pipeline, in order

```
market_win_totals.xlsx      PlayerSalariesCSV.csv      real_rosters_202627.py
        |                            |                          |
        v                            v                          |
market_ratings.py            cap_sheet_data.py                  |
(sportsbook lines             (5-year contracts,                |
 -> Elo ratings,               all 30 teams)                    |
 2027 draft only)                    |                          |
        |                            +------------+--------------+
        |                            |            v
        |                            |    trusted_rosters.py  (NEW -- the
        |                            |    REAL current team per player,
        |                            |    per user direction that this +
        |                            |    the cap sheet are correct and
        |                            |    darkodpmleaderboard.csv's Team
        |                            |    column is NOT -- 90/530 players
        |                            |    re-keyed, incl. Giannis/LeBron/
        |                            |    Kawhi; see its docstring)
        |                            v            |
        |                    roster_continuity.py |  ("still under
        |                    (NEW -- "still under  |  contract to THIS
        |                    contract" signal,     |  team" re-keying
        |                    name-matched, ignores |  applied INSIDE
        |                    Team entirely -- see  |  load_darko_players()
        |                    its docstring)        |  below, before any
        |                            |             |  rating is computed)
        +-------------------+        |             |
        |                   v        v             v
        |         darkodpmleaderboard.csv + darkolongevityprojections.csv
        |                   |
        |                   v
        |         multi_year_advanced_stats.csv (built by
        |         build_multi_year_stats.py from the user-supplied
        |         Advanced Stats.xlsx: DARKO/BPM/VORP/PER/age, 2023-24
        |         through 2025-26)
        |                   |
        |                   v
        |         player_value_regression.py  (LIVE -- multi-year
        |         DARKO/BPM/VORP+age regression, r^2~=0.64, upgrades
        |         404/530 players with 3 seasons on file to a
        |         regression-projected next-season DPM; the rest keep
        |         their raw current-season DPM)
        |                   |
        |                   v
        |         darko_ratings.py  (DPM+longevity+continuity, TEAMS
        |         RE-KEYED onto trusted_rosters.py, calibrated against
        |         market_ratings.py's Elo -> evolved ratings for the
        |         2028-2032 drafts)
        |                   |
        v                   v
conferences.py  ---->  standings_sim.py  <----  draft_picks_data.py
(East/West)            (season simulator)       (raw pick-ownership text,
        |                     |                   all 30 teams, 2027-2033)
        v                     v                          |
draft_pipeline_321.py  <-----+                            v
(play-in + 3-2-1 lottery,       ^                 pick_resolver.py
 both rounds, per season)       |                 (classifies each
        |                       |                  fragment: simple /
        v                       |                  swap / unresolved;
pick_restrictions_321.py        |                  runs a separate joint
(real 2025-26 history ->        |                  trial batch per draft
 "no repeat #1 / no             |                  year, using market_
 3-straight top-5" seeded       |                  ratings.py's or darko_
 for 2027)                      |                  ratings.py's teams,
        |                       |                  and each year's own
        v                       |                  history_by_year, as
run_real_league.py's            |                  appropriate)
build_restriction_history_by_year() --------------------> ^
(chains that history forward year over year,               |
 2027->2033, via advance_history() + derive_own_picks(),   |
 re-running draft_pipeline_321.py's Monte Carlo each year   |
 under the PRIOR year's history to get that year's own      |
 modal outcome -- feeds the resulting history_by_year        |
 into pick_resolver.py above)                                |
                                                            |
                                                            v
                                                    pick_valuation.py
                                                    (slot -> value, fit
                                                     from real career
                                                     outcomes)
                                                            |
                                                            v
                                                    pick_grading.py
                                                    (value -> 1-10 grade)
                                                            |
                                                            v
                                                    run_real_league.py
                                                    (orchestrates all of
                                                     the above, writes
                                                     league_pick_grades.md)
```

Everything above is exercised end to end by `run_real_league.py`.
`grading.py` (trade grading) and `roster_cap.py`'s cap-space/apron helpers
sit alongside the pipeline as tools you call directly with real assets --
they aren't wired into the automatic league-wide run.

## What each file does

### Data layer (real, sourced facts)

- **`market_win_totals.xlsx`** -- consensus 2026-27 season win-total O/U
  lines (DraftKings/FanDuel/Hard Rock/Caesars). Input to `market_ratings.py`.
- **`PlayerSalariesCSV.csv`** -- 5-year (2026-27 through 2030-31) salary and
  option data for all 30 teams, 435 contracts. Input to `cap_sheet_data.py`.
- **`darkodpmleaderboard.csv`** -- 530 active players' DARKO DPM (a
  per-100-possession plus-minus skill rating, split into ODPM/DDPM) and
  projected MPG. Input to `darko_ratings.py`.
- **`darkolongevityprojections.csv`** -- the SAME 530 players (verified
  identical `(Player, Team)` keys against the DPM file), each with a 0-100
  "still an NBA player" probability at +1 through +15 years out. Input to
  `darko_ratings.py`.
- **`multi_year_advanced_stats_TEMPLATE.csv`** -- NOT loaded by anything;
  shows the exact schema `player_value_regression.py` expects (Player,
  Team, Season, Age, DARKO_DPM, BPM, VORP -- one row per player-season) so
  a real multi-year file can be dropped in without guessing the format.
- **`multi_year_advanced_stats.csv`** -- the REAL multi-year file, 1,501
  player-season rows / 713 players, 2023-24 through 2025-26 (Season labeled
  by ending year: 2024/2025/2026). Built by `build_multi_year_stats.py`
  from a user-supplied `Advanced Stats.xlsx` (DARKO DPM leaderboards +
  Basketball-Reference PER/BPM/VORP/Age tables for those 3 seasons) --
  that script isn't part of the runtime pipeline, it's a one-time
  converter; re-run it if a newer `Advanced Stats.xlsx` is supplied. Also
  carries a PER column the regression doesn't use yet (see
  `player_value_regression.py`'s note on this). This is what
  `run_real_league.MULTI_YEAR_STATS_CSV` points at.
- **`conferences.py`** -- static East/West assignment for all 30 teams.
- **`draft_picks_data.py`** -- every team's pick ownership, 2027-2033, as
  raw text transcribed from LD Sport (credited to ESPN) -- e.g. `"MIL/NO
  (Less Favorable) 1st (If #5-30)"`. Deliberately kept as text rather than
  pre-resolved, since resolving conditional language requires simulation
  (see `pick_resolver.py` below). The 2026 draft has concluded, so each
  team's already-resolved 2026 selection(s) were removed -- this table now
  starts at 2027, the next draft the pipeline actually projects.
- **`cap_sheet_data.py`** -- parses `PlayerSalariesCSV.csv` into
  `roster_cap.Contract`/`CapSheet` objects for all 30 teams at import time.
  Its docstring has the full history of why this superseded four earlier
  scraping attempts (nbacaptracker.com, Spotrac, LD Sport, HoopsHype), all
  of which had confirmed data-quality or access problems. Now actually
  consumed at runtime, by `roster_continuity.py` (see below) -- it used to
  be a standalone data layer nothing else imported.
- **`team_codes.py`** -- maps the 2-3 letter team codes used in
  `draft_picks_data.py`'s pick text (e.g. `"NO"`, `"GS"`) to the full team
  names used everywhere else in the pipeline.
- **`real_rosters_202627.py`** -- user-supplied real depth charts for all 30
  teams (526 players, `{team: {position: [names]}}`, names carry inline
  annotations like "(R)"/"**"/"(RFA)" the transcription kept on purpose --
  see its docstring). Originally just a reference dataset `cap_sheet_data.py`
  was cross-checked against; now ALSO consumed at runtime, by
  `trusted_rosters.py` (see below) -- it's the primary source for which
  team a player is actually on.

### Simulation layer

- **`standings_sim.py`** -- core Monte Carlo season engine. `Team` (name,
  Elo-style rating, conference), `win_probability()` (Bradley-Terry logistic
  with a home-court bump), `build_synthetic_schedule()` (balanced random
  schedule -- not the real fixture list), `simulate_season()` (one 82-game
  season -> wins per team).
- **`lottery_sim_321.py`** -- the 3-2-1 lottery's ball mechanics (16 teams,
  3/2/1 balls per the league's official rules, floor protections at picks
  12/16) plus, via `pick_restrictions_321.py`, the "no repeat #1 / no
  3-straight top-5" pick restrictions.
- **`pick_restrictions_321.py`** -- implements those restrictions, seeded
  with the REAL 2025 and 2026 draft results (given directly, not simulated)
  so the very first 3-2-1 draft (2027) is constrained correctly: Washington
  can't get pick 1 (they had it in 2026), Utah can't land top-5 (they did
  in both 2025 and 2026). `enforce_pick_restrictions()` re-seats any
  restricted team by filling each slot 1..n with the first still-legal team
  remaining in queue order -- a slot-by-slot fill, not the naive "bump the
  violator down, shift the rest up" splice it started as. That splice
  version worked fine for 2027 (at most one team restricted per rule this
  year), but with two or more teams simultaneously restricted from the same
  range -- which happens once restrictions are chained into later years,
  see below -- it could bump one violator onto another and back, forever;
  the current slot-by-slot version has no such failure mode and always
  terminates. `advance_history()` (fold one year's own-pick outcomes into
  the next year's history) and `derive_own_picks()` (collapse a full
  Monte Carlo pick-count distribution to one representative "own pick" per
  team, by MODE across trials -- see its docstring for why this is a
  documented approximation, consistent with the rest of the pipeline's
  independent-trials-per-year design, rather than one fully-correlated
  multi-year chain) are what let `run_real_league.py`'s
  `build_restriction_history_by_year()` chain this rule from the real 2027
  seed all the way through the 2033 draft, instead of only enforcing it for
  2027.
- **`draft_pipeline_321.py`** -- ties a season simulation to the play-in
  game, the lottery draw, and the second round, all from one simulated
  season so a team's first- and second-round outcomes stay correlated.
  Round 2 uses the rule effective the 2027 draft onward
  (`simulate_second_round_order()`): picks 31-46 are a SNAKE off the
  round-1 lottery order (the team that picked 16th in round 1 picks 31st;
  the team that picked 1st picks 46th), and picks 47-60 continue reverse
  standings among the playoff teams, with ties broken in reverse order of
  those teams' round-1 positions. `joint_pick_number_trials()` is the
  function `swap_resolver.py` depends on: it runs many simulated seasons and
  returns every requested team's pick numbers **from the same trials**,
  preserving the correlation swap comparisons need (two teams' records
  aren't independent -- same conference, overlapping schedules).
- **`market_ratings.py`** -- converts the sportsbook win-total spreadsheet
  into calibrated Elo ratings via iterative fixed-point fitting (there's no
  closed-form solution since all 30 ratings are jointly determined). This is
  the ground truth for the 2027 draft specifically (the season the market
  lines actually cover); see `market_ratings.py`'s docstring for why market
  data, not a DARKO sum, is used as-is for that one season.
- **`darko_ratings.py`** -- projects team strength for the 2028-2032 drafts,
  which the market hasn't priced. Builds each team's MPG-weighted DARKO net
  rating, fits a linear regression against `market_ratings.py`'s Elo (r^2
  reported by its `__main__` -- check it before trusting anything
  downstream), then re-derives that net rating per future year by
  multiplying each player's contribution by TWO independent 0-1 signals:
  their career-longevity probability at that year (still an NBA player
  ANYWHERE) and, new this round, their `roster_continuity.py` weight
  (still under contract to WHEREVER they're currently rostered
  specifically). Both a retiring player's and a departed-via-continuity
  player's minutes are treated as replacement-level, not redistributed to
  teammates. Capped at 5 years out because the model can never GAIN
  talent (no incoming rookies/trades/free agents modeled) -- though it's
  worth knowing that doesn't mean a clean flat-or-down trajectory: because
  below-average/fringe players' presence and continuity tend to decay
  FASTER than stars', a team's rating can actually RISE in the near term
  as its weakest contributors drop out first (Denver: 1.05 -> 1.44 -> 1.46
  -> 1.27 at offsets 0/1/3/5, confirmed directly), before eventually
  declining as the stars' own presence fades. See its docstring for the
  full reasoning on both the model and that correction. Each player's DPM
  input comes from `player_value_regression.load_darko_players_with_projection()`
  (see below), LIVE since the previous round; each player's TEAM is now
  re-keyed onto `trusted_rosters.py`'s real current-roster data (see
  below) rather than DARKO's own (partly stale) Team column.
- **`player_value_regression.py`** -- LIVE: projects a player's NEXT-SEASON
  DARKO DPM from multiple years of DARKO/BPM/VORP plus age, instead of
  treating last season's single DPM snapshot as-is. Fits an interpretable
  4-feature OLS regression (age, age^2, a z-scored recent-form composite,
  and a year-over-year trend slope) via `numpy.linalg.lstsq`. Fit against
  the real `data/multi_year_advanced_stats.csv` (318 training rows, well
  past the 15-row overfitting floor its own `fit_regression()` checks
  for): r^2~=0.64, comparable to `darko_ratings.py`'s own DPM-to-Elo fit.
  Using these regression-projected values (instead of raw current-season
  DPM) as `darko_ratings.py`'s input actually IMPROVES its fit against
  market Elo, from r^2~=0.66 to r^2~=0.72 -- a real signal the multi-year
  trend/age features are adding information, not just noise. 404 of 530
  current players have the required 3 seasons on file and get a
  regression-projected value; the other 126 (mostly rookies/short-history
  players) fall back to `darko_ratings.py`'s original single-year behavior
  automatically, so this was a strict upgrade, never a data loss. The
  module still also still supports its original small labeled-synthetic
  fixture in `__main__` for mechanics validation, and still falls back to
  fully-`None`/no-op behavior if `run_real_league.MULTI_YEAR_STATS_CSV` is
  ever unset again.
- **`roster_continuity.py`** -- NEW, LIVE: the "still under contract to
  THIS team" signal `darko_ratings.py` was missing (longevity alone only
  knows "still an NBA player somewhere"; a player can stay in the league
  while leaving via free agency/trade, and the old model had no way to
  catch that). Sourced from `PlayerSalariesCSV.csv`'s real contract years
  and player/team/mutual option flags (via `cap_sheet_data.py`/
  `roster_cap.py`). Returns 1.0 (neutral, no penalty) when there's no
  contract on file or the season falls past the cap sheet's 2030-31
  coverage window, `OPTION_YEAR_CONTINUITY=0.7` for an option year, and
  `NOT_ON_BOOKS_CONTINUITY=0.3` when the player's tracked contract simply
  doesn't reach that season -- both flagged, undocumented-elsewhere
  ASSUMPTIONS, not fits (no data source here says how often options get
  exercised or expiring vets get retained). Matches players to contracts
  by NAME ONLY, deliberately ignoring the Team column -- see the next
  bullet for why. 383 of DARKO's 530 players (72%) have a name-matched
  contract; the other 147 (mostly deep-bench/two-way) get the neutral
  default, spot-checked to confirm they're genuinely absent from the cap
  sheet, not a matching miss.
  **DISCOVERY while building this, now FIXED (see `trusted_rosters.py`
  below):** `darkodpmleaderboard.csv`'s Team column disagreed with
  `PlayerSalariesCSV.csv`'s / `real_rosters_202627.py`'s for a meaningful
  number of players, including several stars -- Giannis Antetokounmpo was
  Miami Heat in the cap sheet/depth chart vs. Milwaukee Bucks in DARKO,
  LeBron James was Philadelphia 76ers vs. Los Angeles Lakers, Kawhi
  Leonard was Toronto Raptors vs. Los Angeles Clippers (90 such mismatches
  found on a direct join). `real_rosters_202627.py` -- `cap_sheet_data.py`'s
  OWN cross-check ground truth -- agreed with the cap sheet, not DARKO, on
  every case checked, so this looked like the cap sheet + depth chart
  describing a different (already-traded) roster reality than the DARKO
  snapshot. Per explicit user direction, the cap sheet/depth chart ARE the
  correct team assignments, real trades DARKO's snapshot hadn't caught up
  to -- see `trusted_rosters.py` for the fix.
- **`trusted_rosters.py`** -- NEW, LIVE: re-keys every DARKO player's team
  onto their REAL current team, per the discovery above. Source priority:
  `real_rosters_202627.TEAM_DEPTH_CHARTS` first (526 players, stripping
  its inline annotations), then `PlayerSalariesCSV.csv`'s Team column for
  the handful the depth chart doesn't cover but the cap sheet does (5 at
  last check). `darko_ratings.load_darko_players()` calls this for every
  player and re-keys `DarkoPlayer.team` wherever it's covered (443/530
  players, 90 of those actually changing team), falling back to DARKO's
  own Team column for the 87 neither trusted source covers. This isn't
  just a future-years fix -- it changes the CURRENT-season (2027 draft)
  DARKO-to-market-Elo fit too, since that's grouped by the same
  `DarkoPlayer.team`. Result: r^2 went from 0.721 (mislabeled teams) to
  0.731 (corrected) on its own, and to 0.737 combined with
  `player_value_regression.py`'s multi-year upgrade -- both real DIRECTION
  improvements (fixing the mislabeling made the model fit the real market
  better, which is exactly what you'd hope a correction does), though
  modest in size.
- **`name_matching.py`** -- shared `normalize_name()` (strips diacritics,
  periods, apostrophes, and Jr./Sr./II/III/IV suffixes) used by
  `build_multi_year_stats.py`, `roster_continuity.py`, and
  `trusted_rosters.py` to join player names across sources that don't
  spell them identically. Not a fuzzy matcher -- true nickname mismatches
  (Bones Hyland / Nah'Shon Hyland) still need a small hand-verified alias
  table local to whichever module is doing that specific join.

### Ownership resolution layer

- **`swap_resolver.py`** -- resolves four tiers of conditional pick
  language into an actual probability distribution, all built on
  `joint_pick_number_trials()`'s correlated trials so comparisons/conditions
  use the SAME simulated season for every team involved:
    1. Flat "TEAM1/TEAM2[/.../TEAM5] (Qualifier) ROUND [(If #A-B)]" swaps
       (up to 5 named teams).
    2. Same-year, single-team cross-pick conditionals -- "TEAM ROUND (If
       YEAR OTHER_TEAM ROUND is #A-B)", e.g. "PHI 2nd (If 2028 PHI 1st is
       #1-8)" -- the pick only conveys in trials where the named condition
       holds that SAME year (`ConditionalPick`/`PickAsset.convey_probability`).
    3. 2-level NESTED swaps -- one member of a flat swap is itself a
       parenthesized flat sub-swap, e.g. "ATL/(CLE/UTA (Less Favorable))
       (More Favorable) 1st" (`NestedSwap`, evaluated per-trial via a small
       recursive tree walk).
    4. A bare "(#A-B)" protection range with no "If" text, but ONLY when
       edge-anchored to one boundary of the round's own number range --
       the same safety net that already governed whether this could ever
       resolve to anything.
  Deliberately still conservative past that: a team carrying its OWN inline
  range condition inside a swap list (e.g. "DEN (If #6-30)/LAC/OKC...") is
  REJECTED rather than resolved, because that same surface syntax covers at
  least two different real mechanics (the pool shrinking to whoever's left,
  vs. the whole fragment simply not conveying) and the raw text alone
  doesn't say which -- guessing between them risks exactly the
  "plausible-looking but wrong number" this module's docstring warns
  against. A REORDERED "(If #A-B)" appearing before the qualifier (instead
  of after, e.g. "ATL/HOU (If #31-55) (More Favorable) 2nd") is only
  accepted when a differently-ordered sibling fragment elsewhere in the
  data CONFIRMS it's an ordinary swap-result protection (see
  `_confirmed_trailing_swap_protections()`) -- otherwise it's just as
  likely to be a per-team gate in disguise (confirmed by a real example:
  Memphis's 2029 "MEM/ORL (If #3-30) (More Favorable) 1st" looks identical
  to the confirmed-safe ATL/HOU case, but Orlando's own complementary
  fragment shows the condition is really about ORL's own pick number, not
  the swap result -- left unresolved). Cross-year conditionals (the
  condition's year differs from the pick's own year) and true multi-year
  protection chains are still out of scope for the reason stated above --
  they need multiple draft years correlated within the same trial, which
  this pipeline's per-year-independent-trials design doesn't support.
- **`pick_resolver.py`** -- the orchestrator for one team's whole pick
  portfolio. Classifies every fragment into one of five buckets (simple /
  flat swap / cross-pick conditional / nested swap / unresolved), and runs
  a joint trial batch per distinct draft year that portfolio needs (via
  `teams_by_year`, e.g. `darko_ratings.py`'s evolved 2028-2032 teams --
  years not covered fall back to a single shared batch against the base
  league, same as before `teams_by_year` existed), returning ready-to-grade
  `PickAsset` objects plus a list of what's still unresolved and why.

### Valuation and grading layer

- **`pick_valuation.py`** -- `pick_value(pick_number)`, a 0-100 relative
  value curve. Calibrated (see `calibrate_pick_value.py`) against 271 real
  2015-2023 first-round career outcomes rather than assumed: picks 1-5
  average roughly 3x the value of picks 6-30, which are themselves fairly
  flat. Second-round picks (31-60, no data available) get the fitted curve
  continued with a documented 0.4x haircut.
- **`calibrate_pick_value.py`** -- the reproducible derivation script for
  the constants hardcoded in `pick_valuation.py`. Not imported by anything;
  run it directly if you get updated career-outcome data and want to
  re-fit the curve. Needs `NBA_Draft_Picks_20152025.xlsx` and `scipy`.
- **`roster_cap.py`** -- `Contract`/`CapSheet` dataclasses (used by
  `cap_sheet_data.py`), current league cap/tax/apron thresholds, and a
  parametric rookie-scale salary approximation for connecting a pick's
  projected slot to its likely cap hit.
- **`pick_grading.py`** -- `PickAsset` (one pick: known slot or a
  probability distribution, optional protection range, optional
  `convey_probability` for a pick whose existence is itself conditional on
  a DIFFERENT pick's outcome -- see `swap_resolver.py`'s cross-pick
  conditional tier -- and a time discount for future years) and the 1-10
  grade, which is literally the pick's percentile rank against all 60
  draft slots on the `pick_valuation.py` curve.
- **`grading.py`** -- two additional, standalone graders: `grade_trade()`
  (value received vs. given -> letter grade) and `grade_selection()` (did a
  team take the best available prospect relative to your own board). Both
  use arbitrary threshold scales, documented as needing calibration against
  real trade history before being treated as authoritative.

### Orchestration and tests

- **`run_real_league.py`** -- the real entry point. Calibrates all 30
  teams' ratings from the market spreadsheet, chains the 3-2-1 pick
  restrictions across every simulated year via
  `build_restriction_history_by_year()` (seeded with real 2025-26 history
  for 2027, then `pick_restrictions_321.advance_history()`/
  `derive_own_picks()` carry it forward through 2033 -- `1000` trials/year,
  `RESTRICTION_TRIALS`/`RESTRICTION_SEED`), prints a
  `summarize_restrictions()` diagnostic of which team is blocked from which
  slot in which year, grades every pick every team owns using that
  per-year `history_by_year`, and writes `league_pick_grades.md` and
  `projected_standings.md`.
- **`test_swap_resolver_integration.py`** -- end-to-end regression check:
  builds a real 30-team league, resolves every team's full pick portfolio,
  and sanity-checks every swap's resolved distribution (probabilities sum
  to ~1, every pick number lands in the correct round's 1-30/31-60 range).
  Run this after changing anything in the resolution or simulation layers.

### Projected standings

`league_pick_grades.md` reports pick VALUES, not the standings those values
are simulated from -- `projected_standings.md` fills that in.
`run_real_league.py`'s `build_projected_standings()` takes the exact same
ratings object used for every pick grade (`teams` for 2027,
`teams_by_year[year]` for 2028-2032, `teams` again for 2033) and runs each
through `standings_sim.expected_wins()` -- plain Monte Carlo win-total
averaging, no lottery or draft-order logic attached -- so the standings
shown are a direct readout of what's actually driving the grades, not a
separately-derived number that could quietly drift out of sync with them.
Each season gets its own East/West table (rank, average wins/losses, games
back), matching how real NBA standings are displayed.

Two things worth knowing before reading it: 2027's and 2033's tables come
out byte-identical -- both use the unmodified 2026-27 market ratings with
the same random seed, since 2033 falls outside `darko_ratings.py`'s
5-year evolved-ratings window (see that module's docstring for why the
window stops at 2032). And every year's average wins already reflect
`darko_ratings.py`'s mean-reversion behavior (a team's rating drifts toward
league-average as its current DPM-weighted core is expected to retire) --
so a team's standings sliding toward .500 in the later years isn't the
model predicting a specific decline, it's the visible consequence of that
assumption; see `darko_ratings.py`'s docstring for the full reasoning.

## Known gaps (honest status, not hidden)

- **32 of 419 pick fragments across the league don't auto-resolve** (last
  checked -- down from an earlier 58 of 393, after `swap_resolver.py`
  gained the same-year cross-pick conditional, nested-swap, and
  edge-anchored-bare-range tiers described above): 21 have swap language
  this conservative parser deliberately declines to guess at -- a
  per-member inline condition whose real-world semantics are ambiguous
  from the text alone (dynamic pool vs. all-or-nothing gate -- see
  `swap_resolver.py`'s module note), an unconfirmed reordered protection,
  or a genuine elliptical continuation fragment; 7 are cross-pick
  conditionals where the condition's year differs from the pick's own year
  (still needs multiple draft years correlated within the same trial, out
  of scope for the reason given in `swap_resolver.py`); 4 don't match any
  known pattern (including two literal "(conditional chain)" placeholders
  in the source data for Denver's multi-year protection chain, and one
  fragment with mismatched parens). `pick_resolver.py`'s output always
  lists these with a specific reason rather than silently guessing.
- **Multi-year team-strength evolution is now partial, not absent.** The
  2028-2032 drafts use `darko_ratings.py`'s DARKO+longevity-evolved ratings
  instead of a frozen snapshot -- but it's a bounded, honestly-caveated
  model, not a real forecast:
  - It can never GAIN talent over time -- departing players' minutes (from
    retiring, per longevity, or from leaving that specific team, per the
    new `roster_continuity.py`) are modeled as going to a replacement-level
    (0 DPM) stand-in, never a rookie who develops, a trade addition, or a
    free agent -- there's no "new talent enters the league" term. This is
    why the window stops at 5 years out (2032) rather than the full 15
    years the longevity data covers. That does NOT mean a clean flat-or-
    down trajectory, though: below-average/fringe players' presence and
    continuity tend to decay FASTER than stars' (less certain to stick
    around at all, less certain to stay on THIS team specifically), so a
    team's rating can actually RISE in the near term as its weakest
    contributors drop out first, before eventually declining as the stars'
    own presence fades -- confirmed directly (Denver: 1.05 -> 1.44 -> 1.46
    -> 1.27 at offsets 0/1/3/5). An earlier version of this doc claimed a
    guaranteed flat-or-down shape; that was wrong and has been corrected
    here and in `darko_ratings.py`'s own docstring.
  - **Roster continuity (`roster_continuity.py`) and a real data-integrity
    finding that came with it, now fixed (`trusted_rosters.py`).**
    `roster_continuity.py` adds a "still under contract to THIS team"
    signal from `PlayerSalariesCSV.csv`'s real contract years/options
    (separate from longevity's "still an NBA player somewhere" signal) --
    see its bullet above for the mechanics and the two flagged, unfit
    discount constants it uses. Building it surfaced a real inconsistency:
    `darkodpmleaderboard.csv`'s Team column disagreed with
    `PlayerSalariesCSV.csv`'s / `real_rosters_202627.py`'s for 90 players,
    including stars (Giannis, LeBron, Kawhi among them) -- per explicit
    user direction, the cap sheet/depth chart are correct (real trades
    DARKO's snapshot hadn't caught up to). `trusted_rosters.py` now
    re-keys `darko_ratings.load_darko_players()`'s team assignment onto
    those trusted sources for every player they cover, so this is no
    longer an open gap -- see its bullet above for the mechanics and the
    (small, positive) effect on the DARKO-to-market fit. The two follow-up
    questions this raised turned out to be non-issues on inspection:
    `darkolongevityprojections.csv` is joined to the DPM file by DARKO's
    OWN (Player, Team) key purely to pair the two files up -- the
    resulting longevity number is a property of the PLAYER, not their
    team label, so re-keying the team afterward doesn't disturb it; and
    `market_ratings.py`'s win-total data is real-franchise-level (from
    sportsbook lines), never keyed by any individual player's team at
    all, so there was never a DARKO-side-vs-cap-sheet-side ambiguity there
    to resolve.
  - The DARKO-to-market fit is real but moderate (r^2 ~ 0.66 at last check,
    reported by `darko_ratings.py`'s `__main__` -- always re-check it if the
    input CSVs change). The single biggest miss is deep, balanced rosters
    like Oklahoma City's: MPG-weighting a full 18-man roster dilutes a
    stacked rotation with garbage-time bench minutes, so a team that's
    genuinely elite by market consensus can come out looking merely
    "above average" in DARKO-implied terms -- which shows up as a
    conspicuous jump between that team's 2027 pick grade (real market data)
    and its 2028+ grades (the lower DARKO-implied number). Worth a manual
    sanity check for any team whose grades jump sharply at that boundary.
  - Players who stay on the roster are scored at one FIXED skill value for
    every future year, only presence (the longevity decay) varies by year.
    That fixed value is now `player_value_regression.py`'s regression-
    projected next-season DPM where available (404/530 players -- an
    age/trend-aware one-step-ahead projection, not the raw prior-season
    snapshot), but it's still only projected ONE season forward and then
    held flat through 2028-2032 -- there's no re-projection that ages a
    player further for each additional year out, so a player already in
    decline is under-penalized by 2032 relative to 2028.
  - 2027 and 2033 aren't touched by this model: 2027 uses
    `market_ratings.py`'s real 2026-27 market ratings directly (the best
    signal available for the season that's actually about to happen), and
    2033 falls back to that same flat baseline since it's outside the
    5-year window.
- **The 3-2-1 lottery is applied uniformly to every future year (2027 and
  beyond)**, even though the league has only confirmed the format through
  the 2029 draft; 2030+ rules are pending a future Board of Governors vote.
- **Pick restrictions are now chained across every simulated year (2027
  through 2033), not just 2027.** `run_real_league.build_restriction_
  history_by_year()` seeds 2027 with the real 2025-26 history as before,
  then carries it forward year by year: each year's full Monte Carlo
  pick-count distribution is collapsed to a single MODAL (most frequent)
  "own pick" per team via `pick_restrictions_321.derive_own_picks()`, which
  is what feeds the next year's restriction check via `advance_history()`.
  This is a documented approximation, not a fully-correlated multi-year
  chain (a real one would need every trial's 2028 draft to depend on that
  SAME trial's 2027 result, which no other part of this pipeline does
  either -- every draft year already runs as its own independent trial
  batch, e.g. `build_projected_standings()`) -- it can misjudge a team's
  restriction status only in the rare case where a year's outcome is a
  near-even three-way-or-worse split with no clear plurality pick number.
- **No cap-holds data** (pending free agents, unsigned draft rights) --
  `cap_sheet_data.py`'s `TEAM_CAP_HOLDS` is empty; the source CSV only
  covers signed active contracts.
- **The trade-protection ban** ("no top-12-through-15 protections on newly
  traded picks") and the **league's discretionary authority** to adjust
  odds/positions for tanking are both explicitly out of scope -- the first
  is a trade-time legal constraint, not a simulation mechanic; the second
  is inherently arbitrary.
