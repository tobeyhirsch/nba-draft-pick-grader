# Real data layer (from LD Sport + NBA Cap Tracker)

Three files, built from two live-fetched sources:

- **`draft_picks_data.py`** — every team's future draft-pick ownership,
  2026-2033, transcribed from LD Sport's Future Draft Picks page
  (https://www.ldsport.com/future-draft-picks.html, fetched live). **All 30
  teams are complete.**
- **`pick_resolver.py`** — converts the raw pick-description text above
  into `pick_grading.PickAsset` objects wherever that's mechanically safe
  (a specific already-resolved slot), and cleanly separates out everything
  conditional (swaps, protections) rather than guessing at it.
- **`cap_sheet_data.py`** — real player-by-player contract data from
  nbacaptracker.com (https://www.nbacaptracker.com/teams/&lt;team-slug&gt;).
  **Only Boston Celtics is populated** — see "What's missing" below.

## Why two sources instead of one

LD Sport's own cap-sheet pages render player salaries from an embedded
OneDrive/Excel widget, not plain HTML — it's not fetchable as text. Its
Future Draft Picks page, by contrast, is real markdown-equivalent text and
came through cleanly. nbacaptracker.com publishes the same category of
data (contracts, cap holds, apron/tax standing) as an actual HTML table, so
it's the source used for `cap_sheet_data.py` instead.

## What's real vs. what needs more work

**Fully real, all 30 teams:** `draft_picks_data.py`. Every pick description
was transcribed directly from the live-fetched page, not generated or
inferred.

**Fully real, 1 of 30 teams:** `cap_sheet_data.py`. Boston Celtics'
contracts, cap holds, and thresholds were fetched live and reconcile
exactly against nbacaptracker.com's own totals (see the `__main__` block —
$183,470,055 active salary, $46,800,000 in cap holds, both match). The
other 29 teams follow the identical pattern; each needs one fetch of
`nbacaptracker.com/teams/<team-slug>` and the same transcription. This
wasn't done blind for all 30 to avoid shipping untranscribed/error-prone
data for teams nobody's asked about yet — say the word and I'll work
through the rest.

**Deliberately NOT auto-resolved:** conditional/swapped picks (e.g. "Better
of MIL and NO," "If #5-30"). `pick_resolver.py` explains exactly why in its
docstring — these depend on the joint outcome of two or three teams'
seasons, which only `draft_pipeline_321.py`'s Monte Carlo can resolve
correctly. Wiring that resolution in (running the specific teams involved
through the simulator and applying the swap condition trial-by-trial) is
the natural next module.

## Using this with the rest of the model

```python
from cap_sheet_data import get_team_cap_sheet
from pick_resolver import build_pick_assets
from pick_grading import grade_pick_portfolio

cap_sheet = get_team_cap_sheet("Boston Celtics")
assets, unresolved = build_pick_assets("Boston Celtics")
grades = grade_pick_portfolio(assets)  # only the currently-resolvable picks
# `unresolved` lists everything that still needs simulator or manual resolution
```

## One important caveat

Draft-pick ownership and cap sheets both change with every trade, option
decision, and signing. This is a snapshot from the August 2026 fetch, not a
live feed — re-fetch before relying on it for anything beyond a demo.
