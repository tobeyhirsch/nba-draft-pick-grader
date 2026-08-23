"""
Resolves ACTUAL, per-trial pick ownership -- who really ends up with each of
the 60 picks in a given draft year, in ONE specific simulated world/trial --
from draft_picks_data.py's raw ownership/swap/protection/conditional text.
This is the missing link between "team X earned pick #7 by its own record"
and "team Y is the one who actually gets to make that selection," per the
real trades, protections, and conditional chains on file.

WHY THIS IS A SEPARATE MODULE FROM pick_resolver.py / swap_resolver.py:
Those two build PROBABILISTIC pick_grading.PickAsset objects -- a
{pick_number: probability} distribution aggregated across many simulated
seasons, for grading one team's pick portfolio in isolation. This module
answers a different, single-trial question that sequential_league_sim.py
needs: given ONE concrete simulated season's actual pick numbers for all 30
teams (one trial, already drawn), which team actually walks away with each
pick, right now, this trial? It does not reimplement any parsing or
swap-comparison logic -- it reuses the exact same fragment-parsing and
per-trial evaluators pick_resolver.py/swap_resolver.py already have
(SIMPLE_PICK_RE / SIMPLE_PROTECTED_RE / _split_top_level from
pick_resolver.py; parse_swap_fragment / parse_conditional_pick_fragment /
parse_nested_swap_fragment / _eval_nested_swap_node from swap_resolver.py,
the last of which already evaluates ONE trial at a time internally -- it's
just called here with a single-element trial list instead of a batch).

SCOPE -- matches pick_resolver.py's/swap_resolver.py's existing resolvable
tiers exactly, no more, no less:
  RESOLVED: simple/bare picks, protection-only picks, flat swaps (2-5
    teams), same-year cross-pick conditionals, 2-level nested swaps.
  NOT RESOLVED (same reasons as swap_resolver.classify_unresolved_reason):
    cross-YEAR conditionals, nested/elliptical continuations (including any
    fragment where an individual swap member carries its own inline
    condition, e.g. Boston's 2028 first-round language -- deliberately
    unsupported, see swap_resolver.py's module note), ambiguous
    annotations, unrecognized text. An unresolved fragment credits NOBODY
    for that specific pick this trial -- conservative, matching this
    pipeline's "don't guess" philosophy throughout -- rather than falling
    back to crediting the natural-slot team, which risks silently
    double-counting against a complementary fragment elsewhere that DOES
    resolve (see the Miami/Charlotte top-14-protection example in
    swap_resolver.invert_conveys_range_to_protection's docstring: Miami's
    own entry and Charlotte's entry are two DIFFERENT fragments that
    partition the same physical pick; guessing a default on top of that
    would double it).

    Worth noting for future work: because sequential_league_sim.py now
    simulates every year 2027-2033 sequentially within one world, a
    cross-YEAR conditional (e.g. "MIA 1st (If 2027 MIA 1st is #15-30)"
    appearing under some team's 2028 entry) is no longer fundamentally
    unresolvable the way it is for the rest of this pipeline (which
    simulates each year independently) -- this module still doesn't
    attempt it, to keep this change scoped to "the same logic the rest of
    the model already uses," but a future pass could look up the earlier
    year's actual realized result from the same world's history and
    resolve these too.

FRAGMENTS ARE PARSED ONCE, NOT PER TRIAL: draft_picks_data.py's text is
static -- only the realized pick numbers change trial to trial. See
parsed_fragments_by_year() / _build_parsed_cache().

DOUBLE-COUNTING CHECK: run `python3 pick_ownership_resolver.py` -- it
resolves ownership against many random synthetic pick-number assignments
(standing in for many different simulated seasons) and confirms no single
(team_code, round, year) natural pick ever gets credited to more than one
receiving team in the same trial, i.e. the resolvable fragments partition
cleanly. Also reports coverage: how many of the 420 team-round-year natural
pick slots (30 teams x 2 rounds x 7 years) get credited to SOMEONE across
those trials vs. never appear in any resolvable fragment.
"""

import random
from typing import Dict, List, Optional, Tuple, Union

from draft_picks_data import TEAM_FUTURE_PICKS
from pick_resolver import SIMPLE_PICK_RE, SIMPLE_PROTECTED_RE, _split_top_level
from swap_resolver import (
    BARE_RANGE_PROTECTED_RE,
    ConditionalPick,
    NestedSwap,
    SwapPick,
    _eval_nested_swap_node,
    classify_unresolved_reason,
    collect_nested_swap_teams,
    invert_conveys_range_to_protection,
    parse_conditional_pick_fragment,
    parse_nested_swap_fragment,
    parse_swap_fragment,
)


