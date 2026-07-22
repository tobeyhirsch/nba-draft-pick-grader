"""
Converts player-level performance projections (DARKO, EPM, RAPTOR, or any
per-100-possession plus-minus metric) plus projected minutes into the
Elo-like `rating` that standings_sim.py and draft_pipeline_321.py expect.

Chain implemented here:
  player DARKO (per-100 net rating) + projected minutes
    -> team net rating per 100 possessions (minutes-weighted average)
    -> team point differential per game (net rating x pace/100)
    -> Elo-style rating (linear conversion, calibrated to ~28 Elo points
       per point of scoring margin -- see ASSUMPTIONS below)

ASSUMPTIONS (read before trusting the numbers):

1. ADDITIVITY. Team net rating is computed as a minutes-weighted average of
   individual DARKO values. Real lineups have fit/redundancy effects (two
   ball-dominant guards, a defense with no rim protector, etc.) that this
   does not capture. DARKO itself partially reflects on-court context from
   a player's *actual* team, so transplanting a player's DARKO onto a
   different hypothetical roster is itself an approximation. This is the
   same simplifying assumption used by most public "sum up the plus-minus"
   projection tools -- it's directionally useful, not lineup-optimal.

2. MINUTES PROJECTIONS ALREADY BAKE IN AVAILABILITY. `projected_mpg` is
   treated as a season-long average that already accounts for expected
   missed games (a player projected for 30 mpg over an expected 65-game
   season should be entered as roughly 30 * 65/82 ≈ 23.8, not 30). This
   module does NOT separately model injury-risk variance -- it only
   affects the mean, not the added standings uncertainty from availability
   risk. A real refinement would simulate games-played as its own
   distribution per player and re-derive team strength week to week.

3. PACE. Net rating (per 100 possessions) is converted to per-game point
   differential using a flat league-average pace assumption (possessions
   per game). Default is 100.0; override per team if you have a pace
   projection (fast teams create more possessions for the *same* per-100
   rating to work with, but the conversion here is intentionally simple --
   it does not model why a team's own pace might change with a new roster).

4. ELO CONVERSION CONSTANT. `ELO_POINTS_PER_MARGIN_POINT = 28.0` is a
   commonly used approximation (in the spirit of FiveThirtyEight's NBA Elo
   methodology) for how many Elo points correspond to one point of
   predicted scoring margin. It has NOT been refit against your specific
   HOME_COURT_ELO=60 constant in standings_sim.py or validated against
   real outcomes -- treat it as a reasonable starting point, not a
   calibrated model.

5. ROSTER COMPLETENESS. A full team-game requires 240 total minutes (5
   players x 48). If the players you pass in don't sum to ~240 mpg, the
   weighted average still works mathematically, but a large deviation
   usually means missing bench players -- build_team() prints a warning
   rather than failing, since incomplete rosters (e.g. modeling only a
   projected rotation) are a legitimate use case too.
"""

from dataclasses import dataclass
from typing import List, Sequence

from standings_sim import Team

LEAGUE_AVERAGE_ELO = 1500.0
ELO_POINTS_PER_MARGIN_POINT = 28.0  # see assumption 4 above
DEFAULT_PACE = 100.0                # possessions per game, see assumption 3
FULL_TEAM_MINUTES = 240.0           # 5 players x 48 minutes
MPG_SANITY_TOLERANCE = 20.0         # warn if total roster mpg is off by more than this


@dataclass
class PlayerProjection:
    name: str
    darko: float          # per-100-possession net rating (DARKO, EPM, RAPTOR, etc.)
    projected_mpg: float  # season-long average minutes per game (see assumption 2)


def team_net_rating(players: Sequence[PlayerProjection]) -> float:
    """Minutes-weighted average DARKO across the roster -> team net rating per 100 poss."""
    total_mpg = sum(p.projected_mpg for p in players)
    if total_mpg <= 0:
        raise ValueError("Total projected minutes must be positive")
    return sum(p.darko * p.projected_mpg for p in players) / total_mpg


def net_rating_to_point_diff(net_rating_per100: float, pace: float = DEFAULT_PACE) -> float:
    """Per-100-possession net rating -> expected point differential per game."""
    return net_rating_per100 * (pace / 100.0)


def point_diff_to_elo(point_diff_per_game: float) -> float:
    """Point differential per game -> Elo-like rating on standings_sim.py's scale."""
    return LEAGUE_AVERAGE_ELO + point_diff_per_game * ELO_POINTS_PER_MARGIN_POINT


def build_team(name: str, players: Sequence[PlayerProjection], conference: str = None,
               pace: float = DEFAULT_PACE) -> Team:
    """
    Full chain: roster of PlayerProjections -> a Team object ready to feed
    into standings_sim.simulate_season() / draft_pipeline_321.py.
    """
    total_mpg = sum(p.projected_mpg for p in players)
    if abs(total_mpg - FULL_TEAM_MINUTES) > MPG_SANITY_TOLERANCE:
        print(f"[team_wins] Warning: {name}'s roster totals {total_mpg:.1f} mpg "
              f"(expected ~{FULL_TEAM_MINUTES:.0f}). Ratings will still compute, "
              f"but check for missing/incomplete roster entries.")

    net_rating = team_net_rating(players)
    point_diff = net_rating_to_point_diff(net_rating, pace=pace)
    rating = point_diff_to_elo(point_diff)
    return Team(name=name, rating=rating, conference=conference)


def build_teams(rosters: dict, conferences: dict = None, pace: float = DEFAULT_PACE) -> List[Team]:
    """
    Convenience wrapper for a whole league.

    rosters: {team_name: [PlayerProjection, ...]}
    conferences: optional {team_name: "East"/"West"}
    """
    conferences = conferences or {}
    return [
        build_team(name, players, conference=conferences.get(name), pace=pace)
        for name, players in rosters.items()
    ]


if __name__ == "__main__":
    # Sanity check: a roster of exactly replacement-level (darko=0) players
    # should produce league-average rating (1500). A clearly stacked roster
    # should produce a meaningfully higher rating.
    replacement_roster = [
        PlayerProjection(f"Replacement{i}", darko=0.0, projected_mpg=240.0 / 8)
        for i in range(8)
    ]
    avg_team = build_team("Replacement Level Team", replacement_roster)
    print(f"Replacement-level team rating (expect ~{LEAGUE_AVERAGE_ELO:.0f}): {avg_team.rating:.1f}")

    stacked_roster = [
        PlayerProjection("Star A", darko=6.0, projected_mpg=36),
        PlayerProjection("Star B", darko=5.0, projected_mpg=34),
        PlayerProjection("Good Starter C", darko=2.5, projected_mpg=32),
        PlayerProjection("Starter D", darko=1.0, projected_mpg=30),
        PlayerProjection("Starter E", darko=0.5, projected_mpg=28),
        PlayerProjection("Bench F", darko=-1.0, projected_mpg=24),
        PlayerProjection("Bench G", darko=-1.5, projected_mpg=22),
        PlayerProjection("Bench H", darko=-2.0, projected_mpg=20),
        PlayerProjection("Bench I", darko=-2.5, projected_mpg=14),
    ]
    stacked_team = build_team("Contender", stacked_roster)
    print(f"Stacked roster total mpg: {sum(p.projected_mpg for p in stacked_roster):.0f} "
          f"(expect ~240)")
    print(f"Stacked team net rating per 100: {team_net_rating(stacked_roster):.2f}")
    print(f"Stacked team rating: {stacked_team.rating:.1f} (expect well above 1500)")
