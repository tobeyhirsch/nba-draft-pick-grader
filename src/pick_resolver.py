"""
Converts the raw pick-description strings in draft_picks_data.py into
pick_grading.PickAsset objects wherever that's actually safe to do
mechanically, and leaves everything else as flagged, unresolved text.

CLASSIFICATION RULE (deliberately conservative):
A pick fragment is treated as "simple" (auto-convertible) ONLY if it
matches `TEAM 1st` or `TEAM 2nd`, optionally with a resolved `(#N)` slot --
i.e. a single team's pick with no "If," "Better/Worse/Most/Least Favorable,"
"Best of," "Worst of," or "/" swap language. Anything else is left in
`conditional_raw` rather than guessed at, because guessing at swap
resolution silently would produce a plausible-looking but likely WRONG
number -- these genuinely depend on the joint outcome of two or three
teams' seasons, which only draft_pipeline_321.py's Monte Carlo can resolve
correctly (see draft_picks_data.py's module docstring for the reasoning).

WHAT THIS MEANS FOR A GIVEN TEAM'S OUTPUT:
- Already-happened 2026 picks with a `(#N)` are graded as KNOWN picks
  (pick_number set directly, grade near 10 or near 1 depending on slot).
- Simple future firsts/seconds with no swap language ("BOS 1st", "CHI 2nd")
  are graded using that team's OWN simulated pick distribution from
  draft_pipeline_321.py -- pass `team_distributions` in to enable this;
  without it, they fall back to a flat "unresolved -- own future pick"
  placeholder value.
- Conditional/swap picks are returned separately in `conditional_raw`,
  labeled with which teams and years are involved, so you can see exactly
  what's NOT being graded automatically and decide how to handle each one
  (the honest options are: (a) wait until the condition resolves, (b) run
  a joint Monte Carlo across the specific teams involved and take
  whichever pick the swap language selects each trial, or (c) make an
  explicit manual judgment call and grade it with a manual PickAsset).
"""

import re
from typing import Dict, List, Optional, Tuple

from draft_picks_data import TEAM_FUTURE_PICKS
from pick_grading import PickAsset

SIMPLE_PICK_RE = re.compile(
    r"^([A-Z]{2,3})\s+(1st|2nd)(?:\s*\(#(\d+)\))?$"
)

UNRESOLVED_FUTURE_OWN_PLACEHOLDER_VALUE = None  # see note below


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


def classify_team_picks(team_name: str) -> Tuple[List[Tuple[int, str, str, Optional[int]]], List[Tuple[int, str]]]:
    """
    Returns (simple_picks, conditional_raw):
      simple_picks: list of (year, owning_team_code, round_str, known_pick_number_or_None)
      conditional_raw: list of (year, raw_fragment_text) for anything NOT auto-resolvable
    """
    if team_name not in TEAM_FUTURE_PICKS:
        raise KeyError(f"{team_name!r} not found in TEAM_FUTURE_PICKS")

    simple_picks = []
    conditional_raw = []

    for year, description in TEAM_FUTURE_PICKS[team_name].items():
        if description.strip() == "(NO PICKS)":
            continue
        for fragment in _split_top_level(description):
            match = SIMPLE_PICK_RE.match(fragment)
            if match:
                team_code, round_str, pick_num = match.groups()
                simple_picks.append((year, team_code, round_str, int(pick_num) if pick_num else None))
            else:
                conditional_raw.append((year, fragment))

    return simple_picks, conditional_raw


def build_pick_assets(team_name: str,
                       team_distributions: Optional[Dict[str, Dict[int, float]]] = None,
                       current_year: int = 2026) -> Tuple[List[PickAsset], List[Tuple[int, str]]]:
    """
    team_distributions: optional {team_code: {pick_number: probability}} --
        pass this in (built from draft_pipeline_321.monte_carlo_321_pick_distribution
        + pick_valuation.distribution_from_counts) to grade a team's simple,
        unconditional FUTURE picks using real simulated odds instead of a
        placeholder. Without it, unresolved future picks are returned with
        no PickAsset (see the returned conditional_raw-style gap) rather
        than a guessed number.

    Returns (assets, conditional_raw) -- assets are ready to grade via
    pick_grading.grade_pick_portfolio(); conditional_raw lists everything
    that still needs manual/simulator resolution, unchanged.
    """
    simple_picks, conditional_raw = classify_team_picks(team_name)
    assets: List[PickAsset] = []
    skipped_unresolved: List[Tuple[int, str]] = []

    for year, team_code, round_str, pick_num in simple_picks:
        years_away = max(0, year - current_year)
        label = f"{year} {team_code} {round_str}" + (f" (#{pick_num})" if pick_num else "")

        if pick_num is not None:
            # Already resolved (this year's draft has happened) -- known slot.
            assets.append(PickAsset(label, pick_number=pick_num, years_away=years_away))
            continue

        if team_distributions and team_code in team_distributions:
            assets.append(PickAsset(label, pick_probabilities=team_distributions[team_code],
                                     years_away=years_away))
            continue

        # No known slot and no simulated distribution available -- don't guess.
        skipped_unresolved.append((year, f"{team_code} {round_str} (future, unresolved -- "
                                          f"needs {team_code}'s simulated pick distribution)"))

    return assets, conditional_raw + skipped_unresolved


if __name__ == "__main__":
    for team in ["Boston Celtics", "Atlanta Hawks", "Cleveland Cavaliers"]:
        assets, unresolved = build_pick_assets(team)
        print(f"\n=== {team} ===")
        print(f"Auto-gradable now (known slots only, no simulator wired in this demo): {len(assets)}")
        for a in assets:
            g = a.grade()
            print(f"  {g['label']:<30} grade={g['grade']:.1f} ({g['grade_label']})")
        print(f"Needs simulator or manual resolution: {len(unresolved)}")
        for year, text in unresolved[:5]:
            print(f"  {year}: {text}")
        if len(unresolved) > 5:
            print(f"  ... and {len(unresolved) - 5} more")