class SimpleFragment:
    """A single team's pick, no swap: a bare own/acquired pick, optionally
    with a numeric protection range (protection_range=None -> unconditional;
    otherwise the range in which it does NOT convey, matching
    pick_grading.PickAsset's convention)."""
    __slots__ = ("team_code", "round_str", "known_pick_num", "protection_range")

    def __init__(self, team_code: str, round_str: str, known_pick_num: Optional[int],
                 protection_range: Optional[Tuple[int, int]]):
        self.team_code = team_code
        self.round_str = round_str
        self.known_pick_num = known_pick_num
        self.protection_range = protection_range


ParsedFragment = Union[SimpleFragment, SwapPick, ConditionalPick, NestedSwap]

_PARSED_CACHE: Optional[Dict[int, List[Tuple[str, ParsedFragment]]]] = None
_UNRESOLVED_CACHE: Optional[List[Tuple[int, str, str, str]]] = None


def _parse_fragment(year: int, fragment: str) -> Tuple[Optional[ParsedFragment], Optional[str]]:
    """Returns (parsed, None) on success, or (None, reason) otherwise.
    Mirrors pick_resolver.classify_team_picks's tier order exactly."""
    m = SIMPLE_PICK_RE.match(fragment)
    if m:
        team_code, round_str, pick_num = m.groups()
        return SimpleFragment(team_code, round_str, int(pick_num) if pick_num else None, None), None

    m = SIMPLE_PROTECTED_RE.match(fragment)
    if m:
        team_code, round_str, lo, hi = m.groups()
        protection = invert_conveys_range_to_protection(round_str, (int(lo), int(hi)))
        if protection is not None:
            return SimpleFragment(team_code, round_str, None, protection), None
        return None, ("protection range spans the whole round or isn't edge-anchored "
                       "-- can't be represented as a single protection window")

    m = BARE_RANGE_PROTECTED_RE.match(fragment)
    if m:
        team_code, round_str, lo, hi = m.groups()
        protection = invert_conveys_range_to_protection(round_str, (int(lo), int(hi)))
        if protection is not None:
            return SimpleFragment(team_code, round_str, None, protection), None
        # falls through to the tiers below, same as pick_resolver.py

    cond = parse_conditional_pick_fragment(year, fragment)
    if cond:
        return cond, None

    swap = parse_swap_fragment(year, fragment)
    if swap:
        return swap, None

    nested = parse_nested_swap_fragment(year, fragment)
    if nested:
        return nested, None

    return None, classify_unresolved_reason(fragment).value


def _build_parsed_cache() -> None:
    global _PARSED_CACHE, _UNRESOLVED_CACHE
    parsed_by_year: Dict[int, List[Tuple[str, ParsedFragment]]] = {}
    unresolved: List[Tuple[int, str, str, str]] = []
    for team_name, by_year in TEAM_FUTURE_PICKS.items():
        for year, description in by_year.items():
            if description.strip() == "(NO PICKS)":
                continue
            for fragment in _split_top_level(description):
                parsed, reason = _parse_fragment(year, fragment)
                if parsed is not None:
                    parsed_by_year.setdefault(year, []).append((team_name, parsed))
                else:
                    unresolved.append((year, team_name, fragment, reason))
    _PARSED_CACHE = parsed_by_year
    _UNRESOLVED_CACHE = unresolved


def parsed_fragments_by_year() -> Dict[int, List[Tuple[str, ParsedFragment]]]:
    """{year: [(receiving_team_name, parsed_fragment), ...]}, computed once
    and cached (draft_picks_data.py's text never changes mid-run)."""
    if _PARSED_CACHE is None:
        _build_parsed_cache()
    return _PARSED_CACHE


def unresolved_fragments() -> List[Tuple[int, str, str, str]]:
    """[(year, receiving_team_name, raw_fragment, reason), ...] for every
    fragment this module can't resolve -- see module docstring's SCOPE
    section. Credited to nobody in resolve_pick_ownership_for_year()."""
    if _UNRESOLVED_CACHE is None:
        _build_parsed_cache()
    return _UNRESOLVED_CACHE


def _within(protection_range: Optional[Tuple[int, int]], value: int) -> bool:
    """True if `value` CONVEYS -- protection_range is the does-NOT-convey
    range (pick_grading.PickAsset's convention), so None always conveys."""
    if protection_range is None:
        return True
    lo, hi = protection_range
    return not (lo <= value <= hi)


def resolve_pick_ownership_for_year(pick_numbers_by_code: Dict[str, Dict[str, int]], year: int
                                     ) -> Dict[str, List[Tuple[int, str]]]:
    owned, _conflicts = _resolve_with_conflicts(pick_numbers_by_code, year)
    return owned


