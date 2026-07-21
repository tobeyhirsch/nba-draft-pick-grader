"""
NBA Draft Lottery simulation (2019-present format).

Mechanism:
  - The 14 non-playoff teams enter the lottery, seeded 1 (worst record) to 14
    (best record among the non-playoff teams).
  - Each seed is assigned a fixed share of the 1,000 possible four-ball
    combinations (see LOTTERY_COMBOS below).
  - Four separate drawings determine picks 1, 2, 3, and 4. A team can only be
    drawn once -- in the real lottery, combinations belonging to a team that
    already won a pick are discarded and redrawn. That process is
    mathematically identical to sampling without replacement, where each
    remaining team's weight is its combo count and the pool is renormalized
    after each draw. That's what draw_top_four() does.
  - Picks 5-14 go to the remaining lottery teams in inverse order of
    regular-season record (no further randomness).
  - Picks 15-30 go to the playoff teams in inverse order of regular-season
    record.

Note: this module does NOT model pick swaps, protections, or pick ownership
changes (e.g. "Team X's pick goes to Team Y unless it lands in the top 5").
That belongs in a separate "pick ownership" step once you're combining this
with the cap-sheet / trade-history layer -- keeping it separate here means
this module stays a pure, testable implementation of the actual lottery
mechanics.
"""

import random
from typing import Dict, List, Sequence

# Combinations out of 1,000, indexed by seed (0 = worst record, 13 = best
# record among the 14 lottery teams). This is the official flattened odds
# table adopted in 2019.
LOTTERY_COMBOS: List[int] = [140, 140, 140, 125, 105, 90, 75, 60, 45, 30, 20, 15, 10, 5]
assert sum(LOTTERY_COMBOS) == 1000

NUM_LOTTERY_TEAMS = 14
NUM_LOTTERY_PICKS = 4  # only picks 1-4 are actually drawn


def draw_top_four(lottery_team_names: Sequence[str], rng: random.Random = random) -> List[str]:
    """
    lottery_team_names: 14 team names ordered worst record (index 0) to best
                         record (index 13) among the non-playoff teams.

    Returns the 4 teams that win picks 1-4, in order.
    """
    if len(lottery_team_names) != NUM_LOTTERY_TEAMS:
        raise ValueError(
            f"Expected {NUM_LOTTERY_TEAMS} lottery teams, got {len(lottery_team_names)}"
        )

    remaining_names = list(lottery_team_names)
    remaining_weights = list(LOTTERY_COMBOS)
    winners = []

    for _ in range(NUM_LOTTERY_PICKS):
        pick = rng.choices(remaining_names, weights=remaining_weights, k=1)[0]
        idx = remaining_names.index(pick)
        winners.append(pick)
        remaining_names.pop(idx)
        remaining_weights.pop(idx)

    return winners


def simulate_lottery(draft_order_worst_to_best: Sequence[str],
                      rng: random.Random = random) -> Dict[str, int]:
    """
    draft_order_worst_to_best: ALL 30 teams, ordered from worst regular-season
                                record (pick 1 candidate) to best (pick 30
                                candidate) -- i.e. the 14 lottery teams
                                followed by the 16 playoff teams in
                                inverse-standings order.

    Returns {team_name: pick_number} for all 30 teams.
    """
    draft_order_worst_to_best = list(draft_order_worst_to_best)
    lottery_teams = draft_order_worst_to_best[:NUM_LOTTERY_TEAMS]
    non_lottery_teams = draft_order_worst_to_best[NUM_LOTTERY_TEAMS:]

    top_four = draw_top_four(lottery_teams, rng=rng)
    remaining_lottery = [t for t in lottery_teams if t not in top_four]

    picks: Dict[str, int] = {}
    for i, team in enumerate(top_four):
        picks[team] = i + 1
    for i, team in enumerate(remaining_lottery):
        picks[team] = NUM_LOTTERY_PICKS + 1 + i  # picks 5-14
    for i, team in enumerate(non_lottery_teams):
        picks[team] = NUM_LOTTERY_TEAMS + 1 + i  # picks 15-30

    return picks


if __name__ == "__main__":
    # Quick sanity check: with enough trials, seed 0 (worst record) should
    # win pick #1 about 14.0% of the time.
    demo_teams = [f"Seed{i+1}" for i in range(14)] + [f"Playoff{i+1}" for i in range(16)]
    trials = 20000
    pick1_wins = 0
    r = random.Random(7)
    for _ in range(trials):
        result = simulate_lottery(demo_teams, rng=r)
        if result["Seed1"] == 1:
            pick1_wins += 1
    print(f"Seed1 won pick #1 in {pick1_wins/trials*100:.2f}% of {trials} trials (expect ~14.0%)")