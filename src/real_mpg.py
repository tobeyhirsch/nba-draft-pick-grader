"""
Real, OBSERVED 2025-26 minutes-per-game -- an alternative to
darkodpmleaderboard.csv's own MPG column, which is a PROJECTION (DARKO's
own documentation admits playing-time projections are its weakest output)
and has no access to real team depth-chart/rotation context at all.

DISCOVERY: cross-checking darkodpmleaderboard.csv's MPG against
real_rosters_202627.py's depth-chart order found 65 within-position-group
inversions -- a player listed DEEPER on a team's real depth chart
projected for meaningfully MORE minutes than one listed above them, both
confirmed on the same real roster. Two examples that motivated this
module: Brooks Barnhizer (OKC, a depth-chart fringe/two-way player) was
DARKO-projected at 35.0 MPG, more than Shai Gilgeous-Alexander's 30.0 --
his real 2025-26 average was 8.7 MPG over 40 games. Payton Sandfort was
projected at 27.1 MPG; his real average was 15.8 over just 4 games.

SOURCE: data/real_mpg_2025_26.csv, built by build_real_mpg.py from a
user-supplied Basketball-Reference "Per Game" export for the CONCLUDED
2025-26 season (582 players, real games actually played -- not a
projection for the upcoming 2026-27 season). darko_ratings.load_darko_players()
uses this module to override DARKO's own MPG wherever a name match exists,
falling back to DARKO's projection only for players this source doesn't
cover (true incoming rookies/players with zero 2025-26 NBA games) -- same
"strict upgrade, never a data loss" convention as trusted_rosters.py's
team re-keying and player_value_regression.py's DPM projection.

A real 2025-26 average is itself an imperfect stand-in for 2026-27 role
(trades, coaching changes, and injuries can all shift a player's real
minutes year to year) -- but it's real, observed data from actual games,
which is categorically more reliable than a projection system that admits
minutes are its weakest output and has no rotation-context input at all.
"""

import csv
import os
from typing import Dict, Optional

from name_matching import normalize_name

REAL_MPG_CSV = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data", "real_mpg_2025_26.csv")


def _build_real_mpg_lookup(csv_path: str) -> Dict[str, float]:
    lookup: Dict[str, float] = {}
    with open(csv_path, encoding="utf-8-sig") as f:
        for row in csv.DictReader(f):
            lookup[normalize_name(row["Player"])] = float(row["MP"])
    return lookup


REAL_MPG_BY_PLAYER: Dict[str, float] = _build_real_mpg_lookup(REAL_MPG_CSV)


def real_mpg_for(player_name: str) -> Optional[float]:
    """The player's real, observed 2025-26 minutes-per-game, or None if data/real_mpg_2025_26.csv doesn't cover them."""
    return REAL_MPG_BY_PLAYER.get(normalize_name(player_name))


if __name__ == "__main__":
    print(f"Real MPG lookup covers {len(REAL_MPG_BY_PLAYER)} distinct (normalized) player names")

    print("\nSpot checks:")
    for name in ["Brooks Barnhizer", "Payton Sandfort", "Shai Gilgeous-Alexander", "Some Fake Player"]:
        print(f"  {name:<28} -> {real_mpg_for(name)}")

    from darko_ratings import DPM_CSV
    darko_rows = []
    with open(DPM_CSV, encoding="utf-8-sig") as f:
        darko_rows = [(row["Player"].strip(), float(row["MPG"])) for row in csv.DictReader(f)]

    matched = [(n, darko_mpg) for n, darko_mpg in darko_rows if real_mpg_for(n) is not None]
    unmatched = [n for n, _ in darko_rows if real_mpg_for(n) is None]

    print(f"\n{len(darko_rows)} DARKO players total")
    print(f"  {len(matched)} matched to real 2025-26 MP (will override DARKO's projection)")
    print(f"  {len(unmatched)} unmatched (keep DARKO's projected MPG, unchanged)")

    diffs = sorted(
        ((real_mpg_for(n) - darko_mpg, n, darko_mpg, real_mpg_for(n)) for n, darko_mpg in matched),
        key=lambda r: r[0],
    )
    print("\nBiggest DARKO-overestimates-vs-real (DARKO projected far MORE than they actually played):")
    for diff, name, darko_mpg, real in diffs[:10]:
        print(f"  {name:<28} DARKO={darko_mpg:>5.1f}  real={real:>5.1f}  ({diff:+.1f})")
    print("\nBiggest DARKO-underestimates-vs-real (DARKO projected far LESS than they actually played):")
    for diff, name, darko_mpg, real in diffs[-10:]:
        print(f"  {name:<28} DARKO={darko_mpg:>5.1f}  real={real:>5.1f}  ({diff:+.1f})")
