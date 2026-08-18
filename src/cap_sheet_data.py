"""
Real cap-sheet data for all 30 teams, 2026-27 through 2030-31 (5 seasons).

STATUS: fully populated for all 30 teams. This supersedes the earlier
partial (3-team) hand-transcribed version of this module -- see SOURCE
HISTORY below for how we got here.

SOURCE HISTORY:

  The original version of this module was hand-transcribed from
  nbacaptracker.com and spotrac.com, one team at a time. That effort only
  reached 3 of 30 teams (Boston Celtics, Charlotte Hornets, Washington
  Wizards) before being paused, and even those 3 had confirmed data-quality
  problems along the way:

    - nbacaptracker.com's "Cap Holds" sidebar table was found to attribute
      Golden State Warriors players (Jonathan Kuminga, Gabe Vincent) to the
      Atlanta Hawks, reproduced identically across two independent fetches.
    - nbacaptracker.com's Charlotte Hornets page was missing LaMelo Ball
      (Charlotte's franchise player) from the main roster table entirely.
    - Spotrac's team cap pages, used after switching away from
      nbacaptracker, turned out to ALSO have wrong team attributions when
      checked against the user-supplied real depth chart
      (real_rosters_202627.py): LaMelo Ball, Miles Bridges, and Josh Green
      were all wrongly listed under Charlotte's Spotrac page (Ball/Green
      are actually on Minnesota, Bridges is on Phoenix). Jaylen Brown and
      Dalano Banton were wrongly listed under Boston's page. Jaden Hardy
      and D'Angelo Russell were wrongly listed under Washington's page.
    - Spotrac's cap pages were also rate-limited (Cloudflare 403 on
      parallel/rapid sequential fetches of the /cap/_/year/2026 pattern
      specifically), and only exposed a single season's cap hit per player,
      not a multi-year progression.
    - Two further sources were evaluated and ruled out entirely: LD Sport
      (ldsport.com, salary tables embedded in unreadable OneDrive/Excel
      widgets) and HoopsHype (hoopshype.com, disallows fetching via
      robots.txt).

  Given the unreliability of automated scraping across FOUR different
  sources, this module now instead parses PlayerSalariesCSV.csv --
  user-supplied 5-year salary data (2026-27 through 2030-31) covering all
  30 teams, 435 players total. This is a direct transcription task (read
  the CSV, build Contract objects) rather than a web-scraping-and-trust
  task, which is why it succeeded where the earlier sources didn't.

  VALIDATION PERFORMED before trusting this CSV: every (team, player) pair
  was cross-checked against real_rosters_202627.TEAM_DEPTH_CHARTS (the
  user-supplied authoritative roster source). Of 435 rows, 433 matched
  cleanly once name-formatting differences were normalized (accented
  characters, curly vs. straight apostrophes, periods in "Jr."/"Sr."/"II"
  suffixes, and known nicknames like "Mo Bamba" for "Mohamed Bamba", "Bones
  Hyland" for "Nah'Shon Hyland", "Cam Christie" for "Cameron Christie").
  Two genuine discrepancies remain, both worth knowing about rather than
  silently trusting:

    - Dennis Schroder and Tre Mann appear SWAPPED between this CSV and the
      depth chart: the CSV has Schroder on Charlotte and Mann on
      Cleveland, while the depth chart has Schroder on Cleveland and Mann
      on Charlotte. This has the shape of an actual trade that happened
      between when the two source snapshots were taken, not a data error
      -- but it hasn't been independently confirmed, so treat either
      team's Schroder/Mann assignment with mild caution.
    - Five players in the CSV don't appear anywhere in the depth chart:
      Zach Collins (Bulls), Lonnie Walker IV (Nuggets), Gary Payton II
      (Warriors), Bradley Beal (Clippers), Pacome Dadiet (Knicks). The
      depth chart may simply be incomplete (it's a snapshot, not
      guaranteed exhaustive down to every end-of-bench/two-way body) --
      these five are kept in the cap sheet data as given, unverified.

Structure matches roster_cap.py's Contract/CapSheet classes directly. Every
Contract's salary_by_year only includes years the CSV gave a nonzero salary
figure for (a player with only a 2026-27 figure and blank years after is an
expiring/one-year deal, same convention roster_cap.CapSheet.expiring_contracts()
already expects). "Mutual Option" years (3 across the whole league: Moritz
Wagner and Keon Ellis of Brooklyn in 2027-28, Isaiah Hartenstein of OKC in
2028-29) are recorded in BOTH player_option_years and team_option_years,
since a mutual option requires both sides to agree to keep it -- either
side declining kills the option year, which is the same practical risk
profile as it being solely that side's option.
"""

