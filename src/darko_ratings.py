"""
Builds team-strength ratings from real DARKO player data -- the DPM
leaderboard (skill) and career longevity projections (presence) -- and
calibrates them against market_ratings.py's market-implied ratings for the
CURRENT season, so this module's actual job is the gap market data can't
fill: how a team's strength evolves in FUTURE seasons the market hasn't
priced yet (see market_ratings.py's docstring for why market data, not a
DARKO sum, is used as-is for the current season -- that reasoning is
unchanged here).

DATA (both user-supplied, verified to share the exact same 530-player
universe -- identical (Player, Team) keys in both files, no fuzzy name
matching needed):
  darkodpmleaderboard.csv     -- DPM (ODPM+DDPM, a per-100-possession
                                  plus-minus rating) and MPG (season-long
                                  projected minutes/game) per active player.
  darkolongevityprojections.csv -- 0-100 "still an NBA player" probability
                                  per player at +1 through +15 years out.

CHAIN:

1. A team's CURRENT net rating is the MPG-weighted average DPM across its
   roster -- the same approach this project's now-deleted team_wins.py
   used (see that file's history in this project for why it was cut: a
   flat DARKO sum was a worse fit than the market line for the CURRENT
   season specifically). All of team_wins.py's caveats still apply: DARKO
   additivity ignores lineup fit, and a player's DARKO partly reflects
   their ACTUAL current role, so it's an approximation to begin with.

2. Fit a linear regression of market_ratings.py's calibrated Elo (ground
   truth for the season that's about to happen) against each team's
   CURRENT DARKO net rating. This replaces team_wins.py's old fixed,
   never-validated "28 Elo points per point of margin" constant with a
   real fitted conversion. The fit's r^2 is the honest answer to "does
   DARKO rank teams the way the real market does" -- run this file's
   __main__ and read it before trusting anything downstream.

3. For a FUTURE season (offset = 1..5 years out -- the 2028 through 2032
   drafts; see WINDOW below for why it stops at 5), recompute the same
   weighted DPM sum but multiply every player's term by their longevity
   probability at that offset. The denominator stays fixed at the team's
   CURRENT total MPG (not the shrinking survivor total) -- a retiring
   player's vacated minutes are modeled as going to a REPLACEMENT-LEVEL
   (0 DPM, i.e. league-average) player, not silently redistributed onto
   the teammates who remain (which would flatter a team for losing
   players). This is a named assumption, not a fit: nothing in the
   supplied data says who actually replaces a retiring player's minutes
   (a rookie, a trade target, in-house development), so replacement level
   is the least presumptuous stand-in.

4. Run that future net rating back through the SAME slope/intercept from
   step 2 to get a future Elo rating, ready for standings_sim.Team /
   draft_pipeline_321's simulator.

WHY THE WINDOW STOPS AT +5 (2028-2032 drafts), NOT +15:
This model can only ever go flat or DOWN over time, never up -- every
retiring player's minutes get replaced with a 0-DPM stand-in, never a
rookie who develops into someone better, a trade addition, or a free-agent
signing. That's a fine approximation for a few years (most rosters don't
turn over that fast) but compounds into an obviously wrong "every team
converges toward replacement level" shape by year 10+. Capped here at
MAX_OFFSET=5 for that reason; the raw longevity file goes out to +15 if a
future revision of this module wants to extend the window (it would need a
counterbalancing "new talent enters the league" term first, which no
supplied data source currently covers).

WHAT ELSE THIS DOES NOT MODEL:
  - Skill trajectories for players who DON'T leave. A player projected to
    still be active at offset +5 is scored at their CURRENT DPM, not an
    age-adjusted one -- the longevity file gives presence, not future
    skill level, and no aging-curve data was supplied.
  - Trades, free agency, or draft picks converting into new rostered
    players. This is today's roster projected forward with attrition only.
"""

import csv
import os
from dataclasses import dataclass
from typing import Dict, List, Optional, Sequence, Tuple

import numpy as np

from standings_sim import Team
from data_paths import find_data_file

