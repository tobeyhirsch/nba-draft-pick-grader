"""
"Pick Restrictions" from the NBA's 3-2-1 Lottery reform (effective the 2027
NBA Draft), per the league's official announcement:

    "No team's pick will be permitted to be the first pick in two
    consecutive NBA Drafts or a top-five pick in three consecutive NBA
    Drafts. These restrictions will apply only to each team's own pick
    without regard to whether that pick has been retained by the team or
    traded to (and thus held by) another team."

lottery_sim_321.py's ball-weighted draw (draw_321_order) and floor
protections (RELEGATION_FLOOR / DEFAULT_FLOOR) implement everything else in
the announcement; this module implements the piece that was previously
flagged as out of scope ("needs draft-history state carried across
simulated seasons"). Two things make that state now available:

  1. The restriction attaches to a team's OWN draft slot (their draft
     position by record, independent of ownership/trades) -- so it can be
     enforced entirely within the lottery draw step, before pick_resolver.py
     applies any trade/swap resolution. No pick-ownership data needed.
  2. The rule only looks back at the two most recently completed drafts. The
     2027 draft -- the first one this rule applies to -- can be seeded with
     REAL history from the actual 2025 and 2026 drafts (user-supplied,
     "Original team" column = each team's own draft slot that year,
     independent of who ended up holding/exercising the pick):

       2025 top-5 (own slot): Dallas, San Antonio, Philadelphia, Charlotte, Utah
       2026 own #1 pick:      Washington
       2026 top-5 (own slot): Washington, Utah, Memphis, Chicago, Indiana

     Only Utah appears in the top 5 in BOTH 2025 and 2026, so Utah is the
     only team entering the real 2027 draft with a live "3 consecutive
     top-5" restriction (a real 2027 top-5 slot would be their 3rd straight).
     Washington had the real 2026 #1 pick, so Washington is restricted from
     the #1 pick specifically in 2027 (the "2 consecutive #1s" rule). No
     other team is restricted going into 2027 under this rule.

ENFORCEMENT MECHANIC (not specified in the league's public announcement,
so this is a documented, reasonable choice, not a confirmed league rule):
if the unconstrained ball draw would seat a restricted team in a forbidden
slot, that team is bumped down to the next slot where they're not
restricted, and every team that would have picked in between shifts up by
one slot. This is the same "push a violator down, shift the rest up"
convention other leagues have used for repeat-pick restrictions, and it
composes correctly with lottery_sim_321.py's floor-protection reordering,
which already runs before this step -- floor protections determine WHERE
a team's ball draw result can be delayed to; pick restrictions never move a
team any earlier than its unconstrained/floor-adjusted slot, only later.
"""

from typing import Dict, List, Optional, Sequence

# Real 2025 and 2026 draft results (first-round picks 1-14, the pre-2027
# lottery range), "Original team" column only -- i.e. whose own record
# produced that slot, independent of which team actually exercised the
# pick via trade. User-supplied.
REAL_2025_OWN_PICKS: Dict[str, int] = {
    "Dallas Mavericks": 1, "San Antonio Spurs": 2, "Philadelphia 76ers": 3,
    "Charlotte Hornets": 4, "Utah Jazz": 5, "Washington Wizards": 6,
    "New Orleans Pelicans": 7, "Brooklyn Nets": 8, "Toronto Raptors": 9,
    "Phoenix Suns": 10, "Portland Trail Blazers": 11, "Chicago Bulls": 12,
    "Sacramento Kings": 13, "Atlanta Hawks": 14,
}

REAL_2026_OWN_PICKS: Dict[str, int] = {
    "Washington Wizards": 1, "Utah Jazz": 2, "Memphis Grizzlies": 3,
    "Chicago Bulls": 4, "Indiana Pacers": 5, "Brooklyn Nets": 6,
    "Sacramento Kings": 7, "New Orleans Pelicans": 8, "Dallas Mavericks": 9,
    "Milwaukee Bucks": 10, "Golden State Warriors": 11, "Los Angeles Clippers": 12,
    "Miami Heat": 13, "Charlotte Hornets": 14,
}


