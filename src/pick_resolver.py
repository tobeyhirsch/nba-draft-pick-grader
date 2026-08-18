"""
Converts the raw pick-description strings in draft_picks_data.py into
pick_grading.PickAsset objects wherever that's actually safe to do
mechanically, and leaves everything else as flagged, unresolved text with an
explanation of what's blocking it.

THREE TIERS a fragment can resolve to (checked in this order):

  1. SIMPLE -- a single team's pick, no swap language. Either already known
     ("BOS 1st (#27)") or a bare future pick ("BOS 1st"), optionally with a
     numeric protection range ("MIA 1st (If #1-14)"). No joint/correlated
     simulation needed -- one team's own marginal pick distribution is
     enough (see standings_sim / draft_pipeline_321's monte-carlo
     functions).

  2. SWAP -- a flat "TEAM1/TEAM2[/TEAM3[/TEAM4]] (Qualifier) ROUND [(If
     #A-B)]" comparison among 2-4 teams' SAME-fragment picks (e.g. "MIL/NO
     (Less Favorable) 1st (If #5-30)"). Parsed and resolved via
     swap_resolver.py, which requires a real league (teams_for_simulation)
     to run the correlated joint trials that this genuinely needs -- see
     swap_resolver.py's module docstring for why marginal distributions
     alone would give a wrong answer here.

  3. UNRESOLVED -- everything else (cross-pick conditionals that depend on
     a DIFFERENT pick's outcome, nested/elliptical swap language, ambiguous
     annotations, or a resolvable shape that just wasn't given a
     simulation league to run against). Returned with a reason string
     rather than guessed at -- see swap_resolver.classify_unresolved_reason
     for the taxonomy.

This conservative, tiered approach is deliberate: a plausible-looking but
wrong pick value is worse than an honest "not resolved yet, and here's
exactly why."
"""

import re
from typing import Dict, List, Optional, Sequence, Tuple

from draft_picks_data import TEAM_FUTURE_PICKS
from pick_grading import PickAsset
from team_codes import TEAM_ABBREV_TO_NAME
from swap_resolver import (
    SwapPick,
    classify_unresolved_reason,
    invert_conveys_range_to_protection,
    parse_swap_fragment,
    swap_to_pick_asset,
)

# Bare pick, optionally with a resolved slot: "BOS 1st", "BOS 2nd (#40)".
SIMPLE_PICK_RE = re.compile(
    r"^([A-Z]{2,3})\s+(1st|2nd)(?:\s*\(#(\d+)\))?$"
)

# A single team's future pick with ONLY a numeric protection range, no swap:
# "DAL 1st (If #3-30)", "MIA 1st (If #1-14)".
SIMPLE_PROTECTED_RE = re.compile(
    r"^([A-Z]{2,3})\s+(1st|2nd)\s*\(If\s*#(\d+)-(\d+)\)$"
)

# (year, team_code, round_str, known_pick_number_or_None, protection_range_or_None)
SimplePick = Tuple[int, str, str, Optional[int], Optional[Tuple[int, int]]]
# (year, raw_fragment_text, human_readable_reason)
UnresolvedEntry = Tuple[int, str, str]


def _split_top_level(description: str) -> List[str]:
    """Splits a comma-separated pick description, ignoring commas inside parentheses."""
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


def classify_team_picks(team_name: str) -> Tuple[List[SimplePick], List[SwapPick], List[UnresolvedEntry]]:
    """
    Returns (simple_picks, swap_picks, unresolved):
      simple_picks: single-team picks (known slot, bare future pick, or
        future pick with only a numeric protection range) -- see SimplePick.
      swap_picks: flat N-way swap comparisons, parsed but NOT yet resolved
        to a distribution -- resolving needs a real league, done in
        build_pick_assets().
      unresolved: anything that doesn't fit either tier, with a reason.
    """
    if team_name not in TEAM_FUTURE_PICKS:
        raise KeyError(f"{team_name!r} not found in TEAM_FUTURE_PICKS")

    simple_picks: List[SimplePick] = []
    swap_picks: List[SwapPick] = []
    unresolved: List[UnresolvedEntry] = []

    for year, description in TEAM_FUTURE_PICKS[team_name].items():
        if description.strip() == "(NO PICKS)":
            continue
        for fragment in _split_top_level(description):
            m = SIMPLE_PICK_RE.match(fragment)
            if m:
                team_code, round_str, pick_num = m.groups()
                simple_picks.append((year, team_code, round_str,
                                      int(pick_num) if pick_num else None, None))
                continue

            m = SIMPLE_PROTECTED_RE.match(fragment)
            if m:
                team_code, round_str, lo, hi = m.groups()
                protection = invert_conveys_range_to_protection(round_str, (int(lo), int(hi)))
                if protection is not None:
                    simple_picks.append((year, team_code, round_str, None, protection))
                    continue
                unresolved.append((year, fragment,
                                    "protection range spans the whole round or isn't edge-anchored "
                                    "-- can't be represented as a single protection window"))
                continue

            swap = parse_swap_fragment(year, fragment)
            if swap:
                swap_picks.append(swap)
                continue

            unresolved.append((year, fragment, classify_unresolved_reason(fragment).value))

    return simple_picks, swap_picks, unresolved