def _resolve_with_conflicts(pick_numbers_by_code: Dict[str, Dict[str, int]], year: int
                             ) -> Tuple[Dict[str, List[Tuple[int, str]]], List[Tuple[str, str, List[str]]]]:
    """
    pick_numbers_by_code: {team_code: {"1st": pick_number, "2nd": pick_number}}
    for all 30 teams, from ONE simulated season (this trial -- one year,
    one world, already drawn by draft_pipeline_321._simulate_321_draft_core
    + simulate_second_round_order).

    Returns {receiving_team_name: [(pick_number, round_str), ...]} -- every
    pick that team actually ends up owning this trial, per real trade/
    protection/swap/conditional data (TEAM_FUTURE_PICKS keys are already
    full team names, so this dict's keys match exactly). A team can own 0,
    1, or several picks in a round once trades are accounted for. A pick
    whose fate depends on an unresolved fragment (see module docstring) is
    credited to nobody -- see unresolved_fragments() to inspect those.

    CONFLICTING CLAIMS: draft_picks_data.py's raw text is occasionally NOT a
    clean partition -- e.g. Toronto's 2029 entry unconditionally lists "TOR
    1st" (their own kept pick) while the LA Clippers' 2029 entry ALSO
    unconditionally lists "TOR 1st"; Indiana's and Portland's 2029 entries
    both list the identical "IND/WAS (Less Favorable) 2nd" swap fragment.
    These read as genuine same-physical-pick conflicts in the source data
    (LD Sport's per-team pages aren't guaranteed mutually exclusive -- a
    team can be shown a pick it has a swap RIGHT to without that meaning it
    receives the asset outright), not a parsing bug -- confirmed by running
    this module directly (`python3 pick_ownership_resolver.py`), which
    checks every resolvable fragment against hundreds of synthetic trials
    and reports exactly which (team, round, year) triples get claimed by
    more than one receiving team. When two OR MORE different teams both
    resolve a claim on the exact same underlying (source team, round) pick
    in the SAME trial, this function credits NEITHER -- same "don't guess"
    philosophy as an unresolved fragment -- rather than arbitrarily picking
    one side of a conflict the source data itself doesn't disambiguate.
    """
    # (receiving_team, pick_number, round_str, source_team_code) for every
    # fragment that conveys this trial -- source is resolved per-tier so
    # conflicting claims on the SAME physical pick can be detected below,
    # even when they arrive via different fragment shapes (e.g. one team's
    # bare "TOR 1st" vs. another's identical bare "TOR 1st").
    candidates: List[Tuple[str, int, str, str]] = []

    for team_name, parsed in parsed_fragments_by_year().get(year, []):
        if isinstance(parsed, SimpleFragment):
            if parsed.known_pick_num is not None:
                candidates.append((team_name, parsed.known_pick_num, parsed.round_str, parsed.team_code))
                continue
            actual = pick_numbers_by_code[parsed.team_code][parsed.round_str]
            if _within(parsed.protection_range, actual):
                candidates.append((team_name, actual, parsed.round_str, parsed.team_code))

        elif isinstance(parsed, SwapPick):
            trial_picks = sorted(pick_numbers_by_code[t][parsed.round_str] for t in parsed.teams)
            resolved = trial_picks[parsed.rank - 1]
            if _within(parsed.protection_range, resolved):
                source = next(t for t in parsed.teams if pick_numbers_by_code[t][parsed.round_str] == resolved)
                candidates.append((team_name, resolved, parsed.round_str, source))

        elif isinstance(parsed, ConditionalPick):
            cond_val = pick_numbers_by_code[parsed.cond_team_code][parsed.cond_round_str]
            lo, hi = parsed.cond_range
            if lo <= cond_val <= hi:
                target_val = pick_numbers_by_code[parsed.team_code][parsed.round_str]
                if _within(parsed.own_protection_range, target_val):
                    candidates.append((team_name, target_val, parsed.round_str, parsed.team_code))

        elif isinstance(parsed, NestedSwap):
            needed = collect_nested_swap_teams(parsed.root)
            joint_trials = {code: {parsed.round_str: [pick_numbers_by_code[code][parsed.round_str]]}
                             for code in needed}
            resolved = _eval_nested_swap_node(parsed.root, parsed.round_str, joint_trials, 0)
            if _within(parsed.protection_range, resolved):
                source = next(t for t in needed if pick_numbers_by_code[t][parsed.round_str] == resolved)
                candidates.append((team_name, resolved, parsed.round_str, source))

    # Group by the physical pick (source team, round) and drop any group
    # claimed by more than one DISTINCT receiving team -- a genuine
    # conflict in the source data, not something to guess a winner for.
    by_source: Dict[Tuple[str, str], List[Tuple[str, int]]] = {}
    for receiving_team, pick_num, round_str, source_code in candidates:
        by_source.setdefault((source_code, round_str), []).append((receiving_team, pick_num))

    owned: Dict[str, List[Tuple[int, str]]] = {name: [] for name in TEAM_FUTURE_PICKS}
    conflicts: List[Tuple[str, str, List[str]]] = []
    for (source_code, round_str), claims in by_source.items():
        distinct_receivers = {receiving_team for receiving_team, _ in claims}
        if len(distinct_receivers) > 1:
            conflicts.append((source_code, round_str, sorted(distinct_receivers)))
            continue  # conflicting claims on the same physical pick -- credit nobody
        receiving_team, pick_num = claims[0]  # all entries agree; dedupe multi-fragment repeats
        owned[receiving_team].append((pick_num, round_str))

    return owned, conflicts


