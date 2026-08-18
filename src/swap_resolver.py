"""
Resolves conditional/swap draft-pick language (draft_picks_data.py's raw
text) into concrete pick_grading.PickAsset objects, for the subset of swap
expressions that are mechanically resolvable: a flat comparison ("Most/2nd
Favorable/.../Least Favorable") among 2-4 named teams' SAME-fragment picks,
optionally with a numeric protection range on the resulting pick number.

WHY THIS HAS TO USE JOINT (CORRELATED) TRIALS, NOT MARGINAL DISTRIBUTIONS:
"The less-favorable of (Team A, Team B)'s picks" is NOT well-approximated by
comparing A's and B's independent marginal pick distributions. Their records
aren't independent draws -- they share a conference, overlapping schedules,
and sometimes correlated roster situations -- and "less favorable" is a
per-trial operation: you need the ACTUAL pair (pickA, pickB) from the SAME
simulated season, take whichever the swap language selects that trial, and
only then look at the distribution of results across trials. This module
always draws teams-of-interest picks from
draft_pipeline_321.joint_pick_number_trials(), which runs every team of
interest through the SAME batch of simulated seasons, preserving that
correlation. (See that function's docstring for the mechanics.)

SCOPE -- what this resolves vs. leaves alone (deliberately conservative, same
philosophy as draft_picks_data.py and pick_resolver.py: a plausible-looking
but wrong number is worse than an honest "not resolved yet"):

  RESOLVED HERE:
    - "TEAM1/TEAM2[/TEAM3[/TEAM4]] (Qualifier) ROUND [(If #A-B)]" -- a flat,
      single-fragment comparison among 2-4 teams' picks, fully restated
      within that one fragment. Qualifier must be one of the exact phrases
      in QUALIFIER_RANK below.

  NOT RESOLVED HERE (categorized by reason via classify_unresolved_reason,
  left as raw text for manual handling or future work):
    - CROSS_PICK_CONDITIONAL: the pick's existence/protection depends on a
      DIFFERENT pick's outcome (e.g. "MIA 2nd (If 2027 DAL 1st is #1-2)"),
      sometimes in a different draft year entirely. Resolving this correctly
      needs multiple draft years simulated jointly for the same league (so
      the dependency chain resolves consistently) -- the current simulator
      only models one static-strength season at a time, so this is out of
      scope until team strength is modeled as evolving year over year.
    - NESTED_OR_ELLIPTICAL: fragments with a parenthesized sub-group inside
      the team list (e.g. "ATL/(CLE/UTA (Less Favorable)) (More Favorable)
      1st") or fragments that are a continuation of a PRECEDING sibling
      fragment's team group via comma-splitting (e.g. a bare "(2nd
      Favorable) 2nd" with no team list of its own -- this only makes sense
      read together with the fragment before it, which the current
      fragment-by-fragment parser doesn't attempt).
    - AMBIGUOUS_ANNOTATION: a parenthetical that doesn't clearly read as
      either a protection ("If #A-B") or a swap qualifier -- e.g. "GS 2nd
      (#31-50)" with no "If", which could be an informational range rather
      than an actual condition. Left alone rather than guessed at.

Single-team picks with ONLY a protection range and no swap at all (e.g. "DAL
1st (If #3-30)") are NOT handled here -- those aren't swaps, and are instead
picked up directly in pick_resolver.py's build_pick_assets() as a protected
own pick.
"""

import re
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Sequence, Tuple

from pick_grading import PickAsset

# Qualifier text (exact phrase as it appears in the source data) -> rank
# among the named teams' picks that trial. Rank 1 = the single MOST
# favorable (lowest pick number) outcome; rank -1 is a sentinel meaning
# "the single LEAST favorable (highest pick number) outcome", resolved to
# len(teams) once the team count is known (parse_swap_fragment does this).
QUALIFIER_RANK: Dict[str, int] = {
    "More Favorable": 1,
    "Most Favorable": 1,
    "2nd Favorable": 2,
    "2nd Most Favorable": 2,
    "3rd Favorable": 3,
    "3rd Most Favorable": 3,
    "Less Favorable": -1,
    "Least Favorable": -1,
}

