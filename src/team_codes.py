"""
Maps the 2-3 letter team codes used in draft_picks_data.py's raw pick-
description text (LD Sport / ESPN convention -- e.g. "NO" for New Orleans,
"GS" for Golden State, "SA" for San Antonio, none of which match the NBA's
own official 3-letter codes like "NOP"/"GSW"/"SAS") to the full team names
used everywhere else in this pipeline (cap_sheet_data.py, draft_picks_data.py's
own TEAM_FUTURE_PICKS keys, and Team.name from team_wins.build_teams()).

Without this mapping, pick_resolver.py's team_distributions / swap_resolver.py's
joint-trial lookups silently fail to match anything in a real run, since the
simulator and cap-sheet data key everything by full name while the raw pick
text uses these short codes.

Built by enumerating every distinct code actually used in
draft_picks_data.TEAM_FUTURE_PICKS (all 30 appear; verified 1:1 against
TEAM_FUTURE_PICKS's own keys).
"""

from typing import Dict

TEAM_ABBREV_TO_NAME: Dict[str, str] = {
    "ATL": "Atlanta Hawks",
    "BKN": "Brooklyn Nets",
    "BOS": "Boston Celtics",
    "CHA": "Charlotte Hornets",
    "CHI": "Chicago Bulls",
    "CLE": "Cleveland Cavaliers",
    "DAL": "Dallas Mavericks",
    "DEN": "Denver Nuggets",
    "DET": "Detroit Pistons",
    "GS": "Golden State Warriors",
    "HOU": "Houston Rockets",
    "IND": "Indiana Pacers",
    "LAC": "Los Angeles Clippers",
    "LAL": "Los Angeles Lakers",
    "MEM": "Memphis Grizzlies",
    "MIA": "Miami Heat",
    "MIL": "Milwaukee Bucks",
    "MIN": "Minnesota Timberwolves",
    "NO": "New Orleans Pelicans",
    "NYK": "New York Knicks",
    "OKC": "Oklahoma City Thunder",
    "ORL": "Orlando Magic",
    "PHI": "Philadelphia 76ers",
    "PHX": "Phoenix Suns",
    "POR": "Portland Trail Blazers",
    "SA": "San Antonio Spurs",
    "SAC": "Sacramento Kings",
    "TOR": "Toronto Raptors",
    "UTA": "Utah Jazz",
    "WAS": "Washington Wizards",
}

TEAM_NAME_TO_ABBREV: Dict[str, str] = {v: k for k, v in TEAM_ABBREV_TO_NAME.items()}


if __name__ == "__main__":
    from draft_picks_data import TEAM_FUTURE_PICKS

    names = set(TEAM_FUTURE_PICKS.keys())
    mapped_names = set(TEAM_ABBREV_TO_NAME.values())
    print(f"Codes mapped: {len(TEAM_ABBREV_TO_NAME)}")
    print(f"Missing from mapping (in TEAM_FUTURE_PICKS but no code maps to them): "
          f"{sorted(names - mapped_names)}")
    print(f"Extra in mapping (code maps to a name not in TEAM_FUTURE_PICKS): "
          f"{sorted(mapped_names - names)}")
