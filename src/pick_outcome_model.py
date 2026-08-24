"""
Converts a DRAFT PICK NUMBER into a probabilistic career-outcome tier, and
that tier into an assumed DPM (DARKO Daily Plus-Minus) contribution a team
can expect that player to add to its roster in future years -- the missing
piece needed to let a team's ACTUAL simulated draft outcome in year Y feed
back into its projected strength for year Y+1 and beyond (see
sequential_league_sim.py, which is the actual consumer of this module).

WHY THIS EXISTS: darko_ratings.py is explicit that its evolution model
"can never GAIN talent over time" -- departing players decay away, but
nobody's draft picks ever turn into a rookie who actually helps the team.
This module is the other half: given pick_valuation.py/pick_grading.py
already grade a pick's TRADE value, this instead grades what the drafted
PLAYER is likely to become, in the same DPM units darko_ratings.py already
works in, so the two compose additively.

DATA SOURCE: data/NBA_Draft_Picks_20152025.xlsx, "Draft Picks 2015-2025"
sheet -- 330 real first-round picks (2015-2025), each hand-tagged with a
subjective career-outcome tier (Superstar / Star-All-Star / Above-average
starter / Contributor / Bust; see that file's "Legend" sheet for the exact
criteria). The 2024-2025 classes (59 picks) are excluded here as "too
early to tell," leaving 271 usable picks -- the same 2015-2023 population
pick_valuation.py's trade-value curve was calibrated from
(calibrate_pick_value.py). This is a DIFFERENT use of the same underlying
data: that module asks "what would a team trade this pick for," this one
asks "what is this player likely to become, in DPM terms."

BUCKET_TIER_PROBS below is NOT re-derived by re-opening the xlsx at
runtime -- like pick_valuation.py's curve constants, it's precomputed once
(bucketed by 5-pick ranges, matching the workbook's own "Charts" tab
exactly, verified against it) and hardcoded here. To recompute from the
source file directly, see the derivation in this module's __main__ block.

SCOPE LIMITATION -- ROUND 2 IS EXTRAPOLATED, NOT REAL DATA: the source
sheet only covers picks 1-30 (first round). ROUND2_TIER_PROBS below is a
documented JUDGMENT CALL (not fit from data) that continues the observed
trend of the 26-30 bucket (already the worst first-round bucket) shifting
further toward Bust/Contributor -- treat second-round outcome tiers as a
rough extrapolation, not an empirical result, the same way this codebase
already treats pick_valuation.SECOND_ROUND_DISCOUNT as a judgment call
rather than a fitted number.

TIER_DPM below is a second documented judgment call: there's no direct
"this tier equals X DPM" data anywhere, so these anchor values are chosen
to line up with the REAL, currently-rostered NBA player population in
data/darkodpmleaderboard.csv (530 active players) -- specifically: that
population's top-10 average DPM is 5.0, top-30 average is 3.4, median is
-1.0, and the observed floor for a still-rostered player is around -5.0.
TIER_DPM's values are picked to sit at plausible points along that real
distribution for each tier's description (see the constant itself for the
per-tier reasoning). These are NOT independently validated against actual
draft-to-DPM outcomes -- that would require matching each of the 271
tagged players to their own real DARKO history, which is future work, not
something this module currently does. Treat TIER_DPM as a reasonable,
transparent assumption, not a calibrated fit.

RAMP_BY_YEARS_SINCE_DRAFT is a third documented judgment call: real
rookies rarely play (or perform at) their eventual steady-state level
immediately. This ramps a drafted player's assumed contribution in
linearly-ish over their first few years, capping at 100% from year 4
onward. Also a judgment call, not fit from data.
"""

import random
from typing import Dict, Optional, Tuple

TIERS = ["Superstar", "Star/All-Star", "Above-average starter", "Contributor", "Bust"]

