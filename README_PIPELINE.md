# NBA Draft Pick Grader — full pipeline

Seven modules, each independently testable, chained together in
`run_full_pipeline_demo.py`.

```
team_wins.py            player DARKO/EPM + minutes -> team Elo rating
        |
standings_sim.py         Elo ratings -> Monte Carlo season simulation
        |
lottery_sim.py            \_ pre-2027 lottery mechanics (top-4 draw)
lottery_sim_321.py         \_ 2027+ "3-2-1 Lottery" mechanics
draft_pipeline_321.py     season sim -> conference seeding -> play-in -> 3-2-1 draw
        |
pick_valuation.py        pick number / distribution -> expected surplus value
        |
roster_cap.py             (parallel) cap sheet + rookie-scale cost estimate
        |
grading.py                pick value + manual asset values -> trade/selection grade
```

## Quick start

```bash
pip install --break-system-packages -r requirements.txt   # stdlib only, nothing to actually install
cd src

# individual sanity checks (each file's __main__ block)
python lottery_sim.py
python lottery_sim_321.py
python standings_sim.py    # no __main__ block yet -- see run_demo.py instead
python team_wins.py
python roster_cap.py
python pick_valuation.py
python grading.py

# full demos
python run_demo.py                  # pre-2027 lottery only
python run_demo_321.py              # pre-2027 vs. 3-2-1, side by side
python run_full_pipeline_demo.py    # rosters -> ratings -> lottery -> value -> grade
```

## What's solid vs. what's a placeholder

**Solid / exact:**
- Lottery ball mechanics for both formats (`lottery_sim.py`, `lottery_sim_321.py`)
  — verified against published odds tables, 0 floor-protection violations
  across 20k+ trials.
- Current 2026-27 cap/tax/apron figures in `roster_cap.py` (confirmed via
  league announcement, July 2026).
- The season/lottery Monte Carlo loop itself (`standings_sim.py`,
  `draft_pipeline_321.py`) — mechanically correct given whatever ratings
  you feed in.

**Documented approximations (each flagged in its module's docstring —
read them before trusting specific numbers):**
- `team_wins.py`: additive DARKO aggregation (no lineup-fit effects),
  flat pace assumption, an unfitted Elo-conversion constant.
- `roster_cap.py`: rookie-scale salaries are a smooth parametric curve,
  NOT the league's actual published rookie-scale table.
- `pick_valuation.py`: the pick-value curve is an illustrative exponential
  decay, not a real regression against historical player outcomes.
- `grading.py`: letter-grade thresholds are arbitrary cutpoints, not
  calibrated against how real trades have been received.
- `standings_sim.py`: synthetic schedule (not the real fixture list), no
  extra-binomial variance beyond game-by-game randomness.
- `draft_pipeline_321.py`: one explicit interpretation of the reformed
  play-in format, called out because official rule language wasn't fully
  available at time of writing.

## Known gaps (not yet built)

- **Multi-year pick restrictions** (no team's own pick #1 overall in
  consecutive drafts, top-5 in 3 consecutive drafts) — needs draft history
  tracked across simulated seasons.
- **Pick ownership / trade protections** — `simulate_lottery()` and
  `simulate_321_lottery()` return picks by *original* team, not *owning*
  team. A pick-ownership remapping step (using `roster_cap.py`'s contract
  data plus a trade ledger) would sit between the lottery output and
  grading.
- **Prospect ranking model** — `grading.grade_selection()` needs a ranked
  board as an input; nothing here generates that board (translated stats,
  athletic testing, age-adjusted production would be its own module).
- **Free-agency / roster-change scenarios** — `roster_cap.py` gives you the
  plumbing (cap space, apron status, expiring contracts) but deliberately
  doesn't simulate actual transactions; that's a judgment layer, not a
  model.
