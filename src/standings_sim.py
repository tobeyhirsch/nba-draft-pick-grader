"""
Monte Carlo season simulation.

Given a "true talent" rating per team, simulates an 82-game season many times
to produce a distribution over final standings -- and, chained with
lottery_sim, a distribution over where each team's draft pick actually lands.

Deliberately simplified for a first pass:
  - Ratings are Elo-style point-differential proxies. The live pipeline
    (run_real_league.py) sources them from market_ratings.py (consensus
    sportsbook win totals, calibrated) rather than a bottom-up roster sum --
    this module doesn't care where the ratings come from.
  - The schedule is a synthetic balanced round-robin rather than the real
    fixture list. Swap in the actual schedule CSV for production use.
  - Game outcomes use a standard logistic (Bradley-Terry) win probability
    from the rating gap, plus a home-court adjustment.
  - Real NBA win totals have some extra-binomial variance beyond pure
    game-by-game randomness (schedule luck, injury streaks, etc.). This
    version doesn't inject that yet -- a reasonable v2 addition is a small
    per-team Gaussian "luck" term added to the rating each trial.

NOTE: this module used to also provide monte_carlo_pick_distribution() /
wins_to_draft_order(), built on the pre-2027 lottery (lottery_sim.py).
Removed as dead code -- the live pipeline runs entirely on 2027+ "3-2-1"
draft years now, via draft_pipeline_321.py's equivalents
(monte_carlo_321_pick_distribution() / simulate_second_round_order()).
"""

import random
from dataclasses import dataclass
from typing import Dict, List, Sequence, Tuple


@dataclass
class Team:
    name: str
    rating: float  # Elo-like scale, ~1500 = league average
    conference: str = None  # "East" / "West" -- only required for the 3-2-1 (2027+) lottery


HOME_COURT_ELO = 60.0  # roughly +3 points of home-court advantage


def win_probability(rating_home: float, rating_away: float) -> float:
    """Bradley-Terry / logistic win probability for the home team."""
    diff = (rating_home + HOME_COURT_ELO) - rating_away
    return 1.0 / (1.0 + 10 ** (-diff / 400.0))


def build_synthetic_schedule(team_names: Sequence[str], games_per_team: int = 82,
                              rng: random.Random = random) -> List[Tuple[str, str]]:
    """
    Builds an approximately balanced schedule: every team ends up with
    `games_per_team` games total, opponents assigned via random pairing.
    Replace with a real schedule for production use -- the simulator only
    needs a list of (home, away) tuples.
    """
    n = len(team_names)
    total_slots = n * games_per_team
    if total_slots % 2 != 0:
        raise ValueError("team_count * games_per_team must be even")

    slots: List[str] = []
    for name in team_names:
        slots.extend([name] * games_per_team)
    rng.shuffle(slots)

    games: List[Tuple[str, str]] = []
    while slots:
        a = slots.pop()
        paired = False
        for i in range(len(slots) - 1, -1, -1):
            if slots[i] != a:
                b = slots.pop(i)
                if rng.random() < 0.5:
                    games.append((a, b))
                else:
                    games.append((b, a))
                paired = True
                break
        if not paired:
            # Leftover team with no valid opponent left (rare edge case) -- drop it.
            continue

    return games


def simulate_season(teams: Sequence[Team], rng: random.Random = random,
                     games_per_team: int = 82) -> Dict[str, int]:
    """Runs one simulated season, returns {team_name: wins}."""
    ratings = {t.name: t.rating for t in teams}
    names = [t.name for t in teams]
    schedule = build_synthetic_schedule(names, games_per_team=games_per_team, rng=rng)

    wins = {name: 0 for name in names}
    for home, away in schedule:
        p_home = win_probability(ratings[home], ratings[away])
        if rng.random() < p_home:
            wins[home] += 1
        else:
            wins[away] += 1

    return wins