if __name__ == "__main__":
    from team_codes import TEAM_ABBREV_TO_NAME

    codes = sorted(TEAM_ABBREV_TO_NAME)
    rng = random.Random(7)

    print(f"Parsed fragments: {sum(len(v) for v in parsed_fragments_by_year().values())} resolvable, "
          f"{len(unresolved_fragments())} unresolved, across {len(parsed_fragments_by_year())} years.")

    reason_counts: Dict[str, int] = {}
    for _, _, _, reason in unresolved_fragments():
        reason_counts[reason] = reason_counts.get(reason, 0) + 1
    print("\nUnresolved breakdown by reason:")
    for reason, count in sorted(reason_counts.items(), key=lambda kv: -kv[1]):
        print(f"  {count:>3}  {reason}")

    print("\n=== Conflict rate + coverage check across 500 random synthetic trials ===")
    years = sorted(TEAM_FUTURE_PICKS["Atlanta Hawks"].keys())
    claimed_ever: set = set()
    all_slots = {(code, rnd, year) for code in codes for rnd in ("1st", "2nd") for year in years}
    conflict_pairs_seen: set = set()  # (source_code, round_str, year) that conflicted at least once
    conflict_events = 0
    post_fix_duplicate_events = 0  # sanity check: should stay exactly 0
    total_trials = 500

    for _ in range(total_trials):
        for year in years:
            order1 = codes[:]
            order2 = codes[:]
            rng.shuffle(order1)
            rng.shuffle(order2)
            round1_pick = {code: i + 1 for i, code in enumerate(order1)}
            round2_pick = {code: 31 + j for j, code in enumerate(order2)}
            pick_numbers_by_code = {
                code: {"1st": round1_pick[code], "2nd": round2_pick[code]} for code in codes
            }
            owned, conflicts = _resolve_with_conflicts(pick_numbers_by_code, year)
            conflict_events += len(conflicts)
            for source_code, round_str, _claimants in conflicts:
                conflict_pairs_seen.add((source_code, round_str, year))

            # sanity check: post-fix, no physical pick should ever be
            # credited to more than one receiving team.
            source_by_pick = {"1st": {}, "2nd": {}}
            for code, d in pick_numbers_by_code.items():
                source_by_pick["1st"][d["1st"]] = code
                source_by_pick["2nd"][d["2nd"]] = code
            claims: Dict[Tuple[str, str], List[str]] = {}
            for receiving_team, picks in owned.items():
                for pick_num, round_str in picks:
                    source_code = source_by_pick[round_str][pick_num]
                    claims.setdefault((source_code, round_str), []).append(receiving_team)
                    claimed_ever.add((source_code, round_str, year))
            for (source_code, round_str), claimants in claims.items():
                if len(claimants) > 1:
                    post_fix_duplicate_events += 1

    never_claimed = all_slots - claimed_ever
    print(f"Post-fix duplicate-credit events across {total_trials} trials x {len(years)} years: "
          f"{post_fix_duplicate_events} ({'CLEAN' if post_fix_duplicate_events == 0 else 'BUG -- investigate'})")
    print(f"Distinct (source team, round, year) triples that showed a genuine conflict in the raw "
          f"data at least once: {len(conflict_pairs_seen)}")
    for source_code, round_str, year in sorted(conflict_pairs_seen, key=lambda x: (x[2], x[0], x[1])):
        print(f"  {year} {source_code} {round_str}")
    print(f"Natural pick-slots (team, round, year) credited to someone in at least one trial: "
          f"{len(claimed_ever)} / {len(all_slots)}")
    if never_claimed:
        print(f"Never claimed by any resolvable fragment in {total_trials} trials "
              f"(either always unresolved, always conflicting, or genuinely never owned by "
              f"anyone in the data): {len(never_claimed)}")