# Matches: TEAM1/TEAM2[/TEAM3[/TEAM4]] (Qualifier) ROUND [(If #LO-HI)]
# e.g. "MIL/NO (Less Favorable) 1st (If #5-30)"
#      "DAL/HOU/PHX (Least Favorable) 1st"
FLAT_SWAP_RE = re.compile(
    r"^([A-Z]{2,3}(?:/[A-Z]{2,3}){1,3})"      # 2-4 team codes, slash-separated
    r"\s*\(([^)]+)\)"                          # qualifier text in parens
    r"\s*(1st|2nd)"                            # round
    r"(?:\s*\(If\s*#(\d+)-(\d+)\))?"           # optional trailing protection range
    r"\s*$"
)

# A bare protection/qualifier parenthetical with no team list attached --
# almost always an elliptical continuation of a preceding comma-separated
# sibling fragment (e.g. "(2nd Favorable) 2nd" following "DEN (If #6-30)/LAC/OKC
# (Most Favorable) 1st, (2nd Favorable) 1st" in the same year's description).
BARE_QUALIFIER_RE = re.compile(r"^\([^)]+\)\s*(1st|2nd)\s*$")

# A parenthetical range with no "If" -- ambiguous, not clearly a condition.
BARE_RANGE_NO_IF_RE = re.compile(r"\(#\d+-\d+\)")

# A protection/condition that names a specific year, i.e. depends on a
# different pick's resolved outcome rather than a static numeric range.
CROSS_PICK_RE = re.compile(r"\(If\s*\d{4}\b")

# Full pick-number range for each round, used to invert a "(If #LO-HI)"
# stated CONVEYS-range into the complementary DOES-NOT-CONVEY range that
# pick_grading.PickAsset.protection_range expects (see the inversion note
# in parse_swap_fragment's caller, build below).
FULL_RANGE_BY_ROUND: Dict[str, Tuple[int, int]] = {"1st": (1, 30), "2nd": (31, 60)}


def invert_conveys_range_to_protection(round_str: str, stated_range: Tuple[int, int]) -> Optional[Tuple[int, int]]:
    """
    The source data's "(If #LO-HI)" text states the range in which the pick
    DOES convey to whoever's section it's listed under (verified against
    draft_picks_data.py's real examples -- e.g. Miami's own retained 2027
    first is listed as "MIA 1st (If #1-14)" in Miami's section, meaning
    Miami keeps it if it's top-14, i.e. it conveys to Miami only in that
    range; Charlotte's section separately lists "MIA 1st (If #15-30)" for
    the same pick, meaning it conveys to Charlotte only outside Miami's
    top-14 protection).

    pick_grading.PickAsset.protection_range is defined the OPPOSITE way --
    the range in which the pick does NOT convey. So this inverts the stated
    range to its complement within the round's full 1-30 / 31-60 span.

    Every stated range actually observed in draft_picks_data.py is anchored
    to one edge of its round (e.g. (5, 30) or (31, 55)), so the complement
    is always a single contiguous range. If some future data has a
    "sandwiched" range touching neither edge, that can't be represented as
    one PickAsset.protection_range tuple -- return None (caller treats the
    fragment as unresolved) rather than silently dropping information.
    """
    full_lo, full_hi = FULL_RANGE_BY_ROUND[round_str]
    stated_lo, stated_hi = stated_range
    if stated_lo == full_lo and stated_hi < full_hi:
        return (stated_hi + 1, full_hi)
    if stated_hi == full_hi and stated_lo > full_lo:
        return (full_lo, stated_lo - 1)
    if stated_lo == full_lo and stated_hi == full_hi:
        return None  # covers the whole round -- no real protection, drop it
    return None  # sandwiched / not edge-anchored -- don't guess