def build_pick_assets(team_name: str,
                       teams_for_simulation: Optional[Sequence] = None,
                       team_distributions: Optional[Dict[str, Dict[int, float]]] = None,
                       trials: int = 5000,
                       seed: int = None,
                       current_year: int = 2026,
                       fallback_value: float = 0.0,
                       history: Optional[Dict[str, List[int]]] = None
                       ) -> Tuple[List[PickAsset], List[UnresolvedEntry]]:
    """
    teams_for_simulation: the real 30-team league (standings_sim.Team
        objects, keyed by full name -- e.g. from team_wins.build_teams() or
        a market-win-total calibration). When given, this function runs ONE
        shared batch of correlated joint trials
        (draft_pipeline_321.joint_pick_number_trials) covering every team
        code this portfolio actually needs -- both this team's own future
        picks AND every team referenced in any of its swaps -- so swap
        comparisons use real correlated outcomes rather than independent
        marginals, and simple future picks get a real simulated
        distribution "for free" from the same run.

    team_distributions: optional {team_code: {pick_number: probability}}
        override/fallback for simple (non-swap) future picks, e.g. if you
        already have marginals computed elsewhere and don't want to re-run
        a simulation. Does NOT help resolve swaps (those need the joint,
        correlated version) -- pass teams_for_simulation for those.

    history: optional pick-restrictions state (pick_restrictions_321.py),
        e.g. pick_restrictions_321.DEFAULT_2027_HISTORY to enforce the real
        "no repeat #1 / no 3-straight top-5" restrictions -- seeded from
        actual 2025-2026 results. Has no effect if teams_for_simulation
        isn't given. IMPORTANT SCOPING: this pipeline doesn't model
        multi-year evolving team strength -- every future year's pick
        distribution for a team is drawn from the same one-season
        simulation (current ratings), only time-discounted via years_away.
        `history` is only factually grounded for the 2027 draft specifically
        (that's the only year with a real, known restriction carry-in), so
        it's applied ONLY to fragments whose year == 2027; every other
        year's fragments always use the unrestricted distribution, even if
        they share a team code with a 2027 fragment in the same portfolio.
        This costs a second joint_pick_number_trials batch (same seed, so
        it only actually diverges from the unrestricted batch on the trials
        where a restriction bites -- see pick_restrictions_321.py).

    Returns (assets, unresolved) -- assets are ready to grade via
    pick_grading.grade_pick_portfolio(); unresolved lists everything that
    still needs a simulation league, multi-year modeling, or manual
    judgment, each with a reason.
    """
    simple_picks, swap_picks, unresolved = classify_team_picks(team_name)
    unresolved = list(unresolved)  # copy -- we'll append to it
    assets: List[PickAsset] = []

    needed_codes = {code for _, code, _, pick_num, _ in simple_picks if pick_num is None}
    for swap in swap_picks:
        needed_codes.update(swap.teams)

    # {code: {"1st": [...], "2nd": [...]}} -- round-aware, see
    # draft_pipeline_321.joint_pick_number_trials's docstring for why this
    # can't be flattened to one list per team (a team's 1st- and 2nd-round
    # pick numbers are different values every trial, not interchangeable).
    joint_by_code: Dict[str, Dict[str, List[int]]] = {}
    # Second, history-restricted batch -- ONLY used for year-2027 fragments.
    # See build_pick_assets' `history` docstring for why 2027 is special-cased
    # rather than applying restrictions to every year.
    joint_by_code_2027: Dict[str, Dict[str, List[int]]] = {}
    if teams_for_simulation and needed_codes:
        bad_codes = [c for c in needed_codes if c not in TEAM_ABBREV_TO_NAME]
        if bad_codes:
            raise KeyError(f"Unknown team code(s), no full-name mapping in team_codes.py: {bad_codes}")
        needed_names = [TEAM_ABBREV_TO_NAME[c] for c in sorted(needed_codes)]
        from draft_pipeline_321 import joint_pick_number_trials  # local import avoids a hard dependency for callers who only need marginals
        joint = joint_pick_number_trials(teams_for_simulation, needed_names, trials=trials, seed=seed)
        joint_by_code = {c: joint[TEAM_ABBREV_TO_NAME[c]] for c in needed_codes}
        if history is not None:
            joint_2027 = joint_pick_number_trials(teams_for_simulation, needed_names, trials=trials,
                                                    seed=seed, history=history)
            joint_by_code_2027 = {c: joint_2027[TEAM_ABBREV_TO_NAME[c]] for c in needed_codes}

    def marginal_distribution_for(code: str, round_str: str, year: int) -> Optional[Dict[int, float]]:
        table = joint_by_code_2027 if (year == 2027 and code in joint_by_code_2027) else joint_by_code
        if code in table:
            picks = table[code][round_str]
            n = len(picks)
            counts: Dict[int, int] = {}
            for p in picks:
                counts[p] = counts.get(p, 0) + 1
            return {p: c / n for p, c in counts.items()}
        if team_distributions and code in team_distributions:
            return team_distributions[code]
        return None

    # --- Tier 1: simple picks (known slot, bare future, or protected future) ---
    for year, team_code, round_str, pick_num, protection_range in simple_picks:
        years_away = max(0, year - current_year)

        if pick_num is not None:
            label = f"{year} {team_code} {round_str} (#{pick_num})"
            assets.append(PickAsset(label, pick_number=pick_num, years_away=years_away))
            continue

        dist = marginal_distribution_for(team_code, round_str, year)
        if dist is None:
            protection_note = f", protection {protection_range}" if protection_range else ""
            unresolved.append((year, f"{team_code} {round_str}{protection_note}",
                                f"future pick, unresolved -- needs {team_code}'s simulated "
                                f"pick distribution (pass teams_for_simulation or team_distributions)"))
            continue

        protection_note = f" (protected, doesn't convey #{protection_range[0]}-{protection_range[1]})" \
            if protection_range else ""
        label = f"{year} {team_code} {round_str}{protection_note}"
        assets.append(PickAsset(label, pick_probabilities=dist,
                                 protection_range=protection_range,
                                 fallback_value=fallback_value,
                                 years_away=years_away))

    # --- Tier 2: swaps (need the joint/correlated distributions above) ---
    for swap in swap_picks:
        if not all(t in joint_by_code for t in swap.teams):
            unresolved.append((swap.year, swap.raw_text,
                                "swap parsed but no simulation league was provided "
                                "(pass teams_for_simulation to resolve it)"))
            continue
        # Slice each team's joint trials down to the ROUND this swap actually
        # concerns (swap.round_str) -- swap.teams' picks in the OTHER round
        # are a different, uncorrelated-for-this-purpose number and must not
        # be mixed in. Use the history-restricted batch only for year-2027
        # swaps (see build_pick_assets' `history` docstring).
        use_2027 = swap.year == 2027 and all(t in joint_by_code_2027 for t in swap.teams)
        source = joint_by_code_2027 if use_2027 else joint_by_code
        round_trials = {t: source[t][swap.round_str] for t in swap.teams}
        assets.append(swap_to_pick_asset(swap, round_trials, current_year=current_year,
                                          fallback_value=fallback_value))

    return assets, unresolved


