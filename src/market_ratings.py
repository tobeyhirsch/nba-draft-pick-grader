"""
Converts consensus market win-total lines (DraftKings/FanDuel/Hard
Rock/Caesars season win-total over/unders) into Elo-style ratings for
standings_sim.Team, calibrated so that simulating a season with these
ratings reproduces each team's market-implied win total in expectation.

This replaces team_wins.py's "sum up player DARKO values" approach as the
rating source for real (non-demo) runs -- see the module-level rationale in
this project's earlier discussion: a consensus market win total already
bakes in real rosters, coaching, scheme, injury risk, and offseason moves,
all things team_wins.py's simple minutes-weighted DARKO sum explicitly
cannot capture (lineup fit, chemistry, etc.). team_wins.py/DARKO still has
a place for hypothetical rosters the market hasn't priced (a proposed
trade, next year's team) -- this module is for grading against the actual
market's view of the team that exists today.

WHY THIS NEEDS ITERATIVE CALIBRATION, NOT A CLOSED-FORM FORMULA:
A team's expected win total depends on ALL 30 teams' ratings simultaneously
(who they play, how good those opponents are) -- there's no way to convert
one team's win total into a rating in isolation without knowing everyone
else's rating too. The schedule itself is also randomized per trial
(standings_sim.build_synthetic_schedule), not a fixed round robin, so there
isn't even a fixed "strength of schedule" to solve algebraically against.

Instead of deriving a formula, calibrate_ratings() iteratively adjusts all
30 ratings together: simulate many seasons with the CURRENT rating guesses,
measure each team's average simulated win total, nudge each team's rating
toward its market target based on the gap, and repeat until simulated win
totals match the market lines within a small tolerance. This is the
standard way to fit a Bradley-Terry/Elo-style model to target win totals
when the outcomes are jointly determined by a whole population of ratings.

initial_rating_guess() provides a fast closed-form starting point (treating
every opponent as exactly league-average, i.e. ignoring strength of
schedule) so the iteration starts in the right neighborhood and converges
in a reasonable number of trials rather than starting from a flat 1500 for
every team.

ACCURACY CAVEAT: 30 ratings are being fit jointly to 30 targets using a
stochastic simulator, so exact convergence isn't guaranteed and the
schedule's own trial-to-trial randomness sets a floor on precision no
amount of iteration removes. calibrate_ratings() reports the max remaining
error and should be checked before trusting the output for anything
precision-sensitive.
"""

import math
import random
from typing import Dict, List, Optional, Sequence

from standings_sim import Team, simulate_season

LEAGUE_AVERAGE_ELO = 1500.0
GAMES_PER_SEASON = 82


def load_market_win_totals(xlsx_path: str) -> Dict[str, float]:
    """
    Loads a spreadsheet shaped like the one this project was given: column
    A = team name (matching the full names used elsewhere in this
    pipeline, e.g. "Boston Celtics"), remaining columns = each sportsbook's
    win-total O/U line. Returns {team_name: average_line_across_books}.
    """
    import openpyxl

    wb = openpyxl.load_workbook(xlsx_path, data_only=True)
    ws = wb.active
    totals: Dict[str, float] = {}
    for row in ws.iter_rows(min_row=2, values_only=True):
        if not row or row[0] is None:
            continue
        team = str(row[0]).strip()
        lines = [float(v) for v in row[1:] if isinstance(v, (int, float))]
        if not lines:
            continue
        totals[team] = sum(lines) / len(lines)
    return totals


def initial_rating_guess(win_total: float, games: int = GAMES_PER_SEASON) -> float:
    """
    Closed-form starting point ONLY (not the final calibrated rating) --
    converts a win percentage into an Elo-style rating via the standard
    logistic inverse, treating every opponent as exactly league-average
    (1500). This ignores strength of schedule entirely (a team with a
    projected 55-27 record against a murderers' row of contenders and a
    team with the same record against a weak slate get the same starting
    guess here) -- calibrate_ratings() corrects for that afterward.
    """
    win_pct = min(max(win_total / games, 0.02), 0.98)  # clamp away from 0/1 (logit undefined there)
    return LEAGUE_AVERAGE_ELO + 400.0 * math.log10(win_pct / (1 - win_pct))


