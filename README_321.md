# 3-2-1 Lottery (2027-2029 format)

Three new files, building on the pre-2027 `lottery_sim.py` / `standings_sim.py`
without modifying their behavior:

- **`lottery_sim_321.py`** — the ball mechanics: pool construction (3/2/1
  balls by category, 3-worst-record relegation), and the floor-protected
  weighted draw across all 16 picks (not just top-4 like the old format).
- **`draft_pipeline_321.py`** — wires a full season simulation into
  conference seeding, the single 7-vs-8 play-in game, and the 3-2-1 draw.
- **`run_demo_321.py`** — runs the same set of team ratings through both the
  old and new systems side by side so you can see how each team's expected
  pick shifts.

## Key rule differences from the pre-2027 format

| | Pre-2027 | 3-2-1 (2027-2029) |
|---|---|---|
| Lottery field | 14 teams | 16 teams |
| Picks drawn by lottery | 1-4 only | 1-16, all of them |
| Playoff field | 16 teams | 14 teams |
| Worst record | Best odds (14.0%) | Worse odds than 7 teams above it (relegated) |
| Pick floor | None explicit | Relegated teams: no worse than 12 |

## An assumption worth flagging

The official release and secondary reporting describe fixed counts — "the
four 9/10 seeds," "the two 7/8 losers" — which only reconcile cleanly to a
16-team, 37-ball total if the play-in itself changed shape: seeds 9 and 10
in each conference are guaranteed lottery entrants no matter what (they no
longer have a realistic road to the playoffs), and the only game that still
decides anything is a single 7-vs-8 matchup, with the loser guaranteed one
ball. That's what's implemented in `draft_pipeline_321.py`. If the league
publishes more precise play-in mechanics later, only `run_seven_eight_game`
and the seeding loop in `simulate_321_draft` need to change — the ball
mechanics and floor-protection draw in `lottery_sim_321.py` are independent
of that assumption and shouldn't need touching.

## Not modeled yet

- **Multi-year pick restrictions** (no team's own pick can be #1 overall in
  consecutive drafts, or top-5 in 3 consecutive drafts) — needs draft
  history tracked across multiple simulated seasons, which doesn't exist
  yet in this single-season pipeline.
- **Ban on top-12–15 protections on newly traded picks** — a cap-sheet /
  pick-ownership rule, not part of the draw itself.
- **League discretion to adjust odds/positions for tanking behavior** —
  inherently judgment-based, not really "simulatable."

## Sanity checks

```bash
python lottery_sim_321.py     # confirms 0 floor violations + ball-share odds
python run_demo_321.py        # full pipeline, old vs. new side by side
```
