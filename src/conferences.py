"""
Real East/West conference assignments for all 30 teams, 2026-27 season.
Static, public information (conference alignment doesn't change year to
year absent league realignment) -- needed by draft_pipeline_321.py, which
requires every Team to have `conference` set to run the play-in + 3-2-1
lottery machinery (15 teams per side).
"""

from typing import Dict

TEAM_CONFERENCE: Dict[str, str] = {
    # Eastern Conference (15)
    "Atlanta Hawks": "East",
    "Boston Celtics": "East",
    "Brooklyn Nets": "East",
    "Charlotte Hornets": "East",
    "Chicago Bulls": "East",
    "Cleveland Cavaliers": "East",
    "Detroit Pistons": "East",
    "Indiana Pacers": "East",
    "Miami Heat": "East",
    "Milwaukee Bucks": "East",
    "New York Knicks": "East",
    "Orlando Magic": "East",
    "Philadelphia 76ers": "East",
    "Toronto Raptors": "East",
    "Washington Wizards": "East",
    # Western Conference (15)
    "Dallas Mavericks": "West",
    "Denver Nuggets": "West",
    "Golden State Warriors": "West",
    "Houston Rockets": "West",
    "Los Angeles Clippers": "West",
    "Los Angeles Lakers": "West",
    "Memphis Grizzlies": "West",
    "Minnesota Timberwolves": "West",
    "New Orleans Pelicans": "West",
    "Oklahoma City Thunder": "West",
    "Phoenix Suns": "West",
    "Portland Trail Blazers": "West",
    "Sacramento Kings": "West",
    "San Antonio Spurs": "West",
    "Utah Jazz": "West",
}

if __name__ == "__main__":
    from draft_picks_data import TEAM_FUTURE_PICKS

    east = [t for t, c in TEAM_CONFERENCE.items() if c == "East"]
    west = [t for t, c in TEAM_CONFERENCE.items() if c == "West"]
    print(f"East: {len(east)} teams, West: {len(west)} teams")
    missing = set(TEAM_FUTURE_PICKS.keys()) - set(TEAM_CONFERENCE.keys())
    print(f"Missing conference assignment: {sorted(missing)}")
