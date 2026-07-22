"""
Master entry point. Runs the full model in order:

  1. Player performance projection  -> team_wins.PlayerProjection
  2. Roster & cap sheet             -> roster_cap.CapSheet
  3. Team win-projection            -> team_wins.build_teams (Elo ratings)
  4. League standings (Monte Carlo) -> standings_sim.simulate_season, via
                                        draft_pipeline_321's internal loop
  5. Lottery simulation             -> draft_pipeline_321 (2027+ 3-2-1 rules)
  6. Grading each pick a team has   -> pick_grading.PickAsset / grade_pick_portfolio

Replace the example rosters/contracts below with real data to use this for
an actual team. Every number that's a placeholder vs. a real, sourced
figure is called out inline.

Run with: python run_model.py
"""

from team_wins import PlayerProjection, build_teams
from roster_cap import CapSheet, Contract, SALARY_CAP_2026_27
from draft_pipeline_321 import monte_carlo_321_pick_distribution
from pick_valuation import distribution_from_counts
from pick_grading import PickAsset, grade_pick_portfolio

TRIALS = 3000  # Monte Carlo trials for the standings/lottery simulation


# --- Step 1: player performance projections (replace with real DARKO/EPM pulls) ---
# One example team's roster. In real use, build one of these per team from
# your DARKO/EPM data source and projected rotation minutes.
EXAMPLE_TEAM_ROSTER = [
    PlayerProjection("Young Wing", darko=-0.5, projected_mpg=30),
    PlayerProjection("Vet Guard", darko=-1.0, projected_mpg=28),
    PlayerProjection("Big Man", darko=-1.5, projected_mpg=26),
    PlayerProjection("Rotation Forward", darko=-2.0, projected_mpg=24),
    PlayerProjection("Bench Guard", darko=-1.0, projected_mpg=22),
    PlayerProjection("Bench Big", darko=-2.5, projected_mpg=20),
    PlayerProjection("Deep Bench A", darko=-3.0, projected_mpg=18),
    PlayerProjection("Deep Bench B", darko=-2.0, projected_mpg=16),
    PlayerProjection("Mop-up Minutes", darko=-3.5, projected_mpg=36),
]
EXAMPLE_TEAM_NAME = "Example Team"
EXAMPLE_TEAM_CONFERENCE = "East"


def build_full_league():
    """
    Builds a 30-team league: the example team above, plus 29 placeholder
    teams so the full standings/play-in/lottery machinery has a real
    30-team field to run against. Replace ALL of this with real rosters
    for actual use -- this function exists only so run_model.py is
    runnable out of the box.
    """
    rosters = {EXAMPLE_TEAM_NAME: EXAMPLE_TEAM_ROSTER}
    conferences = {EXAMPLE_TEAM_NAME: EXAMPLE_TEAM_CONFERENCE}

    filler_ratings = [1420 + i * 8 for i in range(29)]
    for i, rating in enumerate(filler_ratings):
        name = f"League Team {i+1}"
        rosters[name] = [
            PlayerProjection(f"{name} Player{j}", darko=0.0, projected_mpg=240 / 8)
            for j in range(8)
        ]
        # Example team is already in East (14 more needed there, 15 in West).
        conferences[name] = "East" if i < 14 else "West"

    teams = build_teams(rosters, conferences)
    for team in teams:
        if team.name.startswith("League Team"):
            idx = int(team.name.replace("League Team ", "")) - 1
            team.rating = filler_ratings[idx]
    return teams


def main():
    # --- Step 1 done above (rosters) ---

    # --- Step 2: roster & cap sheet (replace with real contract data) ---
    print("=" * 70)
    print("STEP 2: Roster & cap sheet")
    print("=" * 70)
    example_cap_sheet = CapSheet(
        team=EXAMPLE_TEAM_NAME,
        contracts=[
            Contract("Young Wing", EXAMPLE_TEAM_NAME, {2026: 8_000_000, 2027: 9_000_000}),
            Contract("Vet Guard", EXAMPLE_TEAM_NAME, {2026: 12_000_000}),  # expiring
            Contract("Big Man", EXAMPLE_TEAM_NAME, {2026: 6_000_000, 2027: 6_500_000}),
        ],
    )
    print(f"{EXAMPLE_TEAM_NAME} 2026 salary: ${example_cap_sheet.total_salary(2026):,.0f}")
    print(f"Cap space vs. ${SALARY_CAP_2026_27:,.0f} cap: "
          f"${example_cap_sheet.cap_space(2026):,.0f}")
    print(f"Apron status: {example_cap_sheet.apron_status(2026)}")
    print(f"Expiring after 2026: "
          f"{[c.player_name for c in example_cap_sheet.expiring_contracts(2027)]}")

    # --- Step 3: team win-projection (DARKO -> Elo rating) ---
    print("\n" + "=" * 70)
    print("STEP 3: Team win-projection (roster -> Elo rating)")
    print("=" * 70)
    teams = build_full_league()
    example_team = next(t for t in teams if t.name == EXAMPLE_TEAM_NAME)
    print(f"{EXAMPLE_TEAM_NAME} projected rating: {example_team.rating:.1f} "
          f"(1500 = league average)")

    # --- Step 4 + 5: league standings Monte Carlo + 3-2-1 lottery simulation ---
    print("\n" + "=" * 70)
    print(f"STEP 4-5: Simulating {TRIALS} seasons + 3-2-1 lotteries")
    print("=" * 70)
    counts = monte_carlo_321_pick_distribution(teams, trials=TRIALS, seed=7)
    example_dist = distribution_from_counts(counts[EXAMPLE_TEAM_NAME], TRIALS)

    print(f"{EXAMPLE_TEAM_NAME}'s projected pick outcomes:")
    print(f"  P(top 4):    {sum(p for k, p in example_dist.items() if k <= 4)*100:5.1f}%")
    print(f"  P(picks 5-16, lottery): "
          f"{sum(p for k, p in example_dist.items() if 5 <= k <= 16)*100:5.1f}%")
    print(f"  P(picks 17-30, made playoffs): "
          f"{sum(p for k, p in example_dist.items() if k >= 17)*100:5.1f}%")

    # --- Step 6: grade each pick the team has ---
    print("\n" + "=" * 70)
    print("STEP 6: Grading each pick this team owns")
    print("=" * 70)
    # Example portfolio: this year's own (uncertain) pick, plus two
    # illustrative acquired picks. Replace with the team's actual pick
    # inventory (own + traded-for, with real protections and years).
    team_picks = [
        PickAsset(f"{EXAMPLE_TEAM_NAME}'s own {2027} first (this year)",
                  pick_probabilities=example_dist, years_away=0),
        PickAsset("Acquired 2028 second-rounder (unprotected)",
                  pick_number=45, years_away=1),
        PickAsset("Acquired 2029 first, top-4 protected, from a good team",
                  pick_probabilities={4: 0.05, 10: 0.20, 16: 0.30, 22: 0.25, 27: 0.20},
                  protection_range=(1, 4), years_away=2),
    ]
    graded = grade_pick_portfolio(team_picks)
    print(f"{'Pick':<52}{'Grade':>8}  Label")
    for g in graded:
        print(f"{g['label']:<52}{g['grade']:>8.1f}  {g['grade_label']}")


if __name__ == "__main__":
    main()
