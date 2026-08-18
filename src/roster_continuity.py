"""
Adds a "will this player still be on THIS team" signal to darko_ratings.py's
future-year projections -- distinct from darkolongevityprojections.csv's
"is this player still an NBA player ANYWHERE" signal. A player can stay in
the league (high longevity presence) while still leaving via free agency
or a trade; darko_ratings.py's model had no way to know that on its own.
This module gives it one, sourced from PlayerSalariesCSV.csv's actual
contract years and option flags (via cap_sheet_data.py / roster_cap.py).

TEAM-MISMATCH DISCOVERY (read this before trusting anything downstream):
While building this, darkodpmleaderboard.csv's Team column was found to
disagree with PlayerSalariesCSV.csv's / real_rosters_202627.py's for a
meaningful number of players -- not edge cases, stars: Giannis
Antetokounmpo is Miami Heat in the cap sheet and depth chart vs. Milwaukee
Bucks in DARKO; LeBron James is Philadelphia 76ers vs. Los Angeles Lakers;
Kawhi Leonard is Toronto Raptors vs. Los Angeles Clippers. A direct
(player, team) join against DARKO's 530 players found 73 such mismatches
(and a further 166 DARKO players with no cap-sheet entry at all, expected
-- see MATCHING below). real_rosters_202627.py (cap_sheet_data.py's own
cross-check ground truth) AGREES with the cap sheet, not with DARKO, on
every case checked -- so this isn't a random data-entry slip on one side,
it looks like the cap sheet + depth chart describe a different roster
reality (already-happened trades) than the DARKO snapshot does.

Per explicit user direction, PlayerSalariesCSV.csv and real_rosters_202627.py
are the trusted/correct team assignments. This module follows that: see
MATCHING below. But that same direction means darko_ratings.py's own
TEAM-LEVEL grouping -- which team a player's DPM counts toward, via
DarkoPlayer.team, which drives every team rating, every standings
projection, and every pick grade in this whole pipeline -- is still keyed
on the (per this same finding, less trusted) DARKO team field, and this
module does NOT change that. Re-keying the entire rating pipeline onto the
cap sheet's team assignments is a bigger, separate change this task didn't
cover (it would also need checking whether darkolongevityprojections.csv
and market_ratings.py's win-total data assume the DARKO-side roster or the
cap-sheet-side one -- an open question, not resolved here). Flagging this
loudly rather than letting it sit as a silent inconsistency -- see
README.md's "Known gaps" section.

MATCHING: contracts are looked up by PLAYER NAME ONLY (normalize_name(),
see name_matching.py), not (player, team) -- deliberately, given the
finding above: gating on DARKO's team field would silently throw away real
contract data for every player DARKO has mislabeled. Checked: all 435
cap-sheet player names are unique, so this can't cross-wire two different
same-named players in this data. Of DARKO's 530 players, 383 (72%) have a
name-matching cap-sheet contract; the other 147 are mostly deep-bench/
two-way players the 435-contract cap sheet simply doesn't cover (spot-
checked several -- e.g. James Harden, Jonathan Kuminga -- confirmed absent
from the raw CSV under any spelling, not a normalization miss). Those 147
get the neutral default below, same as darko_ratings.py's existing
"no data -> don't guess" policy elsewhere.

CONTINUITY SCALE (0.0-1.0, same shape as DarkoPlayer.presence()):
  1.0  -- no signal either way: no contract on file for this player at
          all, or the season falls after the cap sheet's coverage window
          (PlayerSalariesCSV.csv only runs through the 2030-31 season).
          Neutral, not a penalty -- consistent with roster_cap.py's own
          "don't fake precision" stance on anything not actually in the
          data.
  1.0  -- contract has a real, non-option salary figure on file for that
          season -- the team clearly expects to have them under contract.
  OPTION_YEAR_CONTINUITY (0.7) -- the season is a player/team/mutual
          option year. ASSUMPTION, not a fit -- no data source here says
          how often NBA options actually get exercised. Treating an option
          year as somewhat less certain than a guaranteed year seemed
          right; 0.7 specifically is a judgment call.
  NOT_ON_BOOKS_CONTINUITY (0.3) -- the cap sheet has this player on file
          for OTHER seasons but nothing for this one (their tracked
          contract has simply run out by then). ASSUMPTION, not a fit:
          treats "no longer under contract" as a meaningful but not
          certain sign they leave that team -- vets on expiring deals get
          re-signed by their own team often enough that 0.0 felt too
          harsh, but 0.3 is not calibrated against any real re-signing-
          rate data.
"""

import os
from typing import Dict

from cap_sheet_data import TEAM_CAP_SHEETS
from roster_cap import Contract
from name_matching import normalize_name

MAX_CAP_SHEET_SEASON = 2030  # last season PlayerSalariesCSV.csv covers ("2030-31")

OPTION_YEAR_CONTINUITY = 0.7
NOT_ON_BOOKS_CONTINUITY = 0.3


def _build_contract_lookup() -> Dict[str, Contract]:
    """{normalize_name(player): Contract}, pooled across every team's cap sheet -- see module docstring MATCHING."""
    lookup: Dict[str, Contract] = {}
    for cap_sheet in TEAM_CAP_SHEETS.values():
        for contract in cap_sheet.contracts:
            lookup[normalize_name(contract.player_name)] = contract
    return lookup


CONTRACT_BY_PLAYER: Dict[str, Contract] = _build_contract_lookup()


def continuity(player_name: str, season_start_year: int) -> float:
    """
    0.0-1.0 confidence this player is still under contract wherever
    they're currently rostered, for the season starting `season_start_year`
    (e.g. 2028 means the 2028-29 season). See module docstring for the
    CONTINUITY SCALE and why OPTION_YEAR_CONTINUITY / NOT_ON_BOOKS_CONTINUITY
    are judgment calls, not fits.
    """
    if season_start_year > MAX_CAP_SHEET_SEASON:
        return 1.0
    contract = CONTRACT_BY_PLAYER.get(normalize_name(player_name))
    if contract is None:
        return 1.0
    if season_start_year not in contract.salary_by_year:
        return NOT_ON_BOOKS_CONTINUITY
    is_option_year = (season_start_year in contract.player_option_years
                       or season_start_year in contract.team_option_years)
    return OPTION_YEAR_CONTINUITY if is_option_year else 1.0


if __name__ == "__main__":
    import csv

    print(f"Loaded contracts for {len(CONTRACT_BY_PLAYER)} distinct (normalized) player names "
          f"across {len(TEAM_CAP_SHEETS)} teams")

    dpm_csv = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "darkodpmleaderboard.csv")
    with open(dpm_csv, encoding="utf-8-sig") as f:
        darko_names = [row["Player"].strip() for row in csv.DictReader(f)]
    matched = sum(1 for n in darko_names if normalize_name(n) in CONTRACT_BY_PLAYER)
    print(f"{matched}/{len(darko_names)} DARKO players ({matched / len(darko_names):.0%}) have a name-matched contract")

    print("\nSpot checks (seasons 2027 through 2031 -- draft years 2028 through 2032's inputs):")
    examples = ["Jaylen Brown", "Moritz Wagner", "Keon Ellis", "Isaiah Hartenstein", "LeBron James", "Some Fake Player"]
    for name in examples:
        row = [f"{continuity(name, ssy):.2f}" for ssy in range(2027, 2032)]
        print(f"  {name:<22}" + "  ".join(row))
