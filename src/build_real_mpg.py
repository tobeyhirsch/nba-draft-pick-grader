"""
One-time conversion script: turns the user-supplied "NBA Player Data
2026.xlsx" (a Basketball-Reference "Per Game" stats export for the
CONCLUDED 2025-26 season -- real observed games, not a projection; see
darko_ratings.py's MPG discussion for why this exists) into a clean CSV
of real per-player minutes:

    Player,MP,Games

Turns out real 2025-26 minutes are dramatically more reliable than
DARKO's own projected MPG for exactly the players where it matters most:
cross-checking `darkodpmleaderboard.csv` against `real_rosters_202627.py`'s
depth-chart order found 65 within-position-group MPG inversions (a
deeper-listed player projected for meaningfully MORE minutes than one
listed above them) -- and DARKO's own documentation admits minutes
projections are its weakest output, especially for players with thin
track record. Two confirmed examples: Brooks Barnhizer (a depth-chart
fringe/two-way OKC player) was projected at 35.0 MPG by DARKO, more than
Shai Gilgeous-Alexander's 30.0 -- his real 2025-26 average was 8.7 MPG.
Payton Sandfort was projected at 27.1 MPG; his real average was 15.8 over
just 4 games.

The workbook came in as single-column pasted CSV text (one full
comma-separated row per cell, from a Basketball-Reference export), same
quirk as build_multi_year_stats.py's "PER VORP BPM" sheets -- each row is
re-parsed with csv.DictReader. 4 blank rows precede the real header row
here (Sheet1 row 5); handled by filtering blank cells rather than assuming
a fixed offset, in case a re-export shifts it.

MULTI-TEAM ROLLUP: MP is reported per-stint for a traded player (one row
per team) PLUS a TOT/2TM/3TM/4TM rollup row with baskeball-reference's own
season-long weighted-average MP across every stint. The rollup row is
preferred here when present -- the same convention build_multi_year_stats.py
uses for its Games column, and for the same reason: a player's TRUE
season-long average shouldn't be read from just one partial stint.

Trailing "League Average" row and the Basketball-Reference attribution
footer line are both filtered out (no numeric G/MP fields to parse).
"""

import csv
import os
from typing import Dict, Tuple

import openpyxl

XLSX_PATH = "/Users/tobeyhirsch/Downloads/NBA Player Data 2026.xlsx"
# Anchored to the repo root (one level up from this file's src/ folder) so
# the output always lands in the tracked data/ folder regardless of
# whether this script is run from the repo root or from inside src/.
OUTPUT_CSV = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "real_mpg_2025_26.csv")


def load_raw_rows(xlsx_path: str) -> list:
    wb = openpyxl.load_workbook(xlsx_path, data_only=True)
    ws = wb["Sheet1"]
    return [row[0] for row in ws.iter_rows(values_only=True) if row and row[0]]


def parse_per_game_table(lines: list) -> Dict[str, Tuple[float, int]]:
    """{Player: (MP, Games)} -- MP/Games from the TOT/2TM/3TM/4TM rollup row
    when one exists, else the player's single (untraded) row."""
    single_team: Dict[str, Tuple[float, int]] = {}
    rollup: Dict[str, Tuple[float, int]] = {}

    for row in csv.DictReader(lines):
        name = row.get("Player")
        if not name or name in ("Player", "League Average"):
            continue
        team = row.get("Team")
        if not team:
            continue
        try:
            mp = float(row["MP"])
            games = int(row["G"])
        except (ValueError, TypeError):
            continue

        name = name.strip()
        if team in ("TOT", "2TM", "3TM", "4TM"):
            rollup.setdefault(name, (mp, games))
        else:
            single_team.setdefault(name, (mp, games))

    return {name: rollup.get(name, stats) for name, stats in single_team.items()}


def main():
    lines = load_raw_rows(XLSX_PATH)
    by_player = parse_per_game_table(lines)

    with open(OUTPUT_CSV, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["Player", "MP", "Games"])
        for name in sorted(by_player):
            mp, games = by_player[name]
            writer.writerow([name, mp, games])

    print(f"Wrote {len(by_player)} players' real 2025-26 MP to {OUTPUT_CSV}")


if __name__ == "__main__":
    main()