DPM_CSV = find_data_file("darkodpmleaderboard.csv", os.path.dirname(os.path.abspath(__file__)))
LONGEVITY_CSV = find_data_file("darkolongevityprojections.csv", os.path.dirname(os.path.abspath(__file__)))

MAX_OFFSET = 5  # see "WHY THE WINDOW STOPS AT +5" above
FIRST_DRAFT_YEAR_COVERED = 2028  # offset 1; the 2027 draft uses market_ratings.py's teams directly, no offset 0 here


@dataclass
class DarkoPlayer:
    name: str
    team: str
    dpm: float
    mpg: float
    longevity_by_offset: Dict[int, float]  # offsets 1..15 -> 0-100

    def presence(self, offset: int) -> float:
        """1.0 "here today" at offset 0; longevity fraction (0.0-1.0) beyond that."""
        if offset <= 0:
            return 1.0
        pct = self.longevity_by_offset.get(offset)
        return 0.0 if pct is None else pct / 100.0


def _parse_dpm(value: str) -> float:
    return float(value.replace("+", ""))


def load_darko_players(dpm_csv: str = DPM_CSV, longevity_csv: str = LONGEVITY_CSV) -> List[DarkoPlayer]:
    with open(dpm_csv, encoding="utf-8-sig") as f:
        dpm_rows = {(r["Player"], r["Team"]): r for r in csv.DictReader(f)}
    with open(longevity_csv, encoding="utf-8-sig") as f:
        lon_rows = {(r["Player"], r["Team"]): r for r in csv.DictReader(f)}

    missing = sorted(set(dpm_rows) - set(lon_rows))
    if missing:
        raise ValueError(
            f"{len(missing)} player(s) in the DPM leaderboard have no matching row in the "
            f"longevity file (name/team mismatch between the two files): {missing[:10]}"
            + (" ..." if len(missing) > 10 else "")
        )

    players = []
    for key, drow in dpm_rows.items():
        lrow = lon_rows[key]
        longevity = {i: float(lrow[f"+{i}"]) for i in range(1, 16)}
        players.append(DarkoPlayer(
            name=drow["Player"],
            team=drow["Team"],
            dpm=_parse_dpm(drow["DPM"]),
            mpg=float(drow["MPG"]),
            longevity_by_offset=longevity,
        ))
    return players


def _group_by_team(players: Sequence[DarkoPlayer]) -> Dict[str, List[DarkoPlayer]]:
    by_team: Dict[str, List[DarkoPlayer]] = {}
    for p in players:
        by_team.setdefault(p.team, []).append(p)
    return by_team


def team_net_rating(team_players: Sequence[DarkoPlayer], offset: int = 0) -> float:
    """
    MPG-weighted average DPM at `offset` years from now (0 = current
    roster, no decay). Denominator is fixed at the team's CURRENT total
    MPG regardless of offset -- see module docstring step 3 for why
    (departed minutes count as replacement level, not redistributed).
    """
    baseline_total_mpg = sum(p.mpg for p in team_players)
    if baseline_total_mpg <= 0:
        raise ValueError("Team has zero total MPG in the DARKO leaderboard -- can't rate it")
    weighted = sum(p.dpm * p.mpg * p.presence(offset) for p in team_players)
    return weighted / baseline_total_mpg


def all_teams_net_ratings(players: Sequence[DarkoPlayer], offset: int = 0) -> Dict[str, float]:
    return {team: team_net_rating(team_players, offset) for team, team_players in _group_by_team(players).items()}


def fit_darko_to_elo(darko_ratings: Dict[str, float], market_elo: Dict[str, float]) -> Tuple[float, float, float]:
    """
    Linear regression: market_elo ~ slope * darko_rating + intercept,
    fit across every team both dicts have in common. Returns (slope,
    intercept, r_squared) -- ALWAYS check r_squared (see module docstring
    step 2) before trusting anything built from this fit.
    """
    common = sorted(set(darko_ratings) & set(market_elo))
    if len(common) < 2:
        raise ValueError("Need at least 2 teams in common to fit a regression")
    x = np.array([darko_ratings[t] for t in common])
    y = np.array([market_elo[t] for t in common])
    slope, intercept = np.polyfit(x, y, 1)
    pred = slope * x + intercept
    ss_res = float(np.sum((y - pred) ** 2))
    ss_tot = float(np.sum((y - y.mean()) ** 2))
    r_squared = 1 - ss_res / ss_tot if ss_tot > 0 else float("nan")
    return float(slope), float(intercept), r_squared