# Precomputed from data/NBA_Draft_Picks_20152025.xlsx's "Draft Picks
# 2015-2025" sheet, 2015-2023 picks only (271 usable rows, "too early to
# tell" 2024-2025 picks excluded). Verified to match that workbook's own
# "Charts" tab exactly. n = sample size per bucket (all comfortably above
# 40, but still real-world small-sample noise -- treat individual bucket
# percentages as directionally right, not precise to the decimal).
BUCKET_TIER_PROBS: Dict[Tuple[int, int], Dict[str, float]] = {
    (1, 5): {"Superstar": 0.1556, "Star/All-Star": 0.3556, "Above-average starter": 0.1778,
             "Contributor": 0.1333, "Bust": 0.1778},  # n=45
    (6, 10): {"Superstar": 0.0, "Star/All-Star": 0.1136, "Above-average starter": 0.2273,
              "Contributor": 0.3636, "Bust": 0.2955},  # n=44
    (11, 15): {"Superstar": 0.0889, "Star/All-Star": 0.1111, "Above-average starter": 0.2,
               "Contributor": 0.3111, "Bust": 0.2889},  # n=45
    (16, 20): {"Superstar": 0.0, "Star/All-Star": 0.0444, "Above-average starter": 0.2222,
               "Contributor": 0.4222, "Bust": 0.3111},  # n=45
    (21, 25): {"Superstar": 0.0217, "Star/All-Star": 0.0435, "Above-average starter": 0.1304,
               "Contributor": 0.2826, "Bust": 0.5217},  # n=46
    (26, 30): {"Superstar": 0.0, "Star/All-Star": 0.087, "Above-average starter": 0.1957,
               "Contributor": 0.2826, "Bust": 0.4348},  # n=46
}

# JUDGMENT CALL, not fit from data -- see module docstring's "SCOPE
# LIMITATION" note. Continues the 26-30 bucket's trend further toward
# Bust/Contributor for the second round.
ROUND2_TIER_PROBS: Dict[Tuple[int, int], Dict[str, float]] = {
    (31, 40): {"Superstar": 0.0, "Star/All-Star": 0.04, "Above-average starter": 0.14,
               "Contributor": 0.28, "Bust": 0.54},
    (41, 50): {"Superstar": 0.0, "Star/All-Star": 0.015, "Above-average starter": 0.085,
               "Contributor": 0.25, "Bust": 0.65},
    (51, 60): {"Superstar": 0.0, "Star/All-Star": 0.005, "Above-average starter": 0.045,
               "Contributor": 0.20, "Bust": 0.75},
}

# JUDGMENT CALL, not fit from data -- see module docstring's "TIER_DPM"
# note. Anchored against data/darkodpmleaderboard.csv's real 530-player
# distribution (top-10 avg 5.0, top-30 avg 3.4, median -1.0, floor ~-5.0).
TIER_DPM: Dict[str, float] = {
    "Superstar": 6.5,       # near the top-10 average of currently rostered players
    "Star/All-Star": 3.5,   # roughly the top-30 average -- All-Star-caliber production
    "Above-average starter": 1.0,   # solidly positive, short of All-Star level
    "Contributor": -1.5,    # below the league median -- a real bench/rotation piece
    "Bust": -3.5,            # near the bottom of the currently-rostered population
}

# JUDGMENT CALL, not fit from data -- see module docstring's "RAMP" note.
# Fraction of TIER_DPM's full value assumed to be realized N years after
# being drafted (year 1 = the draft year itself; a player drafted in 2027
# is assumed to contribute at the year-1 rate starting with the 2028
# season, i.e. offset 1 in darko_ratings.py's terms).
RAMP_BY_YEARS_SINCE_DRAFT: Dict[int, float] = {1: 0.30, 2: 0.65, 3: 0.90}
RAMP_FULL_AFTER_YEARS = 4  # 100% from this many years post-draft onward

# A team's total on-court player-minutes pool per game (5 players x 48
# minutes, ignoring overtime) -- the denominator used to convert an
# assumed drafted-player minutes share into a team-average DPM shift, the
# same style of MPG-weighted-average approach team_net_rating() in
# darko_ratings.py already uses for real rostered players.
TEAM_MPG_POOL = 240.0

# Assumed STEADY-STATE (fully ramped) minutes/game for a drafted player,
# BY OUTCOME TIER rather than by round. This matters: real NBA teams don't
# hand a bust the same minutes as a star just because both were drafted in
# round 1 -- busts get benched, stars play heavy minutes. Keying minutes
# off the realized tier (not the round) captures that; the round's effect
# is already fully captured separately, through BUCKET_TIER_PROBS/
# ROUND2_TIER_PROBS making good tiers much less LIKELY for later picks --
# using round to ALSO discount assumed minutes would double-count that.
# JUDGMENT CALL, not fit from data.
TIER_MPG: Dict[str, float] = {
    "Superstar": 34.0,      # a franchise cornerstone, heavy minutes immediately once developed
    "Star/All-Star": 30.0,  # a clear starter getting starter-plus minutes
    "Above-average starter": 24.0,  # a normal full-time starter's workload
    "Contributor": 14.0,    # a rotation/bench piece, meaningful but limited minutes
    "Bust": 5.0,             # a fringe roster spot -- mostly doesn't play, so the drag is small
}


