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

# Matches: TEAM1/TEAM2[/TEAM3[/TEAM4[/TEAM5]]] (Qualifier) ROUND [(If #LO-HI)]
# e.g. "MIL/NO (Less Favorable) 1st (If #5-30)"
#      "DAL/HOU/PHX (Least Favorable) 1st"
#      "HOU/IND/MIA/OKC/SA (Least Favorable) 2nd"
FLAT_SWAP_RE = re.compile(
    r"^([A-Z]{2,3}(?:/[A-Z]{2,3}){1,4})"      # 2-5 team codes, slash-separated
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

# A single team's future pick with a BARE numeric protection range, no "If"
# text: "GS 2nd (#31-50)". Distinct from SIMPLE_PROTECTED_RE (which requires
# "If") -- only fired for edge-anchored ranges (see
# invert_conveys_range_to_protection), which is the same safety net that
# already governs whether this ever actually resolves to something. Applied
# broadly rather than to specific teams because the edge-anchoring check
# itself is the guard against false positives: a genuinely ambiguous
# "informational" range (sandwiched, not touching either boundary of the
# round) still safely falls through to AMBIGUOUS_ANNOTATION unresolved,
# unchanged. Confirmed against real data: Golden State's 2032 "GS 2nd
# (#31-50)" and Memphis's 2032 "GS 2nd (#51-60)" are the two halves of the
# SAME pick (round 2's full range is 31-60, and the two stated ranges
# partition it exactly at the 50/51 boundary with no gap or overlap) --
# strong evidence these are real conditions, just formatted without "If".
BARE_RANGE_PROTECTED_RE = re.compile(
    r"^([A-Z]{2,3})\s+(1st|2nd)\s*\(#(\d+)-(\d+)\)$"
)

# Same-year, single-team "cross-pick conditional": TEAM's pick only exists
# (conveys) if a DIFFERENT (or the same) team's SAME-YEAR pick lands in a
# stated range, e.g. "CHA 2nd (If 2027 SA 1st is #1-16)" or "PHI 2nd (If
# 2028 PHI 1st is #1-8)". Optionally combined with TEAM's own protection
# range on top (checked only within the "conveys" branch), e.g. "BOS 2nd
# (If #31-45) (If 2028 BOS 1st is #2-30)". RESOLVABLE when cond_year equals
# the fragment's own draft year (both picks come from the exact same
# simulated season, so draft_pipeline_321.joint_pick_number_trials already
# correlates them) -- see pick_resolver.py's conditional-pick tier. A
# DIFFERENT year (e.g. "MIA 1st (If 2027 MIA 1st is #15-30)" appearing
# under a team's 2028 entry) still matches this regex syntactically but is
# NOT resolved (the caller checks cond_year == year and leaves cross-year
# matches to fall through to classify_unresolved_reason unchanged) -- that
# needs multiple draft years correlated within the same trial, which this
# pipeline's per-year-independent-trials design doesn't support.
CROSS_PICK_SAME_YEAR_RE = re.compile(
    r"^([A-Z]{2,3})\s+(1st|2nd)"
    r"(?:\s*\(If\s*#(\d+)-(\d+)\))?"                                          # optional own protection range
    r"\s*\(If\s*(\d{4})\s+([A-Z]{2,3})\s+(1st|2nd)\s+is\s*#(\d+)(?:-(\d+))?\)"  # cross-pick condition (range or single pick)
    r"\s*$"
)

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


@dataclass
class ConditionalPick:
    """A same-year, single-team cross-pick conditional -- see
    CROSS_PICK_SAME_YEAR_RE's docstring. `team_code`'s pick conveys only in
    trials where `cond_team_code`'s `cond_round_str` pick that same year
    lands in [cond_lo, cond_hi]; `own_protection_range`, if set, is an
    ADDITIONAL ordinary protection on team_code's own pick number, checked
    only within the "it conveyed" branch."""
    year: int
    team_code: str
    round_str: str
    cond_team_code: str
    cond_round_str: str
    cond_range: Tuple[int, int]
    own_protection_range: Optional[Tuple[int, int]] = None
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


def parse_conditional_pick_fragment(year: int, fragment: str) -> Optional[ConditionalPick]:
    """
    Attempts to parse a same-year, single-team cross-pick conditional (see
    CROSS_PICK_SAME_YEAR_RE and ConditionalPick's docstrings). Returns None
    if the fragment doesn't match that shape AT ALL, OR if it matches but
    the condition's year differs from `year` (a genuine cross-year
    conditional -- caller should fall back to classify_unresolved_reason,
    which still correctly labels it CROSS_PICK_CONDITIONAL either way).
    """
    m = CROSS_PICK_SAME_YEAR_RE.match(fragment.strip())
    if not m:
        return None

    team_code, round_str, own_lo, own_hi, cond_year, cond_team, cond_round, cond_lo, cond_hi = m.groups()
    if int(cond_year) != year:
        return None  # cross-year -- not resolvable here, leave to the caller's normal fallback
    if cond_hi is None:
        cond_hi = cond_lo  # "is #1" (single pick number) rather than "is #A-B" (a range)

    own_protection = None
    if own_lo and own_hi:
        stated_range = (int(own_lo), int(own_hi))
        own_protection = invert_conveys_range_to_protection(round_str, stated_range)
        if own_protection is None and stated_range != FULL_RANGE_BY_ROUND[round_str]:
            return None  # stated but not safely invertible -- don't guess

    return ConditionalPick(
        year=year, team_code=team_code, round_str=round_str,
        cond_team_code=cond_team, cond_round_str=cond_round,
        cond_range=(int(cond_lo), int(cond_hi)),
        own_protection_range=own_protection, raw_text=fragment,
    )


def resolve_conditional_pick(cond: ConditionalPick, joint_trials: Dict[str, Dict[str, List[int]]]
                              ) -> Tuple[Dict[int, float], float]:
    """
    joint_trials: {team_code: {"1st": [...], "2nd": [...]}} for EXACTLY
    cond.team_code and cond.cond_team_code, from the SAME correlated batch
    (both picks must come from the same simulated season for the
    conditioning to mean anything).

    Returns (conditioned_distribution, convey_probability):
      conditioned_distribution: {pick_number: probability}, normalized over
        ONLY the trials where the condition held (i.e. sums to 1) -- pass
        as PickAsset.pick_probabilities.
      convey_probability: fraction of all trials where the condition held
        -- pass as PickAsset.convey_probability.
    """
    cond_values = joint_trials[cond.cond_team_code][cond.cond_round_str]
    target_values = joint_trials[cond.team_code][cond.round_str]
    n_trials = len(cond_values)
    if len(target_values) != n_trials:
        raise ValueError("joint_trials lists must all be the same length (same trial batch)")
    if n_trials == 0:
        raise ValueError("joint_trials has zero trials")

    lo, hi = cond.cond_range
    counts: Dict[int, int] = {}
    convey_count = 0
    for i in range(n_trials):
        if lo <= cond_values[i] <= hi:
            convey_count += 1
            counts[target_values[i]] = counts.get(target_values[i], 0) + 1

    convey_probability = convey_count / n_trials
    if convey_count == 0:
        return {}, 0.0
    dist = {pick: count / convey_count for pick, count in counts.items()}
    return dist, convey_probability


def conditional_pick_to_asset(cond: ConditionalPick, joint_trials: Dict[str, Dict[str, List[int]]],
                               current_year: int = 2026, fallback_value: float = 0.0) -> PickAsset:
    """Resolves a ConditionalPick against a joint-trial batch and wraps the
    result as a gradable PickAsset."""
    dist, convey_probability = resolve_conditional_pick(cond, joint_trials)
    protection_note = f", own protection {cond.own_protection_range}" if cond.own_protection_range else ""
    label = (f"{cond.year} {cond.team_code} {cond.round_str} (conveys only if {cond.cond_team_code} "
             f"{cond.cond_round_str} is #{cond.cond_range[0]}-{cond.cond_range[1]}{protection_note}, "
             f"conditional-resolved)")
    years_away = max(0, cond.year - current_year)
    if convey_probability == 0.0:
        return PickAsset(label=label, pick_probabilities={0: 1.0}, convey_probability=0.0,
                          fallback_value=fallback_value, years_away=years_away)
    return PickAsset(
        label=label,
        pick_probabilities=dist,
        protection_range=cond.own_protection_range,
        convey_probability=convey_probability,
        fallback_value=fallback_value,
        years_away=years_away,
    )


# ---------------------------------------------------------------------------
# Nested swaps: "TEAM1/(TEAM2/TEAM3 (Qualifier)) (Qualifier) ROUND" -- a
# 2-level generalization of the flat swap above, where one (or more) of the
# outer group's members is itself a parenthesized flat-swap sub-group
# instead of a bare team code, e.g. "ATL/(CLE/UTA (Less Favorable)) (More
# Favorable) 1st" (the 2028 Atlanta Hawks pick: compare ATL's own pick
# against "the less favorable of CLE/UTA", take the more favorable of
# those two).
#
# DELIBERATELY NOT SUPPORTED: any member carrying its own inline range
# condition (e.g. "DEN (If #6-30)/LAC/OKC (Most Favorable) 1st" -- Denver
# only joins the pool if its own pick is #6-30). Real-world trade language
# uses that same surface syntax for at least two DIFFERENT underlying
# mechanics -- sometimes "the pool shrinks to whoever's left" (the other
# members still swap among themselves), sometimes "the whole fragment
# doesn't convey at all if the condition fails" (a separate, differently
# shaped asset elsewhere covers that case instead) -- and the raw text
# alone doesn't say which. Guessing between those two would risk exactly
# the "plausible-looking but wrong number" this module's docstring warns
# against, so fragments with an inline per-member condition are left
# unresolved (still classified NESTED_OR_ELLIPTICAL) rather than guessed
# at. parse_nested_swap_fragment returns None for any such fragment.
# ---------------------------------------------------------------------------

@dataclass
class TeamLeaf:
    code: str


@dataclass
class SwapGroup:
    members: List[object]      # TeamLeaf | SwapGroup
    qualifier: str


@dataclass
class NestedSwap:
    year: int
    root: SwapGroup
    round_str: str
    protection_range: Optional[Tuple[int, int]] = None
    raw_text: str = ""


# The full fragment, minus its member-list prefix: an optional protection
# clause, the mandatory qualifier clause, the round, and an optional
# trailing protection clause -- in EITHER order (both orderings are
# observed in real data, e.g. "ATL/HOU (If #31-55) (More Favorable) 2nd"
# puts protection first, "MIL/NO (Less Favorable) 1st (If #5-30)" puts it
# last). Non-greedy `members` lets backtracking find the correct split even
# when the member-list itself contains parens (a nested sub-group).
NESTED_SWAP_SUFFIX_RE = re.compile(
    r"^(?P<members>.+?)"
    r"(?:\s*\(If\s*#(?P<plo1>\d+)-(?P<phi1>\d+)\))?"
    r"\s*\((?P<qualifier>[^)]+)\)"
    r"\s*(?P<round>1st|2nd)"
    r"(?:\s*\(If\s*#(?P<plo2>\d+)-(?P<phi2>\d+)\))?"
    r"\s*$"
)

_BARE_TEAM_CODE_RE = re.compile(r"^[A-Z]{2,3}$")
_INNER_GROUP_RE = re.compile(r"^\((?P<sub>.+?)\s*\((?P<q>[^)]+)\)\)$")


def _split_top_level_slash(s: str) -> List[str]:
    """Splits a member-list string on '/' at paren-depth 0 only."""
    parts = []
    depth = 0
    current = ""
    for ch in s:
        if ch == "(":
            depth += 1
        elif ch == ")":
            depth -= 1
        if ch == "/" and depth == 0:
            parts.append(current)
            current = ""
        else:
            current += ch
    parts.append(current)
    return [p for p in parts]


def _parse_member(token: str):
    """Parses one member-list token into a TeamLeaf or SwapGroup. Returns
    None if the token is anything this conservative parser doesn't
    recognize (a bare team code, or a fully-parenthesized nested group with
    its own trailing qualifier) -- notably, a team code carrying its own
    inline condition is REJECTED (returns None), not guessed at (see the
    module note above)."""
    token = token.strip()
    if _BARE_TEAM_CODE_RE.match(token):
        return TeamLeaf(token)

    m = _INNER_GROUP_RE.match(token)
    if m:
        qualifier = m.group("q")
        if qualifier not in QUALIFIER_RANK:
            return None
        sub_tokens = _split_top_level_slash(m.group("sub"))
        sub_nodes = [_parse_member(t) for t in sub_tokens]
        if any(n is None for n in sub_nodes) or len(sub_nodes) < 2:
            return None
        return SwapGroup(sub_nodes, qualifier)

    return None  # anything else (inline condition, malformed, etc.) -- don't guess


def _split_top_level_commas(description: str) -> List[str]:
    """Local copy of pick_resolver._split_top_level, duplicated here (not
    imported) to avoid a circular import -- pick_resolver imports this
    module at load time."""
    parts = []
    depth = 0
    current = ""
    for ch in description:
        if ch == "(":
            depth += 1
        elif ch == ")":
            depth -= 1
        if ch == "," and depth == 0:
            parts.append(current.strip())
            current = ""
        else:
            current += ch
    if current.strip():
        parts.append(current.strip())
    return parts


_CONFIRMED_TRAILING_PROTECTIONS_CACHE = None


def _confirmed_trailing_swap_protections() -> "set":
    """
    Scans EVERY fragment in draft_picks_data.TEAM_FUTURE_PICKS for flat
    swaps using the STANDARD, unambiguous "TEAMLIST (Qualifier) ROUND (If
    #LO-HI)" order -- protection AFTER the qualifier, the same convention
    used everywhere else a protection range appears in this dataset.
    Returns {(frozenset(teams), round_str, (lo, hi))}.

    WHY THIS EXISTS: parse_nested_swap_fragment also accepts the REORDERED
    "TEAMLIST (If #LO-HI) (Qualifier) ROUND" variant (protection BEFORE the
    qualifier), because that's confirmed safe in at least one real case --
    Atlanta's 2031 "ATL/HOU (If #31-55) (More Favorable) 2nd" is confirmed
    by Houston's OWN 2031 fragment, "ATL/HOU (Less Favorable) 2nd (If
    #31-55)", using the unambiguous trailing order for the SAME team
    pair/round/range. But that reordering is syntactically indistinguishable
    from a DIFFERENT, ambiguous pattern: a range gating one specific named
    team's OWN pick (not the swap result) -- e.g. Memphis's 2029 "MEM/ORL
    (If #3-30) (More Favorable) 1st", which Orlando's own complementary
    fragment ("ORL 1st (If #1-2) / MEM/ORL (If #3-30) (Less Favorable)
    1st") strongly suggests is really "ORL's OWN pick, if #3-30" (partitions
    ORL's full 1-30 range against the #1-2 alternative), not a swap-result
    protection. Without a second, differently-ordered sibling fragment
    confirming the swap-result reading, accepting the reordered form would
    risk exactly the "plausible-looking but wrong number" this module's
    docstring warns against -- so parse_nested_swap_fragment only accepts a
    reordered (leading) protection when this function confirms it.
    """
    global _CONFIRMED_TRAILING_PROTECTIONS_CACHE
    if _CONFIRMED_TRAILING_PROTECTIONS_CACHE is not None:
        return _CONFIRMED_TRAILING_PROTECTIONS_CACHE

    from draft_picks_data import TEAM_FUTURE_PICKS
    confirmed = set()
    for _, picks in TEAM_FUTURE_PICKS.items():
        for _, description in picks.items():
            if description.strip() == "(NO PICKS)":
                continue
            for fragment in _split_top_level_commas(description):
                m = FLAT_SWAP_RE.match(fragment.strip())
                if not m:
                    continue
                team_str, qualifier, round_str, lo, hi = m.groups()
                if qualifier not in QUALIFIER_RANK or not (lo and hi):
                    continue
                confirmed.add((frozenset(team_str.split("/")), round_str, (int(lo), int(hi))))
    _CONFIRMED_TRAILING_PROTECTIONS_CACHE = confirmed
    return confirmed


def parse_nested_swap_fragment(year: int, fragment: str) -> Optional[NestedSwap]:
    """
    Attempts to parse a 2-level nested swap (see module note above). Returns
    None if the fragment isn't this shape, or contains anything this
    conservative parser doesn't recognize (an inline per-member condition,
    a 3+-level nesting, malformed parens, an unconfirmed reordered
    protection, etc.) -- caller falls back to classify_unresolved_reason()
    as before.
    """
    fragment = fragment.strip()
    m = NESTED_SWAP_SUFFIX_RE.match(fragment)
    if not m:
        return None

    qualifier = m.group("qualifier")
    if qualifier not in QUALIFIER_RANK:
        return None
    round_str = m.group("round")

    member_tokens = _split_top_level_slash(m.group("members"))
    if len(member_tokens) < 2:
        return None
    members = [_parse_member(t) for t in member_tokens]
    if any(n is None for n in members):
        return None

    lo1, hi1, lo2, hi2 = m.group("plo1"), m.group("phi1"), m.group("plo2"), m.group("phi2")
    if lo1 and hi1 and lo2 and hi2:
        return None  # two protection clauses on one fragment -- not a shape we expect, don't guess
    if lo1 and hi1:
        # Leading (reordered) protection -- only accept if a differently-
        # ordered sibling fragment elsewhere confirms this is really a
        # swap-result protection, not a per-team gate (see
        # _confirmed_trailing_swap_protections' docstring).
        leaf_teams = frozenset(collect_nested_swap_teams(SwapGroup(members, qualifier)))
        if (leaf_teams, round_str, (int(lo1), int(hi1))) not in _confirmed_trailing_swap_protections():
            return None
    lo, hi = (lo1, hi1) if (lo1 and hi1) else (lo2, hi2)
    protection = None
    if lo and hi:
        stated_range = (int(lo), int(hi))
        protection = invert_conveys_range_to_protection(round_str, stated_range)
        if protection is None and stated_range != FULL_RANGE_BY_ROUND[round_str]:
            return None

    return NestedSwap(year=year, root=SwapGroup(members, qualifier), round_str=round_str,
                       protection_range=protection, raw_text=fragment)


def collect_nested_swap_teams(node) -> "set[str]":
    """All leaf team codes referenced anywhere in a SwapGroup/TeamLeaf tree."""
    if isinstance(node, TeamLeaf):
        return {node.code}
    teams: "set[str]" = set()
    for m in node.members:
        teams |= collect_nested_swap_teams(m)
    return teams


def _eval_nested_swap_node(node, round_str: str, joint_trials: Dict[str, Dict[str, List[int]]], i: int) -> int:
    if isinstance(node, TeamLeaf):
        return joint_trials[node.code][round_str][i]
    values = sorted(_eval_nested_swap_node(m, round_str, joint_trials, i) for m in node.members)
    rank = QUALIFIER_RANK[node.qualifier]
    if rank == -1:
        rank = len(values)  # "Less/Least Favorable" = worst of this group
    return values[rank - 1]


def resolve_nested_swap_distribution(swap: NestedSwap, joint_trials: Dict[str, Dict[str, List[int]]]
                                      ) -> Dict[int, float]:
    """Same idea as resolve_swap_distribution, but evaluates the (possibly
    nested) tree per trial instead of a flat team list. joint_trials:
    {team_code: {"1st": [...], "2nd": [...]}} for every leaf team code in
    swap.root (see collect_nested_swap_teams), from the SAME correlated
    batch."""
    needed = collect_nested_swap_teams(swap.root)
    missing = [t for t in needed if t not in joint_trials]
    if missing:
        raise KeyError(f"joint_trials missing required teams: {missing}")

    n_trials = len(joint_trials[next(iter(needed))][swap.round_str])
    for t in needed:
        if len(joint_trials[t][swap.round_str]) != n_trials:
            raise ValueError("joint_trials lists must all be the same length (same trial batch)")
    if n_trials == 0:
        raise ValueError("joint_trials has zero trials")

    counts: Dict[int, int] = {}
    for i in range(n_trials):
        resolved = _eval_nested_swap_node(swap.root, swap.round_str, joint_trials, i)
        counts[resolved] = counts.get(resolved, 0) + 1
    return {pick: count / n_trials for pick, count in counts.items()}


def _describe_nested_swap_node(node) -> str:
    if isinstance(node, TeamLeaf):
        return node.code
    inner = "/".join(_describe_nested_swap_node(m) for m in node.members)
    return f"({inner} {node.qualifier})"


def nested_swap_to_pick_asset(swap: NestedSwap, joint_trials: Dict[str, Dict[str, List[int]]],
                               current_year: int = 2026, fallback_value: float = 0.0) -> PickAsset:
    """Resolves a NestedSwap against a joint-trial batch and wraps the
    result as a gradable PickAsset."""
    dist = resolve_nested_swap_distribution(swap, joint_trials)
    desc = "/".join(_describe_nested_swap_node(m) for m in swap.root.members)
    label = f"{swap.year} {desc} ({swap.root.qualifier}) {swap.round_str} (nested swap-resolved)"
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
