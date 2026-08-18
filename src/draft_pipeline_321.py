"""
End-to-end 2027+ pipeline: simulate a season, seed both conferences,
resolve the single 7-vs-8 play-in game, build the 3-2-1 ball pool, and draw
the full 30-team draft order.

Requires each Team to have a `conference` set ("East" or "West"), 15 teams
per conference.
"""

import random
from typing import Dict, List, Optional, Sequence

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


def _simulate_321_draft_core(teams: Sequence[Team], rng: random.Random = random,
                              games_per_team: int = 82,
                              history: Optional[Dict[str, List[int]]] = None
                              ) -> "tuple[Dict[str, int], Dict[str, int]]":
    """
    Shared internals for one full season + play-in + 3-2-1 lottery.
    Returns (wins, first_round_picks) -- wins is exposed so
    simulate_321_draft_full() can derive the second round from the SAME
    simulated season rather than a fresh, uncorrelated one.

    `history`: optional pick-restrictions state (see
    pick_restrictions_321.py), e.g. pick_restrictions_321.DEFAULT_2027_HISTORY
    to simulate the 2027 draft under the real "no repeat #1 / no 3-straight
    top-5" restrictions seeded from actual 2025-2026 results. Omit for years
    without seeded/carried-forward history (restrictions are simply not
    enforced, matching pre-3-2-1 behavior).
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
    lottery_picks = simulate_321_lottery(pool, rng=rng, history=history)  # picks 1-16

    # Picks 17-30: the 14 playoff teams, worst record first.
    playoff_ranked = sorted(playoff_14, key=lambda n: wins[n])
    picks: Dict[str, int] = dict(lottery_picks)
    for i, name in enumerate(playoff_ranked):
        picks[name] = NUM_LOTTERY_TEAMS_PLUS_ONE + i

    return wins, picks


def simulate_321_draft(teams: Sequence[Team], rng: random.Random = random,
                        games_per_team: int = 82,
                        history: Optional[Dict[str, List[int]]] = None) -> Dict[str, int]:
    """
    Runs one full season + play-in + 3-2-1 lottery. Returns {team_name: pick_number}
    for all 30 teams (picks 1-16 via the lottery, 17-30 for the 14 playoff
    teams in inverse standings order). FIRST ROUND ONLY -- see
    simulate_321_draft_full() for both rounds. `history`: see
    _simulate_321_draft_core()'s docstring.
    """
    _, picks = _simulate_321_draft_core(teams, rng=rng, games_per_team=games_per_team, history=history)
    return picks


def simulate_second_round_order(wins: Dict[str, int], rng: random.Random = random) -> Dict[str, int]:
    """
    Second-round picks (31-60), given the SAME season's wins dict used for
    the first round. Real NBA mechanics: the lottery draw only reshuffles
    the FIRST round -- the second round is always a straight worst-record-
    first snake off the regular-season standings, no lottery involved. Ties
    broken randomly (pre-shuffle before the stable sort), same convention as
    standings_sim.wins_to_draft_order.
    """
    names = list(wins.keys())
    rng.shuffle(names)
    order = sorted(names, key=lambda n: wins[n])  # worst record = pick 31
    return {name: 31 + i for i, name in enumerate(order)}


def simulate_321_draft_full(teams: Sequence[Team], rng: random.Random = random,
                             games_per_team: int = 82,
                             history: Optional[Dict[str, List[int]]] = None) -> Dict[str, int]:
    """
    Full 60-pick draft order for one simulated season: picks 1-30 via the
    3-2-1 lottery mechanism, picks 31-60 via straight reverse-standings
    order (no lottery in round 2). Both rounds are derived from the SAME
    simulated season, so a team's first- and second-round outcomes stay
    correlated within a trial -- needed for swap_resolver.py, since some
    swap language spans both rounds' picks for the same team pair.
    `history`: see _simulate_321_draft_core()'s docstring; pick restrictions
    only ever affect first-round slots 1-5, never the second round.
    """
    wins, first_round = _simulate_321_draft_core(teams, rng=rng, games_per_team=games_per_team, history=history)
    second_round = simulate_second_round_order(wins, rng=rng)
    return {**first_round, **second_round}


NUM_LOTTERY_TEAMS_PLUS_ONE = 17


def monte_carlo_321_pick_distribution(teams: Sequence[Team], trials: int = 5000,
                                       games_per_team: int = 82,
                                       seed: int = None,
                                       history: Optional[Dict[str, List[int]]] = None
                                       ) -> Dict[str, Dict[int, int]]:
    """Same shape as standings_sim.monte_carlo_pick_distribution, but for the 2027+ rules.
    `history`: see _simulate_321_draft_core()'s docstring; omit for old behavior."""
    rng = random.Random(seed)
    counts: Dict[str, Dict[int, int]] = {
        t.name: {p: 0 for p in range(1, 31)} for t in teams
    }
    for _ in range(trials):
        picks = simulate_321_draft(teams, rng=rng, games_per_team=games_per_team, history=history)
        for name, pick in picks.items():
            counts[name][pick] += 1
    return counts


def joint_pick_number_trials(teams: Sequence[Team], team_names_of_interest: Sequence[str],
                              trials: int = 5000, games_per_team: int = 82,
                              seed: int = None,
                              history: Optional[Dict[str, List[int]]] = None
                              ) -> Dict[str, Dict[str, List[int]]]:
    """
    Like monte_carlo_321_pick_distribution, but returns per-trial pick
    numbers for a SPECIFIC subset of teams instead of aggregated counts for
    everyone -- and critically, preserves the trial-to-trial CORRELATION
    between those teams' outcomes, since every team's list at index i comes
    from the exact same simulated season (same schedule draw, same lottery
    draw). This is what swap_resolver.py needs: "Team A's less-favorable of
    (A, B)'s picks" has to compare A and B's picks from the SAME season, not
    their independent marginal distributions -- their records aren't
    independent (shared conference, overlapping schedules, etc.), and the
    swap comparison itself is a per-trial operation.

    Only tracks the requested teams (not the full 30) to keep memory low
    when this is called many times for different swap groups.

    Every team has BOTH a first-round slot (1-30) and a second-round slot
    (31-60) EVERY season -- they're different numbers for the same team, so
    they can't be merged into one {team: pick_number} mapping (an earlier
    version of this function did exactly that via
    simulate_321_draft_full()'s {**first_round, **second_round} merge, which
    silently discarded every team's first-round result since both dicts
    share the same team-name keys -- second_round always won the merge).
    Returns {team_name: {"1st": [pick_trial_0, ...], "2nd": [pick_trial_0, ...]}}
    instead, so callers can select the round a given pick fragment actually
    needs.
    """
    names_of_interest = list(team_names_of_interest)
    all_names = {t.name for t in teams}
    missing = [n for n in names_of_interest if n not in all_names]
    if missing:
        raise KeyError(f"Team(s) not found in league: {missing}")

    rng = random.Random(seed)
    results: Dict[str, Dict[str, List[int]]] = {n: {"1st": [], "2nd": []} for n in names_of_interest}
    for _ in range(trials):
        wins, first_round = _simulate_321_draft_core(teams, rng=rng, games_per_team=games_per_team, history=history)
        second_round = simulate_second_round_order(wins, rng=rng)
        for n in names_of_interest:
            results[n]["1st"].append(first_round[n])
            results[n]["2nd"].append(second_round[n])
    return results
