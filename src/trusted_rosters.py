"""
The authoritative "which team is this player actually on" answer for this
project -- per explicit user direction, real_rosters_202627.py (the
user-supplied depth chart) and PlayerSalariesCSV.csv (via
cap_sheet_data.py) are correct, and darkodpmleaderboard.csv's Team column
is NOT. This was discovered while building roster_continuity.py: a direct
join found 89 of 530 DARKO players (17%) labeled onto a DIFFERENT team
than the depth chart/cap sheet says they're actually on -- not edge cases,
several stars: Giannis Antetokounmpo DARKO-labeled Milwaukee Bucks vs.
actually Miami Heat, LeBron James DARKO-labeled Los Angeles Lakers vs.
actually Philadelphia 76ers, Kawhi Leonard DARKO-labeled Los Angeles
Clippers vs. actually Toronto Raptors, and 86 more (see this file's
__main__ for the full list). darko_ratings.load_darko_players() uses this
module to re-key every DARKO player onto their real team before any
rating is computed -- see that module for how.

SOURCE PRIORITY: real_rosters_202627.TEAM_DEPTH_CHARTS first (526 players
-- the primary roster-membership source per that module's own docstring),
then PlayerSalariesCSV.csv's Team column (via cap_sheet_data.py) for
players the depth chart doesn't cover but the cap sheet does (5 at last
check -- Zach Collins, Lonnie Walker IV, Gary Payton II, Bradley Beal,
Pacome Dadiet -- see cap_sheet_data.py's docstring on why those 5 are
cap-sheet-only). Never the other way around: cap_sheet_data.py's own
docstring frames the depth chart as the thing OTHER sources get checked
against, and its two known disagreements with the cap sheet (Dennis
Schroder / Tre Mann's team) are left resolved in the depth chart's favor
for that same reason.

Depth-chart player names carry inline annotations the raw transcription
kept on purpose ("(R)" rookie, "**" two-way/camp-body/non-guaranteed,
"(Ex-10)"/"(Ex-9)" Exhibit contracts, "(RFA)"/"(UFA)" free-agent status,
"(+)" notable recent addition -- see real_rosters_202627.py's docstring)
-- strip_annotations() removes these before matching.

A player in NEITHER trusted source keeps whatever team their own data
source already says (darko_ratings.py falls back to DARKO's original Team
column for these -- consistent with this project's "no data -> don't
guess" policy elsewhere, e.g. roster_continuity.py's neutral defaults).
"""

import re
from typing import Dict, Optional

from real_rosters_202627 import TEAM_DEPTH_CHARTS
from cap_sheet_data import TEAM_CAP_SHEETS
from name_matching import normalize_name


def strip_annotations(name: str) -> str:
    """Removes real_rosters_202627.py's inline markers ('(R)', '**', '(Ex-10)', etc.) -- see that module's docstring."""
    n = re.sub(r"\*+", "", name)
    n = re.sub(r"\([^)]*\)", "", n)
    return n.strip()


def _build_trusted_team_lookup() -> Dict[str, str]:
    lookup: Dict[str, str] = {}
    for team, positions in TEAM_DEPTH_CHARTS.items():
        for _pos, names in positions.items():
            for raw in names:
                lookup[normalize_name(strip_annotations(raw))] = team
    # Cap sheet fills in players the depth chart doesn't cover -- never overrides the depth chart (see module docstring SOURCE PRIORITY).
    for cap_sheet in TEAM_CAP_SHEETS.values():
        for contract in cap_sheet.contracts:
            key = normalize_name(contract.player_name)
            if key not in lookup:
                lookup[key] = cap_sheet.team
    return lookup


TRUSTED_TEAM_BY_PLAYER: Dict[str, str] = _build_trusted_team_lookup()


def trusted_team_for(player_name: str) -> Optional[str]:
    """The player's real current team per real_rosters_202627.py / PlayerSalariesCSV.csv, or None if neither source covers them."""
    return TRUSTED_TEAM_BY_PLAYER.get(normalize_name(player_name))


if __name__ == "__main__":
    import csv
    import os

    print(f"Trusted team lookup covers {len(TRUSTED_TEAM_BY_PLAYER)} distinct (normalized) player names "
          f"({len(TEAM_DEPTH_CHARTS)} depth-chart teams)")

    print("\nSpot checks:")
    for name in ["Giannis Antetokounmpo", "LeBron James", "Kawhi Leonard", "Some Fake Player"]:
        print(f"  {name:<24} -> {trusted_team_for(name)}")

    from data_paths import find_data_file
    dpm_csv = find_data_file("darkodpmleaderboard.csv", os.path.dirname(os.path.abspath(__file__)))
    with open(dpm_csv, encoding="utf-8-sig") as f:
        darko_rows = [(row["Player"].strip(), row["Team"].strip()) for row in csv.DictReader(f)]

    matched = [(n, t) for n, t in darko_rows if trusted_team_for(n) is not None]
    reassigned = [(n, t, trusted_team_for(n)) for n, t in matched if trusted_team_for(n) != t]
    unmatched = [n for n, t in darko_rows if trusted_team_for(n) is None]

    print(f"\n{len(darko_rows)} DARKO players total")
    print(f"  {len(matched)} matched to a trusted source")
    print(f"  {len(reassigned)} of those disagree with DARKO's own Team column (re-keyed)")
    print(f"  {len(unmatched)} matched to NEITHER trusted source (keep DARKO's Team column, unchanged)")

    print("\nFull reassignment list (DARKO-labeled -> trusted):")
    for name, darko_team, real_team in sorted(reassigned):
        print(f"  {name:<28} {darko_team:<26} -> {real_team}")
