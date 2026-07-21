"""
NBA "3-2-1 Lottery" ball mechanics, effective the 2027-2029 NBA Drafts.

Source: https://www.nba.com/news/nba-board-governors-approve-new-draft-lottery-system

Rules implemented here:
  - 16 teams enter the lottery (up from 14 under the pre-2027 format):
      * 10 teams that miss both the playoffs and the play-in (seeds 11-15 in
        each conference) get 3 balls each -- EXCEPT the 3 worst records
        league-wide among this group of 10 are "draft relegated" to 2 balls.
      * The No. 9 and No. 10 seed in each conference (4 teams total) get 2
        balls each.
      * The loser of each conference's 7-vs-8 play-in game (2 teams total)
        gets 1 ball.
    Total: 7*3 + 3*2 + 4*2 + 2*1 = 37 balls across 16 teams -- matches the
    widely reported ball count for this system.
  - All 16 picks (not just the top 4, unlike the pre-2027 format) are
    determined by the ball drawing, subject to floor protections:
      * Relegated (bottom-3-record) teams cannot fall below pick 12.
      * Every other lottery team's floor is pick 16, which is automatically
        satisfied since there are only 16 lottery slots.

INTERPRETATION NOTE -- the play-in format assumed here:
  Multiple secondary reports describe "four 9/10 seeds" and "two 7/8 losers"
  as fixed counts (not "however many end up eliminated"), which only
  reconciles to a clean 16-team / 37-ball total if the reformed play-in
  works like this: seeds 9 and 10 in each conference are guaranteed lottery
  entrants regardless of any game they play (they no longer have a
  realistic path to the playoffs -- this is the actual anti-tanking lever,
  since it removes any incentive to angle for the 9/10 seed rather than
  climb into the top 6). The only game that still decides a playoff spot is
  a single 7-vs-8 matchup: winner gets the conference's final playoff berth,
  loser is guaranteed one lottery ball. That gives a 14-team playoff field
  (7 per conference) and a 16-team lottery field, which is what's
  documented. This is treated as an explicit assumption pending the
  league's full rulebook language, and is easy to swap out if a more
  precise structure is published later.

NOT modeled here (out of scope for a single-season lottery draw):
  - Multi-year pick restrictions (no team's own pick can be #1 overall in
    consecutive drafts, or a top-5 pick in 3 consecutive drafts) -- this
    needs draft-history state carried across simulated seasons.
  - The ban on top-12-through-15 protections on newly traded picks -- that's
    a cap-sheet / pick-ownership rule, not part of the draw mechanics.
  - The league's expanded disciplinary authority to adjust odds/positions.
"""

import random
from typing import Dict, List, NamedTuple, Sequence


class LotteryEntrant(NamedTuple):
    name: str
    balls: int
    floor_pick: int  # worst possible pick number for this team


NUM_LOTTERY_TEAMS = 16
RELEGATION_FLOOR = 12
DEFAULT_FLOOR = 16


def build_lottery_pool(non_playoff_seeds_11_to_15: Sequence[str],
                        team_wins: Dict[str, int],
                        seed_9_and_10_per_conference: Sequence[str],
                        seven_eight_losers: Sequence[str]) -> List[LotteryEntrant]:
    """
    Assembles the 16-team, ball-weighted lottery pool for one season.

    non_playoff_seeds_11_to_15: the 10 teams (5 per conference) that missed
        both the playoffs and the play-in.
    team_wins: wins dict covering at least those 10 teams, used to find the
        3 worst records for relegation.
    seed_9_and_10_per_conference: the 4 teams (2 per conference) seeded 9th
        or 10th in their conference.
    seven_eight_losers: the 2 teams (1 per conference) that lost their
        conference's 7-vs-8 play-in game.
    """
    if len(non_playoff_seeds_11_to_15) != 10:
        raise ValueError("Expected 10 non-playoff/non-play-in teams (5 per conference)")
    if len(seed_9_and_10_per_conference) != 4:
        raise ValueError("Expected 4 teams seeded 9 or 10 (2 per conference)")
    if len(seven_eight_losers) != 2:
        raise ValueError("Expected 2 losers of the 7-vs-8 play-in game (1 per conference)")

    relegated = set(sorted(non_playoff_seeds_11_to_15, key=lambda n: team_wins[n])[:3])

    pool: List[LotteryEntrant] = []
    for name in non_playoff_seeds_11_to_15:
        if name in relegated:
            pool.append(LotteryEntrant(name, balls=2, floor_pick=RELEGATION_FLOOR))
        else:
            pool.append(LotteryEntrant(name, balls=3, floor_pick=DEFAULT_FLOOR))
    for name in seed_9_and_10_per_conference:
        pool.append(LotteryEntrant(name, balls=2, floor_pick=DEFAULT_FLOOR))
    for name in seven_eight_losers:
        pool.append(LotteryEntrant(name, balls=1, floor_pick=DEFAULT_FLOOR))

    assert len(pool) == NUM_LOTTERY_TEAMS
    assert sum(e.balls for e in pool) == 37
    return pool