class UnresolvedReason(Enum):
    CROSS_PICK_CONDITIONAL = "depends on a different pick's outcome (needs multi-year simulation)"
    NESTED_OR_ELLIPTICAL = "nested parens or a continuation fragment -- needs manual resolution"
    AMBIGUOUS_ANNOTATION = "parenthetical range with no 'If' -- unclear if it's a real condition"
    UNRECOGNIZED = "doesn't match any known pattern"


@dataclass
class SwapPick:
    year: int
    teams: List[str]                          # team codes, in the order written
    rank: int                                  # 1 = best of the group, len(teams) = worst
    round_str: str                             # "1st" or "2nd"
    protection_range: Optional[Tuple[int, int]] = None
    raw_text: str = ""


def classify_unresolved_reason(fragment: str) -> UnresolvedReason:
    """Best-effort explanation for why a fragment wasn't auto-resolved -- for
    surfacing to a human, not for driving any further automatic logic."""
    if CROSS_PICK_RE.search(fragment):
        return UnresolvedReason.CROSS_PICK_CONDITIONAL
    if BARE_QUALIFIER_RE.match(fragment.strip()):
        return UnresolvedReason.NESTED_OR_ELLIPTICAL
    if "(" in fragment and ")" in fragment:
        # Nested parens (more than one distinct paren group, or a paren
        # group containing another team-list-like token) -- heuristic catch-all.
        if fragment.count("(") > 1 or re.search(r"\([A-Z]{2,3}/", fragment):
            return UnresolvedReason.NESTED_OR_ELLIPTICAL
        if BARE_RANGE_NO_IF_RE.search(fragment) and "If" not in fragment:
            return UnresolvedReason.AMBIGUOUS_ANNOTATION
    return UnresolvedReason.UNRECOGNIZED


def parse_swap_fragment(year: int, fragment: str) -> Optional[SwapPick]:
    """
    Attempts to parse one raw pick-description fragment into a SwapPick.
    Returns None if the fragment isn't a flat, single-group swap this
    module can handle -- caller should fall back to
    classify_unresolved_reason() to explain why.
    """
    m = FLAT_SWAP_RE.match(fragment.strip())
    if not m:
        return None

    team_str, qualifier, round_str, lo, hi = m.groups()
    teams = team_str.split("/")
    if len(set(teams)) != len(teams):
        return None  # repeated team code -- malformed, don't guess

    if qualifier not in QUALIFIER_RANK:
        return None  # unrecognized qualifier vocabulary -- don't guess

    rank = QUALIFIER_RANK[qualifier]
    if rank == -1:
        rank = len(teams)  # "Less/Least Favorable" = worst of the group
    if rank > len(teams):
        return None  # e.g. "3rd Favorable" among only 2 teams -- malformed

    protection = None
    if lo and hi:
        stated_range = (int(lo), int(hi))
        # NOTE: the source text's "(If #LO-HI)" states the CONVEYS range,
        # not the protection range -- invert it. See
        # invert_conveys_range_to_protection's docstring for why.
        protection = invert_conveys_range_to_protection(round_str, stated_range)
        if protection is None and stated_range != FULL_RANGE_BY_ROUND[round_str]:
            # A real condition was stated but couldn't be safely inverted
            # (not edge-anchored) -- don't silently drop it as unprotected.
            return None

    return SwapPick(year=year, teams=teams, rank=rank, round_str=round_str,
                     protection_range=protection, raw_text=fragment)