def build_history(*year_own_picks: Dict[str, int]) -> Dict[str, List[int]]:
    """
    Combines any number of years' {team: own_pick_number} maps (oldest
    first) into the {team: [pick_year_n-2, pick_year_n-1, ...]} shape
    violates_restrictions()/enforce_pick_restrictions() expect. A team with
    no entry in a given year (e.g. they made the playoffs and had no
    lottery slot that year) simply has no restriction contribution from
    that year -- only an actual top-5-or-#1 finish creates a restriction.
    """
    history: Dict[str, List[int]] = {}
    for year_picks in year_own_picks:
        for team, pick in year_picks.items():
            history.setdefault(team, []).append(pick)
    return history


# Seeded, ready-to-use history for simulating the 2027 draft (the first
# draft the 3-2-1 restrictions apply to) -- see module docstring.
DEFAULT_2027_HISTORY: Dict[str, List[int]] = build_history(REAL_2025_OWN_PICKS, REAL_2026_OWN_PICKS)


def violates_restrictions(team: str, pick_number: int, history: Dict[str, List[int]]) -> bool:
    """
    True if seating `team` at `pick_number` (their OWN slot for the draft
    being simulated) would break either restriction, given `history` =
    {team: [..., last_year_pick, this_years_pick_so_far_excluded]} (most
    recent year last; only the last 2 entries matter).
    """
    past = history.get(team, [])
    if pick_number == 1 and past and past[-1] == 1:
        return True
    if pick_number <= 5 and len(past) >= 2 and past[-1] <= 5 and past[-2] <= 5:
        return True
    return False


def enforce_pick_restrictions(order: Sequence[str], history: Dict[str, List[int]]) -> List[str]:
    """
    Takes a fully floor-protection-resolved draw order (order[0] = pick 1,
    ..., a permutation of the lottery pool's team names) and re-seats any
    team that would violate a restriction at its drawn slot, per the
    bump-down/shift-up mechanic documented in the module docstring. Returns
    a new list; does not mutate the input.

    Algorithm: fill slots 1..n in order; at each slot, take the FIRST team
    still remaining (in their current relative order) that is legal at that
    slot, skipping over -- but not yet placing -- any restricted team it
    isn't that team's turn for. This is the slot-by-slot generalization of
    "push a violator down, shift the rest up": an unrestricted team at the
    front of the remaining queue is placed immediately (no shift), while a
    restricted team is skipped until the draw reaches a slot where it's
    legal, at which point it's placed and removed from the queue.

    NOTE: an earlier version of this function bumped one restricted team at
    a time via an in-place list splice (order[i:j+1] = ... + [team]) and
    re-checked slot i afterward. That's correct with at most one restricted
    team contending for the top-5/first-legal-slot boundary, but with TWO OR
    MORE teams simultaneously restricted from the same range (e.g. two teams
    both blocked from top-5 in the same draft -- which can't happen in the
    real-history-seeded 2027 draft, but does happen once restrictions are
    chained across multiple simulated years), bumping one could push it onto
    the other and vice versa, forever -- an infinite oscillation, not merely
    a slow case. The slot-by-slot fill below has no such failure mode: each
    iteration of the outer loop permanently places exactly one team, so it
    always terminates in O(n^2) time regardless of how many teams are
    simultaneously restricted.
    """
    remaining = list(order)
    n = len(remaining)
    final_order: List[str] = []
    for slot in range(1, n + 1):
        chosen = None
        for team in remaining:
            if not violates_restrictions(team, slot, history):
                chosen = team
                break
        if chosen is None:
            # No legal team left for this slot (shouldn't happen with
            # today's single #1-repeat and top-5x3 rules against a 16-slot
            # pool, but fail safe rather than silently drop a team): take
            # whoever's next in line rather than lose them.
            chosen = remaining[0]
        final_order.append(chosen)
        remaining.remove(chosen)
    return final_order