def _draw_unconstrained_order(pool: Sequence[LotteryEntrant], rng: random.Random) -> List[str]:
    """
    Sequential weighted draw without replacement (no floor protections
    applied yet) -- this is the same mechanic used in the pre-2027 top-4
    draw, just extended across all 16 slots.
    """
    names = [e.name for e in pool]
    weights = [e.balls for e in pool]
    order: List[str] = []
    for _ in range(len(names)):
        pick = rng.choices(names, weights=weights, k=1)[0]
        idx = names.index(pick)
        order.append(pick)
        names.pop(idx)
        weights.pop(idx)
    return order


def draw_321_order(pool: Sequence[LotteryEntrant], rng: random.Random = random) -> List[str]:
    """
    Runs the full 16-pick weighted draw, then applies floor protections.

    Algorithm: draw an unconstrained order, then rebuild it slot by slot.
    At each slot, check every distinct floor value still owed among
    unplaced teams (earliest-deadline-first feasibility check): if the
    count of teams due by some floor F exceeds the number of slots left
    before F, one of them must be forced into the current slot instead of
    waiting. This generalizes to any number of simultaneous protections,
    though today's rules only use one nontrivial floor (12, for relegated
    teams).
    """
    unconstrained = _draw_unconstrained_order(pool, rng)
    floor_by_team = {e.name: e.floor_pick for e in pool}
    remaining = list(unconstrained)
    final_order: List[str] = []
    n = len(pool)

    for slot in range(1, n + 1):
        forced = None
        distinct_floors = sorted(set(floor_by_team[t] for t in remaining))
        for floor in distinct_floors:
            due = [t for t in remaining if floor_by_team[t] <= floor]
            rooms_left_if_skipped = floor - slot
            if len(due) > rooms_left_if_skipped:
                forced = min(due, key=lambda t: unconstrained.index(t))
                break
        chosen = forced if forced is not None else remaining[0]
        final_order.append(chosen)
        remaining.remove(chosen)

    return final_order


def simulate_321_lottery(pool: Sequence[LotteryEntrant],
                          rng: random.Random = random) -> Dict[str, int]:
    """Returns {team_name: pick_number} for the 16 lottery teams (picks 1-16)."""
    order = draw_321_order(pool, rng=rng)
    return {name: i + 1 for i, name in enumerate(order)}


if __name__ == "__main__":
    # Sanity checks:
    #   1. Relegated teams should never be assigned worse than pick 12.
    #   2. Pick-1 odds should roughly track ball share (2/37 ~= 5.4% for a
    #      relegated team, 3/37 ~= 8.1% for a mid-lottery team).
    r = random.Random(11)
    mid_teams = [f"Mid{i}" for i in range(7)]
    relegated_teams = [f"Releg{i}" for i in range(3)]
    non_playoff_10 = mid_teams + relegated_teams
    wins = {t: 30 for t in mid_teams}
    wins.update({t: 15 for t in relegated_teams})  # relegated = worse record
    nine_ten = [f"NineTen{i}" for i in range(4)]
    seven_eight = [f"SevenEight{i}" for i in range(2)]

    trials = 20000
    worst_floor_violations = 0
    pick1_counts = {name: 0 for name in non_playoff_10 + nine_ten + seven_eight}

    for _ in range(trials):
        pool = build_lottery_pool(non_playoff_10, wins, nine_ten, seven_eight)
        picks = simulate_321_lottery(pool, rng=r)
        for t in relegated_teams:
            if picks[t] > RELEGATION_FLOOR:
                worst_floor_violations += 1
        for name, p in picks.items():
            if p == 1:
                pick1_counts[name] += 1

    print(f"Floor violations (should be 0): {worst_floor_violations}")
    print(f"Relegated team pick-1 rate (expect ~{2/37*100:.1f}%): "
          f"{pick1_counts[relegated_teams[0]]/trials*100:.2f}%")
    print(f"Mid-lottery team pick-1 rate (expect ~{3/37*100:.1f}%): "
          f"{pick1_counts[mid_teams[0]]/trials*100:.2f}%")