import csv
import os
from typing import Dict, List

from roster_cap import Contract, CapSheet
from data_paths import find_data_file

_CSV_PATH = find_data_file("PlayerSalariesCSV.csv", os.path.dirname(os.path.abspath(__file__)))

_SALARY_COLUMNS = [
    (2026, "Salary 2026-27", "Option 2026-27"),
    (2027, "Salary 2027-28", "Option 2027-28"),
    (2028, "Salary 2028-29", "Option 2028-29"),
    (2029, "Salary 2029-30", "Option 2029-30"),
    (2030, "Salary 2030-31", "Option 2030-31"),
]


def _parse_contract(row: Dict[str, str]) -> Contract:
    team = row["Team"].strip()
    player = row["Player"].strip()
    salary_by_year: Dict[int, float] = {}
    player_option_years: List[int] = []
    team_option_years: List[int] = []

    for year, salary_col, option_col in _SALARY_COLUMNS:
        raw_salary = row[salary_col].strip()
        if not raw_salary:
            continue
        salary_by_year[year] = float(int(raw_salary))

        option = row[option_col].strip()
        if option == "Player Option":
            player_option_years.append(year)
        elif option == "Team Option":
            team_option_years.append(year)
        elif option == "Mutual Option":
            player_option_years.append(year)
            team_option_years.append(year)

    return Contract(
        player_name=player,
        team=team,
        salary_by_year=salary_by_year,
        player_option_years=player_option_years,
        team_option_years=team_option_years,
    )


def _load_all_cap_sheets(csv_path: str = _CSV_PATH) -> Dict[str, CapSheet]:
    sheets: Dict[str, List[Contract]] = {}
    with open(csv_path, newline="", encoding="utf-8-sig") as f:
        for row in csv.DictReader(f):
            contract = _parse_contract(row)
            sheets.setdefault(contract.team, []).append(contract)
    return {team: CapSheet(team=team, contracts=contracts) for team, contracts in sheets.items()}


TEAM_CAP_SHEETS: Dict[str, CapSheet] = _load_all_cap_sheets()

# No cap-holds (pending free agent / unsigned draft pick) data source is
# available yet -- PlayerSalariesCSV.csv only covers signed active
# contracts ("Status" column is "Active" for all 435 rows). Left empty
# rather than guessed at; populate per-team if/when that data is supplied.
TEAM_CAP_HOLDS: Dict[str, Dict[str, float]] = {}


def get_team_cap_sheet(team_name: str) -> CapSheet:
    if team_name not in TEAM_CAP_SHEETS:
        raise KeyError(
            f"{team_name!r} not found. Available teams: {sorted(TEAM_CAP_SHEETS)}."
        )
    return TEAM_CAP_SHEETS[team_name]


if __name__ == "__main__":
    print(f"Loaded cap sheets for {len(TEAM_CAP_SHEETS)} teams from {_CSV_PATH}")
    total_players = sum(len(cs.contracts) for cs in TEAM_CAP_SHEETS.values())
    print(f"Total contracts: {total_players}")

    from roster_cap import SALARY_CAP_2026_27

    print(f"\n{'Team':<28}{'2026-27 total':>16}{'Apron status':>16}{'# contracts':>13}")
    rows = []
    for team, cs in TEAM_CAP_SHEETS.items():
        total = cs.total_salary(2026, guaranteed_only=False)
        rows.append((team, total, cs.apron_status(2026), len(cs.contracts)))
    rows.sort(key=lambda r: -r[1])
    for team, total, status, n in rows:
        print(f"{team:<28}{total:>16,.0f}{status:>16}{n:>13}")

    league_total = sum(r[1] for r in rows)
    print(f"\nLeague-wide 2026-27 total (active contracts only, no cap holds): ${league_total:,.0f}")
    print(f"For reference, 30 x salary cap (${SALARY_CAP_2026_27:,.0f}) = ${30*SALARY_CAP_2026_27:,.0f}")

    bos = get_team_cap_sheet("Boston Celtics")
    print(f"\nBoston Celtics 2026-27 contracts ({len(bos.contracts)}):")
    for c in sorted(bos.contracts, key=lambda c: -c.salary(2026)):
        opt = ""
        if 2026 in c.player_option_years:
            opt = " (player option)"
        elif 2026 in c.team_option_years:
            opt = " (team option)"
        print(f"  {c.player_name:<28} ${c.salary(2026):>12,.0f}{opt}")