def darko_elo(darko_rating: float, slope: float, intercept: float) -> float:
    return slope * darko_rating + intercept


def future_year_teams(players: Sequence[DarkoPlayer], offset: int, slope: float, intercept: float,
                       conferences: Dict[str, str]) -> List[Team]:
    """
    Team list for `offset` years from now (1..MAX_OFFSET), using this
    module's DARKO+longevity-evolved net rating run through the SAME
    market-fitted slope/intercept from fit_darko_to_elo().
    """
    if not (1 <= offset <= MAX_OFFSET):
        raise ValueError(f"offset must be 1-{MAX_OFFSET} (near-term window only, see module docstring)")
    ratings = all_teams_net_ratings(players, offset=offset)
    missing_conf = set(ratings) - set(conferences)
    if missing_conf:
        raise KeyError(f"No conference assignment for: {sorted(missing_conf)}")
    return [Team(name=t, rating=darko_elo(r, slope, intercept), conference=conferences[t])
            for t, r in ratings.items()]


if __name__ == "__main__":
    from conferences import TEAM_CONFERENCE
    from market_ratings import load_market_win_totals, calibrate_ratings

    market_xlsx = find_data_file("market_win_totals.xlsx", os.path.dirname(os.path.abspath(__file__)))
    win_totals = load_market_win_totals(market_xlsx)
    print(f"Loaded {len(win_totals)} teams' market win totals from {market_xlsx}")

    print("Calibrating market ratings (ground truth for the CURRENT season)...")
    market_elo = calibrate_ratings(win_totals, seed=11, trials_per_iteration=400, iterations=30)

    players = load_darko_players()
    print(f"Loaded {len(players)} players from the DARKO leaderboard "
          f"(joined against longevity projections, {len(set(p.team for p in players))} teams)")

    darko_now = all_teams_net_ratings(players, offset=0)
    slope, intercept, r2 = fit_darko_to_elo(darko_now, market_elo)
    print(f"\nDARKO net-rating -> market Elo fit: elo = {slope:.2f} * darko + {intercept:.1f}")
    print(f"r^2 = {r2:.3f} (how well CURRENT-season DARKO rank-orders teams the way the real market does)")

    print(f"\n{'Team':<28}{'DARKO net':>10}{'DARKO-implied Elo':>19}{'Market Elo':>12}{'Residual':>10}")
    rows = []
    for team in sorted(darko_now, key=lambda t: -darko_now[t]):
        implied = darko_elo(darko_now[team], slope, intercept)
        actual = market_elo[team]
        rows.append((team, darko_now[team], implied, actual, implied - actual))
    for team, dnet, implied, actual, resid in rows:
        print(f"{team:<28}{dnet:>10.2f}{implied:>19.1f}{actual:>12.1f}{resid:>+10.1f}")

    print(f"\n--- Projected DARKO-implied Elo drift, current vs. +{MAX_OFFSET} years "
          f"(the {FIRST_DRAFT_YEAR_COVERED} vs. {FIRST_DRAFT_YEAR_COVERED + MAX_OFFSET - 1} draft-feeding seasons) ---")
    darko_future = all_teams_net_ratings(players, offset=MAX_OFFSET)
    drift_rows = []
    for team in darko_now:
        now_elo = darko_elo(darko_now[team], slope, intercept)
        future_elo = darko_elo(darko_future[team], slope, intercept)
        drift_rows.append((team, now_elo, future_elo, future_elo - now_elo))
    drift_rows.sort(key=lambda r: r[3])  # biggest decline first
    print(f"{'Team':<28}{'Elo now':>10}{f'Elo +{MAX_OFFSET}y':>10}{'Drift':>10}")
    for team, now_elo, future_elo, drift in drift_rows:
        print(f"{team:<28}{now_elo:>10.1f}{future_elo:>10.1f}{drift:>+10.1f}")
