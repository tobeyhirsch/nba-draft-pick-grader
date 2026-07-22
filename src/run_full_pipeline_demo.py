"""
Full pipeline demo: DARKO-style roster projections all the way through to
1-10 grades for each pick a team owns.

Run with: python run_full_pipeline_demo.py

Steps:
  1. team_wins.py       : rosters -> Elo ratings
  2. draft_pipeline_321 : simulate seasons + 3-2-1 lottery, thousands of trials
  3. pick_valuation.py  : convert one team's pick-outcome distribution into
                          an expected value
  4. roster_cap.py      : project the expected rookie-scale cap hit for
                          that same pick
  5. pick_grading.py    : grade each pick the team owns, 1-10
"""

import random

from team_wins import PlayerProjection, build_teams
from draft_pipeline_321 import monte_carlo_321_pick_distribution
from pick_valuation import distribution_from_counts, expected_value_of_distribution
from roster_cap import project_incoming_rookie_cost
from pick_grading import PickAsset, grade_pick_portfolio

# --- Step 1: rosters (illustrative, not real players) -------------------
# Two example teams: one clearly bad (lottery-bound), one clearly good.
# Everyone else in the demo league uses simple placeholder ratings so the
# full 30-team season/lottery machinery still runs.

TANKING_TEAM_ROSTER = [
    PlayerProjection("Young Prospect", darko=-1.0, projected_mpg=30),
    PlayerProjection("Vet Placeholder A", darko=-0.5, projected_mpg=28),
    PlayerProjection("Vet Placeholder B", darko=-1.5, projected_mpg=26),
    PlayerProjection("Rotation C", darko=-2.0, projected_mpg=24),
    PlayerProjection("Rotation D", darko=-1.0, projected_mpg=22),
    PlayerProjection("Bench E", darko=-2.5, projected_mpg=20),
    PlayerProjection("Bench F", darko=-3.0, projected_mpg=18),
    PlayerProjection("Bench G", darko=-2.0, projected_mpg=16),
    PlayerProjection("Deep Bench H", darko=-3.5, projected_mpg=36),  # mop-up minutes
]

CONTENDER_ROSTER = [
    PlayerProjection("Star Wing", darko=6.5, projected_mpg=35),
    PlayerProjection("All-Star Guard", darko=5.5, projected_mpg=34),
    PlayerProjection("Two-Way Big", darko=3.0, projected_mpg=30),
    PlayerProjection("3&D Starter", darko=1.5, projected_mpg=28),
    PlayerProjection("Starting PG", darko=1.0, projected_mpg=27),
    PlayerProjection("Bench Scorer", darko=0.0, projected_mpg=22),
    PlayerProjection("Backup Big", darko=-0.5, projected_mpg=20),
    PlayerProjection("Depth Wing", darko=-1.5, projected_mpg=18),
    PlayerProjection("Depth Guard", darko=-2.0, projected_mpg=26),
]


def build_demo_league():
    rosters = {"Tanking Team": TANKING_TEAM_ROSTER, "Contender": CONTENDER_ROSTER}
    conferences = {"Tanking Team": "East", "Contender": "West"}

    # Fill out the rest of the league with simple placeholder ratings
    # spread between the two extremes, split evenly into conferences.
    filler_ratings = [1420 + i * 8 for i in range(28)]
    for i, rating in enumerate(filler_ratings):
        name = f"Filler{i+1}"
        rosters[name] = [PlayerProjection(f"{name}_Player{j}", darko=0.0, projected_mpg=240 / 8)
                          for j in range(8)]
        conferences[name] = "East" if i % 2 == 0 else "West"
        # Nudge the filler team's rating directly since we want a spread,
        # not all-replacement-level -- override after building.

    teams = build_teams(rosters, conferences)
    # Overwrite filler ratings directly for a realistic spread (bypassing
    # the roster-driven calc for these placeholder teams only).
    for team in teams:
        if team.name.startswith("Filler"):
            idx = int(team.name.replace("Filler", "")) - 1
            team.rating = filler_ratings[idx]
    return teams


def main():
    teams = build_demo_league()
    trials = 3000

    print(f"Step 1-2: simulating {trials} seasons + 3-2-1 lotteries...")
    counts = monte_carlo_321_pick_distribution(teams, trials=trials, seed=7)

    tanking_dist = distribution_from_counts(counts["Tanking Team"], trials)
    tanking_ev = expected_value_of_distribution(tanking_dist)
    top7_probs = {p: prob for p, prob in tanking_dist.items() if p <= 7}
    print(f"\nTanking Team's pick outcomes:")
    print(f"  P(top 4):  {sum(p for k, p in tanking_dist.items() if k <= 4)*100:.1f}%")
    print(f"  P(relegated below 12, i.e. worst-record penalty biting): "
          f"{sum(p for k, p in tanking_dist.items() if k > 12)*100:.1f}%")
    print(f"  Expected pick value (0-100 scale): {tanking_ev:.1f}")

    print(f"\nStep 3-4: projected rookie-scale cost for that pick distribution...")
    rookie_cost = project_incoming_rookie_cost(tanking_dist)
    print(f"  Expected incoming rookie cap hit: ${rookie_cost:,.0f}")

    print(f"\nStep 5: grading each pick Tanking Team owns (1-10 scale)...")
    # Example portfolio: this year's uncertain lottery pick, plus two
    # illustrative other assets to show the scale across different cases.
    team_picks = [
        PickAsset("Tanking Team's own pick (this year, from the sim above)",
                  pick_probabilities=tanking_dist, years_away=0),
        PickAsset("Hypothetical future 2nd-rounder (unprotected, known slot)",
                  pick_number=52, years_away=1),
        PickAsset("Hypothetical acquired top-4-protected first from a good team",
                  pick_probabilities={4: 0.05, 10: 0.15, 16: 0.30, 22: 0.30, 27: 0.20},
                  protection_range=(1, 4), years_away=2),
    ]
    graded = grade_pick_portfolio(team_picks)
    print(f"{'Pick':<58}{'Grade':>8}  Label")
    for g in graded:
        print(f"{g['label']:<58}{g['grade']:>8.1f}  {g['grade_label']}")


if __name__ == "__main__":
    main()