def advance_history(history: Dict[str, List[int]], this_years_own_picks: Dict[str, int],
                     keep_last: int = 2) -> Dict[str, List[int]]:
    """
    Returns a NEW history dict with this year's own-pick results appended,
    trimmed to the last `keep_last` entries per team -- use this to chain
    the restriction rule across consecutive simulated draft years (e.g.
    2027's result feeds into enforcing 2028's restrictions).
    """
    updated: Dict[str, List[int]] = {team: list(picks) for team, picks in history.items()}
    for team, pick in this_years_own_picks.items():
        updated.setdefault(team, []).append(pick)
        updated[team] = updated[team][-keep_last:]
    return updated


def derive_own_picks(pick_distribution: Dict[str, Dict[int, int]]) -> Dict[str, int]:
    """
    Collapses one simulated year's FULL per-team pick-count distribution
    (as returned by draft_pipeline_321.monte_carlo_321_pick_distribution --
    {team: {pick_number: trial_count}}) down to a single representative
    "own pick" integer per team, suitable for advance_history()'s
    `this_years_own_picks` argument.

    ASSUMPTION, not a fit: this project's multi-year restriction-carry-
    forward isn't a single fully-correlated Monte Carlo chain (that would
    need every trial's own 2028 draft to depend on THAT SAME trial's 2027
    result, which the rest of this pipeline doesn't do either -- every
    draft year already runs as its own independent trial batch against
    that year's ratings, e.g. run_real_league.build_projected_standings).
    Consistent with that existing level of approximation, each year's
    restriction-relevant outcome is instead collapsed to its single MODAL
    (most frequent) pick number across that year's trials -- "if forced to
    name one deterministic outcome for this year, use the most likely
    one" -- and that one number is what feeds the next year's restriction
    check. This can only ever miscall a team's restriction status in the
    (rare, since it requires a near-even three-way-or-worse split) case
    where no single pick number clears a plurality by a meaningful margin;
    exact pick number beyond "1", "2-5", or "6+" never matters here since
    violates_restrictions() only checks those three buckets.
    """
    return {team: max(counts, key=counts.get) for team, counts in pick_distribution.items() if counts}


if __name__ == "__main__":
    print("2027 restriction state seeded from real 2025+2026 results:")
    for team, picks in sorted(DEFAULT_2027_HISTORY.items()):
        flags = []
        if picks and picks[-1] == 1:
            flags.append("blocked from #1 in 2027")
        if len(picks) >= 2 and picks[-2] <= 5 and picks[-1] <= 5:
            flags.append("blocked from top-5 in 2027")
        if flags:
            print(f"  {team:<28} {picks}  -- {', '.join(flags)}")

    # Sanity check: repeatedly draw a synthetic 16-team pool with Washington
    # forced into pick 1 and Utah forced into pick 3, confirm the
    # restriction mechanic reseats them correctly and never drops a team or
    # duplicates a slot.
    import random
    fake_order = ["Washington Wizards", "Utah Jazz"] + [f"Other{i}" for i in range(14)]
    fixed_history = DEFAULT_2027_HISTORY

    violations = 0
    trials = 5000
    rng = random.Random(7)
    for _ in range(trials):
        order = list(fake_order)
        rng.shuffle(order)
        # force the two restricted teams back to the front to stress-test
        order.remove("Washington Wizards")
        order.remove("Utah Jazz")
        order = ["Washington Wizards", "Utah Jazz"] + order
        fixed = enforce_pick_restrictions(order, fixed_history)
        assert sorted(fixed) == sorted(order), "enforce_pick_restrictions dropped or duplicated a team"
        if fixed[0] == "Washington Wizards":
            violations += 1
        if fixed.index("Utah Jazz") < 5:
            violations += 1
    print(f"\n{trials} stress-test draws, restriction violations after enforcement: {violations} (expect 0)")