if __name__ == "__main__":
    print("=== Tier breakdown across all 30 teams (no simulation league) ===")
    totals = {"simple": 0, "swap_parsed": 0, "unresolved": 0}
    reason_counts: Dict[str, int] = {}
    for team in TEAM_FUTURE_PICKS:
        simple, swaps, unresolved = classify_team_picks(team)
        totals["simple"] += len(simple)
        totals["swap_parsed"] += len(swaps)
        totals["unresolved"] += len(unresolved)
        for _, _, reason in unresolved:
            reason_counts[reason] = reason_counts.get(reason, 0) + 1

    print(f"Simple (known slot, bare future, or protected future): {totals['simple']}")
    print(f"Swap fragments parsed (need a simulation league to resolve): {totals['swap_parsed']}")
    print(f"Still unresolved: {totals['unresolved']}")
    print("\nUnresolved breakdown by reason:")
    for reason, count in sorted(reason_counts.items(), key=lambda kv: -kv[1]):
        print(f"  {count:>3}  {reason}")

    print("\n\n=== Detail for three example teams (no simulation league in this demo) ===")
    for team in ["Boston Celtics", "Atlanta Hawks", "Cleveland Cavaliers"]:
        assets, unresolved = build_pick_assets(team)
        print(f"\n--- {team} ---")
        print(f"Auto-gradable now (known slots only, no league passed in): {len(assets)}")
        for a in assets:
            g = a.grade()
            print(f"  {g['label']:<40} grade={g['grade']:.1f} ({g['grade_label']})")
        print(f"Needs a simulation league or manual resolution: {len(unresolved)}")
        for year, text, reason in unresolved[:5]:
            print(f"  {year}: {text}  [{reason}]")
        if len(unresolved) > 5:
            print(f"  ... and {len(unresolved) - 5} more")
