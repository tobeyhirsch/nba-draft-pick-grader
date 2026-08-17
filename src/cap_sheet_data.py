"""
Real cap-sheet data, sourced from nbacaptracker.com (fetched live) --
chosen over LD Sport's own cap-sheet pages because LD Sport's salary tables
are rendered from an embedded OneDrive/Excel widget that isn't fetchable as
plain content; nbacaptracker.com publishes the same category of data
(active contracts by year, cap holds, apron/tax summary) as real HTML.

CURRENT STATUS: Boston Celtics is fully populated below as a verified,
real example (contract-by-contract, 2026-27 through 2030-31, fetched
directly from nbacaptracker.com/teams/boston-celtics). The other 29 teams
are NOT yet populated -- each one needs its own fetch
(nbacaptracker.com/teams/<team-slug>) and the same transcription. That's
roughly 29 more fetches plus careful transcription, which is straightforward
to do on request but wasn't done blind for all 30 teams to avoid silently
shipping error-prone data for teams nobody asked about yet.

Structure matches roster_cap.py's Contract/CapSheet classes directly.
"""

from typing import Dict, List

from roster_cap import Contract, CapSheet

# --- Boston Celtics: real, verified 2026-27 active contracts ---
# Source: https://www.nbacaptracker.com/teams/boston-celtics (fetched live).
# Team option / player option years are flagged; cap holds (pending free
# agents, unsigned picks) are tracked separately from active contracts.
BOSTON_CELTICS_CONTRACTS: List[Contract] = [
    Contract("Jayson Tatum", "Boston Celtics",
             {2026: 58_456_566, 2027: 62_786_682, 2028: 67_116_798, 2029: 71_446_914},
             player_option_years=[2029]),
    Contract("Jaylen Brown", "Boston Celtics",
             {2026: 57_078_728, 2027: 61_015_192, 2028: 64_951_656}),
    Contract("Derrick White", "Boston Celtics",
             {2026: 30_348_000, 2027: 32_596_000, 2028: 34_844_000},
             player_option_years=[2028]),
    Contract("Sam Hauser", "Boston Celtics",
             {2026: 10_848_215, 2027: 11_651_785, 2028: 12_455_356}),
    Contract("Payton Pritchard", "Boston Celtics",
             {2026: 7_767_857, 2027: 8_303_571}),
    Contract("Hugo Gonzalez", "Boston Celtics",
             {2026: 2_923_560, 2027: 3_062_640, 2028: 5_528_065},
             team_option_years=[2027, 2028]),
    Contract("Dalano Banton", "Boston Celtics", {2026: 2_801_346}),
    Contract("Luka Garza", "Boston Celtics", {2026: 2_801_346}),
    Contract("Baylor Scheierman", "Boston Celtics",
             {2026: 2_744_040, 2027: 4_952_993}, team_option_years=[2027]),
    Contract("Neemias Queta", "Boston Celtics", {2026: 2_667_944}),
    Contract("Ron Harper Jr.", "Boston Celtics",
             {2026: 2_626_248, 2027: 2_988_885},
             guaranteed_by_year={2026: False}),  # $0 GTD, fully guaranteed 1/10/27
    Contract("Jordan Walsh", "Boston Celtics",
             {2026: 2_406_205}, team_option_years=[2026]),
    Contract("Amari Williams", "Boston Celtics", {2026: 0}),  # two-way contract
]

# Cap holds (pending free agents, not on active roster salary) -- separate
# from Contract objects since they represent a different accounting
# category under the CBA, not a signed salary.
BOSTON_CELTICS_CAP_HOLDS_2026_27: Dict[str, float] = {
    "Blake Griffin": 2_500_000,
    "Nikola Vucevic": 32_200_000,
    "Max Shulga": 2_200_000,
    "John Tonje": 2_200_000,
    "Torrey Craig": 2_500_000,
    "Mfiondu Kabengele": 2_200_000,
    "Chris Cenac Jr.": 3_000_000,
}

TEAM_CAP_SHEETS: Dict[str, CapSheet] = {
    "Boston Celtics": CapSheet(team="Boston Celtics", contracts=BOSTON_CELTICS_CONTRACTS),
}

TEAM_CAP_HOLDS: Dict[str, Dict[str, float]] = {
    "Boston Celtics": BOSTON_CELTICS_CAP_HOLDS_2026_27,
}

# Verified real thresholds nbacaptracker.com reported for Boston specifically
# (their figures round slightly differently than the league's own release
# figures in roster_cap.py -- e.g. $165.0M vs $164.961M -- both are the same
# real number, just rounded differently by each source).
NBACAPTRACKER_2026_27_CAP = 165_000_000
NBACAPTRACKER_2026_27_TAX = 201_000_000
NBACAPTRACKER_2026_27_FIRST_APRON = 209_000_000
NBACAPTRACKER_2026_27_SECOND_APRON = 222_000_000


def get_team_cap_sheet(team_name: str) -> CapSheet:
    if team_name not in TEAM_CAP_SHEETS:
        raise KeyError(
            f"{team_name!r} not yet populated with real data. "
            f"Currently available: {sorted(TEAM_CAP_SHEETS)}. "
            f"To add a team, fetch nbacaptracker.com/teams/<team-slug> and "
            f"transcribe following the Boston Celtics example above."
        )
    return TEAM_CAP_SHEETS[team_name]


if __name__ == "__main__":
    bos = get_team_cap_sheet("Boston Celtics")
    guaranteed_only = bos.total_salary(2026, guaranteed_only=True)
    all_cap_hits = bos.total_salary(2026, guaranteed_only=False)
    print(f"Boston Celtics 2026-27:")
    print(f"  Guaranteed-only total:  ${guaranteed_only:,.0f}")
    print(f"  All cap hits (incl. non-guaranteed, e.g. Ron Harper Jr.'s "
          f"$2,626,248): ${all_cap_hits:,.0f}")
    print(f"  nbacaptracker.com's 'Active Salary' figure: $183,470,055 "
          f"(matches the all-cap-hits number -- they count non-guaranteed "
          f"salary in the roster total, same as most public cap sites do; "
          f"CapSheet.total_salary() defaults to guaranteed_only=True since "
          f"that's usually the more decision-relevant number for planning)")
    print(f"Apron status: {bos.apron_status(2026, first_apron=NBACAPTRACKER_2026_27_FIRST_APRON, second_apron=NBACAPTRACKER_2026_27_SECOND_APRON, tax_line=NBACAPTRACKER_2026_27_TAX)}")
    total_cap_holds = sum(BOSTON_CELTICS_CAP_HOLDS_2026_27.values())
    print(f"Cap holds total: ${total_cap_holds:,.0f} (nbacaptracker.com reports $46,800,000)")