def tier_probs_for_pick(pick_number: int) -> Dict[str, float]:
    """Returns the {tier: probability} distribution for a given 1-60 pick number."""
    if not (1 <= pick_number <= 60):
        raise ValueError(f"pick_number must be 1-60, got {pick_number}")
    table = BUCKET_TIER_PROBS if pick_number <= 30 else ROUND2_TIER_PROBS
    for (lo, hi), probs in table.items():
        if lo <= pick_number <= hi:
            return probs
    raise AssertionError(f"no bucket covers pick {pick_number} -- bucket tables have a gap")


def sample_outcome_tier(pick_number: int, rng: random.Random) -> str:
    """Draws one random career-outcome tier for a hypothetical player picked at pick_number."""
    probs = tier_probs_for_pick(pick_number)
    tiers = list(probs.keys())
    weights = list(probs.values())
    return rng.choices(tiers, weights=weights, k=1)[0]


def ramp_fraction(years_since_drafted: int) -> float:
    """0.0-1.0 fraction of full TIER_DPM value realized this many years after being drafted."""
    if years_since_drafted < 1:
        return 0.0
    if years_since_drafted >= RAMP_FULL_AFTER_YEARS:
        return 1.0
    return RAMP_BY_YEARS_SINCE_DRAFT.get(years_since_drafted, 1.0)


def team_dpm_delta(pick_number: int, tier: str, years_since_drafted: int) -> float:
    """
    The additive shift to a team's average roster DPM from having drafted
    a player of this tier at this pick, N years after the draft (see
    ramp_fraction). This is what sequential_league_sim.py adds into a
    team's darko_ratings.py-style net rating before reconverting to Elo.
    """
    mpg = TIER_MPG[tier]
    dpm = TIER_DPM[tier]
    return (mpg * ramp_fraction(years_since_drafted) * dpm) / TEAM_MPG_POOL


def sample_team_dpm_delta(pick_number: int, years_since_drafted: int, rng: random.Random
                           ) -> Tuple[str, float]:
    """Convenience: sample a tier and return (tier, team_dpm_delta) together."""
    tier = sample_outcome_tier(pick_number, rng)
    return tier, team_dpm_delta(pick_number, tier, years_since_drafted)


if __name__ == "__main__":
    # Recompute BUCKET_TIER_PROBS/OVERALL_PROBS from the source xlsx directly,
    # to verify the hardcoded constants above still match the source file.
    import openpyxl
    from collections import Counter
    from data_paths import find_data_file
    import os

    xlsx_path = find_data_file("NBA_Draft_Picks_20152025.xlsx", os.path.dirname(os.path.abspath(__file__)))
    wb = openpyxl.load_workbook(xlsx_path, data_only=True)
    ws = wb["Draft Picks 2015-2025"]
    rows = list(ws.iter_rows(min_row=3, values_only=True))
    TIER_CLEAN = {
        "\U0001f7e9 Superstar": "Superstar",
        "\U0001f7e6 Star / All-Star": "Star/All-Star",
        "\U0001f7e8 Above-average starter": "Above-average starter",
        "⬛ Contributor / role player": "Contributor",
        "\U0001f7e5 Bust": "Bust",
    }
    usable = [(r[1], TIER_CLEAN[r[5]]) for r in rows if r[5] in TIER_CLEAN]
    print(f"Recomputing from {xlsx_path}: {len(usable)} usable (non-'too early') picks\n")
    mismatches = 0
    for (lo, hi), hardcoded in BUCKET_TIER_PROBS.items():
        in_bucket = [t for p, t in usable if lo <= p <= hi]
        n = len(in_bucket)
        counts = Counter(in_bucket)
        recomputed = {t: round(counts.get(t, 0) / n, 4) for t in TIERS}
        match = "OK" if recomputed == hardcoded else "MISMATCH"
        if match == "MISMATCH":
            mismatches += 1
        print(f"  ({lo:>2}, {hi:>2})  n={n:<3}  {match}")
        if match == "MISMATCH":
            print(f"    hardcoded:  {hardcoded}")
            print(f"    recomputed: {recomputed}")
    print(f"\n{'All buckets match the source file.' if mismatches == 0 else f'{mismatches} bucket(s) MISMATCHED -- re-derive and update BUCKET_TIER_PROBS above.'}")

    print("\nExample: expected team DPM delta by pick number, at full ramp (year 4+):")
    for pick in [1, 5, 10, 15, 20, 25, 30, 40, 55]:
        # expectation over the tier distribution, not a single sample
        probs = tier_probs_for_pick(pick)
        expected_dpm = sum(p * team_dpm_delta(pick, tier, years_since_drafted=4) for tier, p in probs.items())
        print(f"  Pick {pick:>2}: expected team DPM delta = {expected_dpm:+.3f}")