def resolve_swap_distribution(swap: SwapPick, joint_trials: Dict[str, List[int]]) -> Dict[int, float]:
    """
    joint_trials: {team_code: [pick_number_trial_0, pick_number_trial_1, ...]}
    for EXACTLY the teams in swap.teams, drawn from the SAME correlated
    batch (draft_pipeline_321.joint_pick_number_trials()) -- the value at
    index i for every team must come from the same simulated season.

    Returns a {pick_number: probability} distribution of the RESOLVED pick
    (the swap.rank-th best among the named teams, per trial). Protection, if
    any, is intentionally NOT applied here -- wrap the result in a
    pick_grading.PickAsset with protection_range set (see swap_to_pick_asset
    below) so protection handling stays in one place (pick_grading.py).
    """
    missing = [t for t in swap.teams if t not in joint_trials]
    if missing:
        raise KeyError(f"joint_trials missing required teams: {missing}")

    n_trials = len(joint_trials[swap.teams[0]])
    for t in swap.teams:
        if len(joint_trials[t]) != n_trials:
            raise ValueError("joint_trials lists must all be the same length (same trial batch)")
    if n_trials == 0:
        raise ValueError("joint_trials has zero trials")

    counts: Dict[int, int] = {}
    for i in range(n_trials):
        # Ascending sort: index 0 = smallest pick number = most favorable.
        trial_picks = sorted(joint_trials[t][i] for t in swap.teams)
        resolved = trial_picks[swap.rank - 1]
        counts[resolved] = counts.get(resolved, 0) + 1

    return {pick: count / n_trials for pick, count in counts.items()}


def swap_to_pick_asset(swap: SwapPick, joint_trials: Dict[str, List[int]],
                        current_year: int = 2026, fallback_value: float = 0.0) -> PickAsset:
    """Resolves a SwapPick against a joint-trial batch and wraps the result
    as a gradable PickAsset (protection applied via pick_grading.py)."""
    dist = resolve_swap_distribution(swap, joint_trials)
    qualifier_desc = "most favorable" if swap.rank == 1 else (
        "least favorable" if swap.rank == len(swap.teams) else f"rank {swap.rank} of {len(swap.teams)}"
    )
    label = (f"{swap.year} {'/'.join(swap.teams)} {swap.round_str} "
             f"({qualifier_desc}, swap-resolved)")
    years_away = max(0, swap.year - current_year)
    return PickAsset(
        label=label,
        pick_probabilities=dist,
        protection_range=swap.protection_range,
        fallback_value=fallback_value,
        years_away=years_away,
    )


if __name__ == "__main__":
    # Self-contained demo: fabricate a joint-trial batch by hand (as if two
    # teams' picks were drawn from the same 10 simulated seasons) and show
    # the "less favorable of A/B" resolution matches the obvious answer.
    fake_joint = {
        "MIL": [3, 12, 25, 8, 30, 1, 19, 14, 6, 22],
        "NO":  [7, 5, 25, 20, 2, 16, 19, 9, 6, 11],
    }
    swap = parse_swap_fragment(2027, "MIL/NO (Less Favorable) 1st (If #5-30)")
    print("Parsed:", swap)
    dist = resolve_swap_distribution(swap, fake_joint)
    print("\nTrial-by-trial check (MIL, NO) -> worse (higher) pick number:")
    for i in range(10):
        pair = (fake_joint["MIL"][i], fake_joint["NO"][i])
        print(f"  trial {i}: MIL={pair[0]:>2} NO={pair[1]:>2} -> worse={max(pair)}")
    print(f"\nResolved distribution: {dist}")

    asset = swap_to_pick_asset(swap, fake_joint, current_year=2026)
    g = asset.grade()
    print(f"\nAs a graded PickAsset (top-4-protected via the (If #5-30) clause -- "
          f"i.e. does NOT convey if the worse pick lands #1-4):")
    print(f"  {g}")

    print("\n--- classify_unresolved_reason examples ---")
    examples = [
        "MIA 2nd (If 2027 DAL 1st is #1-2)",
        "(2nd Favorable) 2nd",
        "ATL/(CLE/UTA (Less Favorable)) (More Favorable) 1st",
        "GS 2nd (#31-50)",
    ]
    for ex in examples:
        print(f"  {ex!r:55} -> {classify_unresolved_reason(ex).name}")