def calibrate_ratings(win_totals: Dict[str, float],
                       iterations: int = 30,
                       trials_per_iteration: int = 400,
                       learning_rate: float = 6.0,
                       tolerance: float = 0.15,
                       seed: Optional[int] = None,
                       verbose: bool = False) -> Dict[str, float]:
    """
    Returns {team_name: calibrated_rating}. See module docstring for the
    method. `tolerance` is the max-abs-win-error (in wins over an 82-game
    season) at which iteration stops early; `learning_rate` is how many
    Elo points to move a team's rating per 1 win of remaining error per
    iteration -- too high oscillates, too low converges slowly. Values
    above are tuned by trial against this project's actual market data
    (see market_ratings.py's __main__ block); if convergence stalls or
    oscillates for a different win-total distribution, lower learning_rate
    and raise iterations.
    """
    names = list(win_totals.keys())
    ratings = {n: initial_rating_guess(win_totals[n]) for n in names}
    rng = random.Random(seed)

    for it in range(iterations):
        teams = [Team(name=n, rating=ratings[n]) for n in names]
        totals = {n: 0.0 for n in names}
        for _ in range(trials_per_iteration):
            wins = simulate_season(teams, rng=rng, games_per_team=GAMES_PER_SEASON)
            for n in names:
                totals[n] += wins[n]
        avg_wins = {n: totals[n] / trials_per_iteration for n in names}

        max_err = 0.0
        for n in names:
            err = win_totals[n] - avg_wins[n]
            max_err = max(max_err, abs(err))
            ratings[n] += learning_rate * err

        if verbose:
            worst = max(names, key=lambda n: abs(win_totals[n] - avg_wins[n]))
            print(f"  iter {it + 1:>2}: max abs win error = {max_err:5.2f}  "
                  f"(worst: {worst}, target {win_totals[worst]:.1f}, sim {avg_wins[worst]:.1f})")

        if max_err < tolerance:
            if verbose:
                print(f"  converged after {it + 1} iterations")
            break

    return ratings


def build_calibrated_teams(win_totals: Dict[str, float], conferences: Dict[str, str],
                            **calibrate_kwargs) -> List[Team]:
    """Convenience wrapper: calibrate ratings and return ready-to-use Team objects with conferences attached."""
    ratings = calibrate_ratings(win_totals, **calibrate_kwargs)
    missing_conf = set(win_totals) - set(conferences)
    if missing_conf:
        raise KeyError(f"No conference assignment for: {sorted(missing_conf)}")
    return [Team(name=n, rating=ratings[n], conference=conferences[n]) for n in win_totals]


if __name__ == "__main__":
    import os
    import sys

    from data_paths import find_data_file

    _default_xlsx = find_data_file("market_win_totals.xlsx", os.path.dirname(os.path.abspath(__file__)))
    xlsx_path = sys.argv[1] if len(sys.argv) > 1 else _default_xlsx
    win_totals = load_market_win_totals(xlsx_path)
    print(f"Loaded {len(win_totals)} teams' market win totals from {xlsx_path}")

    print("\nCalibrating ratings (this runs several hundred simulated seasons per iteration)...")
    ratings = calibrate_ratings(win_totals, seed=11, verbose=True)

    # Final validation pass: simulate a large batch with the calibrated
    # ratings and compare average wins against the market targets directly,
    # independent of the calibration loop itself.
    print("\n=== Final validation: 2000 simulated seasons vs. market win totals ===")
    from standings_sim import Team as _Team
    teams = [_Team(name=n, rating=ratings[n]) for n in win_totals]
    rng = random.Random(99)
    totals = {n: 0.0 for n in win_totals}
    TRIALS = 2000
    for _ in range(TRIALS):
        wins = simulate_season(teams, rng=rng, games_per_team=GAMES_PER_SEASON)
        for n in win_totals:
            totals[n] += wins[n]
    avg_wins = {n: totals[n] / TRIALS for n in win_totals}

    rows = sorted(win_totals.items(), key=lambda kv: -kv[1])
    print(f"{'Team':<28}{'Market':>8}{'Simulated':>11}{'Rating':>9}{'Error':>8}")
    max_err = 0.0
    sum_abs_err = 0.0
    for name, target in rows:
        sim = avg_wins[name]
        err = sim - target
        max_err = max(max_err, abs(err))
        sum_abs_err += abs(err)
        print(f"{name:<28}{target:>8.1f}{sim:>11.2f}{ratings[name]:>9.1f}{err:>+8.2f}")
    print(f"\nMean abs error: {sum_abs_err/len(win_totals):.3f} wins  |  Max abs error: {max_err:.3f} wins")
    total_market = sum(win_totals.values())
    total_sim = sum(avg_wins.values())
    print(f"League total wins -- market: {total_market:.1f}, simulated: {total_sim:.1f} "
          f"(should both be {30*GAMES_PER_SEASON//2} since every game has exactly one winner)")
