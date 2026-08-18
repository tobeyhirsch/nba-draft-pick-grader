# NBA Draft Pick Grading Model

Projects team strength from real market data, simulates NBA seasons and the
draft lottery (both the pre-2027 format and the new 2027+ "3-2-1" format),
resolves every pick a team owns -- including conditional/swap language like
"less favorable of Team A and Team B's picks" -- into a probability
distribution over draft slots, and grades each one 1-10.

**Entry point:** `python run_real_league.py` (optionally followed by one or
more team names to grade just those teams; with no arguments it grades all
30). Takes about 2 minutes for the full league at the default trial count.
Writes `league_pick_grades.md`.

## Pipeline, in order

```
market_win_totals.xlsx                    PlayerSalariesCSV.csv
        |                                          |
        v                                          v
market_ratings.py                          cap_sheet_data.py
(sportsbook lines -> Elo ratings)          (5-year contracts, all 30 teams)
        |
        v
conferences.py  ---->  standings_sim.py  <----  draft_picks_data.py
(East/West)            (season simulator)       (raw pick-ownership text,
        |                     |                   all 30 teams, 2026-2033)
        v                     v                          |
draft_pipeline_321.py  <-----+                            v
(play-in + 3-2-1 lottery,                         pick_resolver.py
 both rounds, per season)                         (classifies each
        |                                          fragment: simple /
        v                                          swap / unresolved)
pick_restrictions_321.py                                  |
(real 2025-26 history ->                                  v
 "no repeat #1 / no                                swap_resolver.py
 3-straight top-5" for 2027)                       (resolves swaps via
        |                                           joint Monte Carlo
        +------------------------------------------>trials from
                                                     draft_pipeline_321.py)
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
- **`conferences.py`** -- static East/West assignment for all 30 teams.
- **`draft_picks_data.py`** -- every team's pick ownership, 2026-2033, as
  raw text transcribed from LD Sport (credited to ESPN) -- e.g. `"MIL/NO
  (Less Favorable) 1st (If #5-30)"`. Deliberately kept as text rather than
  pre-resolved, since resolving conditional language requires simulation
  (see `pick_resolver.py` below).
- **`cap_sheet_data.py`** -- parses `PlayerSalariesCSV.csv` into
  `roster_cap.Contract`/`CapSheet` objects for all 30 teams at import time.
  Its docstring has the full history of why this superseded four earlier
  scraping attempts (nbacaptracker.com, Spotrac, LD Sport, HoopsHype), all
  of which had confirmed data-quality or access problems.
- **`team_codes.py`** -- maps the 2-3 letter team codes used in
  `draft_picks_data.py`'s pick text (e.g. `"NO"`, `"GS"`) to the full team
  names used everywhere else in the pipeline.
- **`real_rosters_202627.py`** -- user-supplied real depth charts for all 30
  teams, kept as a reference/ground-truth dataset. Not imported by any
  runtime module (`cap_sheet_data.py` parses the CSV directly) -- it exists
  because it's what the CSV's player-team attributions were cross-checked
  against before trusting them. Useful if you get new roster/salary data
  and want to re-validate it the same way.

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
  in both 2025 and 2026).
- **`draft_pipeline_321.py`** -- ties a season simulation to the play-in
  game, the lottery draw, and the (lottery-free, straight-reverse-standings)
  second round, all from one simulated season so a team's first- and
  second-round outcomes stay correlated. `joint_pick_number_trials()` is the
  function `swap_resolver.py` depends on: it runs many simulated seasons and
  returns every requested team's pick numbers **from the same trials**,
  preserving the correlation swap comparisons need (two teams' records
  aren't independent -- same conference, overlapping schedules).
- **`market_ratings.py`** -- converts the sportsbook win-total spreadsheet
  into calibrated Elo ratings via iterative fixed-point fitting (there's no
  closed-form solution since all 30 ratings are jointly determined).

### Ownership resolution layer

- **`swap_resolver.py`** -- resolves flat "TEAM1/TEAM2 (Qualifier) ROUND"
  swap language into an actual probability distribution, using
  `joint_pick_number_trials()`'s correlated trials. Conservative by design:
  only resolves single-fragment comparisons among 2-4 named teams; leaves
  nested/elliptical language and cross-year conditionals unresolved with an
  explicit reason rather than guessing.
- **`pick_resolver.py`** -- the orchestrator for one team's whole pick
  portfolio. Classifies every fragment (simple / swap / unresolved), runs
  ONE shared batch of joint trials covering everything that portfolio needs,
  and returns ready-to-grade `PickAsset` objects plus a list of what's still
  unresolved and why.

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
  probability distribution, optional protection range, time discount for
  future years) and the 1-10 grade, which is literally the pick's
  percentile rank against all 60 draft slots on the `pick_valuation.py`
  curve.
- **`grading.py`** -- two additional, standalone graders: `grade_trade()`
  (value received vs. given -> letter grade) and `grade_selection()` (did a
  team take the best available prospect relative to your own board). Both
  use arbitrary threshold scales, documented as needing calibration against
  real trade history before being treated as authoritative.

### Orchestration and tests

- **`run_real_league.py`** -- the real entry point. Calibrates all 30
  teams' ratings from the market spreadsheet, grades every pick every team
  owns (seeding the 2027 pick restrictions with real history), and writes
  `league_pick_grades.md`.
- **`test_swap_resolver_integration.py`** -- end-to-end regression check:
  builds a real 30-team league, resolves every team's full pick portfolio,
  and sanity-checks every swap's resolved distribution (probabilities sum
  to ~1, every pick number lands in the correct round's 1-30/31-60 range).
  Run this after changing anything in the resolution or simulation layers.

## Known gaps (honest status, not hidden)

- **58 of 511 pick fragments across the league don't auto-resolve** (last
  checked): 28 have nested/elliptical swap language the parser doesn't
  attempt, 23 are cross-pick conditionals that depend on a *different*
  pick's outcome (would need multi-year team-strength modeling, which this
  pipeline doesn't do), 5 don't match any known pattern, 2 are ambiguous
  parenthetical ranges. `pick_resolver.py`'s output always lists these with
  a specific reason rather than silently guessing.
- **No multi-year team-strength evolution.** Every future year's pick
  distribution for a team comes from the SAME one-season simulation
  (current market-calibrated ratings), only time-discounted via
  `years_away`. A 2033 pick is graded as if today's team strength holds
  for seven more years, which it won't -- there's no mechanism here for
  aging curves, expected roster turnover, or CBA changes.
- **The 3-2-1 lottery is applied uniformly to every future year (2027 and
  beyond)**, even though the league has only confirmed the format through
  the 2029 draft; 2030+ rules are pending a future Board of Governors vote.
- **Pick restrictions are only seeded for 2027.** The "no repeat #1 / no
  3-straight top-5" rule is enforced with real history for 2027 specifically;
  other years are simulated unrestricted since there's no real (or modeled)
  history to seed them with -- see `pick_resolver.py`'s `history` parameter
  docstring.
- **No cap-holds data** (pending free agents, unsigned draft rights) --
  `cap_sheet_data.py`'s `TEAM_CAP_HOLDS` is empty; the source CSV only
  covers signed active contracts.
- **The trade-protection ban** ("no top-12-through-15 protections on newly
  traded picks") and the **league's discretionary authority** to adjust
  odds/positions for tanking are both explicitly out of scope -- the first
  is a trade-time legal constraint, not a simulation mechanic; the second
  is inherently arbitrary.
