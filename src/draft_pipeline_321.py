"""
End-to-end 2027+ pipeline: simulate a season, seed both conferences,
resolve the single 7-vs-8 play-in game, build the 3-2-1 ball pool, and draw
the full 30-team draft order.

Requires each Team to have a `conference` set ("East" or "West"), 15 teams
per conference.
"""

import random
from typing import Dict, List, Sequence

from standings_sim import Team, simulate_season, win_probability
from lottery_sim_321 import build_lottery_pool, simulate_321_lottery


def seed_conferences(teams: Sequence[Team], wins: Dict[str, int]) -> Dict[str, List[str]]:
    """Returns {"East": [team names, best record first, i.e. seed 1..15], "West": [...]}"""
    by_conf: Dict[str, List[str]] = {"East": [], "West": []}
    for t in teams:
        if t.conference not in ("East", "West"):
            raise ValueError(f"Team {t.name} needs conference set to 'East' or 'West'")
        by_conf[t.conference].append(t.name)

    for conf in by_conf:
        if len(by_conf[conf]) != 15:
            raise ValueError(f"{conf} has {len(by_conf[conf])} teams, expected 15")
        by_conf[conf].sort(key=lambda n: -wins[n])  # best record (seed 1) first

    return by_conf


def run_seven_eight_game(seed7: str, seed8: str, ratings: Dict[str, float],
                          rng: random.Random = random) -> Dict[str, str]:
    """
    Single win-or-go-home game; the 7 seed hosts. Returns {"winner": ..., "loser": ...}.
    Winner claims the conference's final playoff spot; loser is guaranteed
    one lottery ball under the 3-2-1 system.
    """
    p_seven = win_probability(ratings[seed7], ratings[seed8])
    if rng.random() < p_seven:
        return {"winner": seed7, "loser": seed8}
    return {"winner": seed8, "loser": seed7}


def simulate_321_draft(teams: Sequence[Team], rng: random.Random = random,
                        games_per_team: int = 82) -> Dict[str, int]:
    """
    Runs one full season + play-in + 3-2-1 lottery. Returns {team_name: pick_number}
    for all 30 teams (picks 1-16 via the lottery, 17-30 for the 14 playoff
    teams in inverse standings order).
    """
    ratings = {t.name: t.rating for t in teams}
    wins = simulate_season(teams, rng=rng, games_per_team=games_per_team)
    conf_seeds = seed_conferences(teams, wins)

    non_playoff_10: List[str] = []
    nine_ten_all: List[str] = []
    seven_eight_losers: List[str] = []
    playoff_14: List[str] = []

    for conf, seeds in conf_seeds.items():
        # seeds[0:6] = seeds 1-6, auto playoff
        playoff_14.extend(seeds[0:6])
        seed7, seed8, seed9, seed10 = seeds[6], seeds[7], seeds[8], seeds[9]
        result = run_seven_eight_game(seed7, seed8, ratings, rng=rng)
        playoff_14.append(result["winner"])
        seven_eight_losers.append(result["loser"])
        nine_ten_all.extend([seed9, seed10])
        non_playoff_10.extend(seeds[10:15])  # seeds 11-15

    pool = build_lottery_pool(non_playoff_10, wins, nine_ten_all, seven_eight_losers)
    lottery_picks = simulate_321_lottery(pool, rng=rng)  # picks 1-16

    # Picks 17-30: the 14 playoff teams, worst record first.
    playoff_ranked = sorted(playoff_14, key=lambda n: wins[n])
    picks: Dict[str, int] = dict(lottery_picks)
    for i, name in enumerate(playoff_ranked):
        picks[name] = NUM_LOTTERY_TEAMS_PLUS_ONE + i

    return picks


NUM_LOTTERY_TEAMS_PLUS_ONE = 17


def monte_carlo_321_pick_distribution(teams: Sequence[Team], trials: int = 5000,
                                       games_per_team: int = 82,
                                       seed: int = None) -> Dict[str, Dict[int, int]]:
    """Same shape as standings_sim.monte_carlo_pick_distribution, but for the 2027+ rules."""
    rng = random.Random(seed)
    counts: Dict[str, Dict[int, int]] = {
        t.name: {p: 0 for p in range(1, 31)} for t in teams
    }
    for _ in range(trials):
        picks = simulate_321_draft(teams, rng=rng, games_per_team=games_per_team)
        for name, pick in picks.items():
            counts[name][pick] += 1
    return counts
