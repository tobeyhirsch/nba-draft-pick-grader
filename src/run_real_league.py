"""
Full real-league orchestrator: real market-calibrated ratings
(market_ratings.py), real conferences (conferences.py), real pick
ownership (draft_picks_data.py), real swap resolution (swap_resolver.py /
pick_resolver.py) -- runs the entire 30-team pipeline end to end and grades
every pick every team owns, 1-10.

Run with:
  python run_real_league.py                 # grade every team (slow, see below)
  python run_real_league.py "Boston Celtics" "Atlanta Hawks"   # grade just these

Writes a full results report to league_pick_grades.md in addition to
printing a summary.

PERFORMANCE NOTE: pick_resolver.build_pick_assets() runs its own dedicated
Monte Carlo batch (TRIALS_PER_TEAM trials) for each team's specific pick
portfolio, and each trial simulates a full 30-team season + lottery draw
from scratch. Total cost scales with (teams requested) x (trials per
team) x (distinct draft years that team's portfolio touches) -- there's no
caching/sharing of simulated seasons ACROSS different teams' calls in the
current pick_resolver design (each team's swaps reference a different
subset of the other 29 teams, so the trial batches aren't directly
reusable as-is without a bigger refactor), and since darko_ratings.py's
evolved ratings were wired in (see build_future_year_teams), a team whose
picks span multiple of the 2028-2032 draft years now runs one batch PER
distinct year in that span rather than one shared batch for its whole
portfolio -- years that share the same league (2027, and 2033+, which both
still fall back to the flat 2026-27 market ratings) still dedupe to a
single batch, so this mostly costs extra for teams with picks spread
across several of the 2028-2032 years. Grading all 30 teams at
TRIALS_PER_TEAM=2000 previously took roughly a minute and a half; expect
noticeably longer now given the extra per-year batches -- raise
TRIALS_PER_TEAM for tighter precision on a small number of teams, lower it
for a fast full-league smoke test.
"""

import os
import sys
import time
from typing import Dict, List, Sequence, Tuple

from market_ratings import load_market_win_totals, build_calibrated_teams
from conferences import TEAM_CONFERENCE
from draft_picks_data import TEAM_FUTURE_PICKS
from pick_resolver import build_pick_assets
from pick_grading import grade_pick_portfolio
from pick_restrictions_321 import DEFAULT_2027_HISTORY
from standings_sim import Team
from data_paths import find_data_file
from darko_ratings import (
    load_darko_players, all_teams_net_ratings, fit_darko_to_elo,
    future_year_teams, MAX_OFFSET, FIRST_DRAFT_YEAR_COVERED,
)

# Checks several common data/ locations relative to THIS file (see
# data_paths.py) rather than assuming one fixed layout -- works whether
# data/ sits next to this file or as a sibling of a src/ folder it's in.
MARKET_XLSX = find_data_file("market_win_totals.xlsx", os.path.dirname(os.path.abspath(__file__)))
CALIBRATION_SEED = 11
GRADING_SEED = 5
TRIALS_PER_TEAM = 2000  # lower = faster/noisier, higher = slower/tighter
RESULTS_FILE = "league_pick_grades.md"


def build_real_league() -> List[Team]:
    win_totals = load_market_win_totals(MARKET_XLSX)
    return build_calibrated_teams(win_totals, TEAM_CONFERENCE, seed=CALIBRATION_SEED,
                                   trials_per_iteration=400, iterations=30)


def build_future_year_teams(base_teams: Sequence[Team]) -> Dict[int, List[Team]]:
    """
    {draft_year: teams} for the 2028-2032 drafts, built from real DARKO DPM
    + longevity data (darko_ratings.py) instead of reusing base_teams'
    2026-27 market ratings unchanged for every future year. The 2027 draft
    deliberately isn't in this dict -- it already uses base_teams directly
    (the real, unmodified 2026-27 market ratings are the best available
    signal for the season that's actually about to happen; darko_ratings.py
    is calibrated AGAINST those same ratings, so re-deriving 2027 from it
    would only add noise). See darko_ratings.py's module docstring for the
    method and its caveats (this model can only ever go flat-or-down per
    team, never up, which is why the window stops at 2032).
    """
    players = load_darko_players()
    darko_now = all_teams_net_ratings(players, offset=0)
    market_elo = {t.name: t.rating for t in base_teams}
    slope, intercept, r2 = fit_darko_to_elo(darko_now, market_elo)
    print(f"  DARKO-to-Elo fit vs. current market ratings: r^2={r2:.3f} "
          f"(slope={slope:.2f}, intercept={intercept:.1f}) -- see darko_ratings.py to inspect further")

    conferences = {t.name: t.conference for t in base_teams}
    return {
        FIRST_DRAFT_YEAR_COVERED + offset - 1: future_year_teams(players, offset, slope, intercept, conferences)
        for offset in range(1, MAX_OFFSET + 1)
    }


def grade_team(team_name: str, teams: Sequence[Team], teams_by_year: Dict[int, List[Team]] = None,
               trials: int = TRIALS_PER_TEAM) -> Tuple[List[dict], List[tuple]]:
    # The market win totals this league is calibrated from are the 2026-27
    # season's O/U lines, so the resulting lottery this pipeline simulates
    # IS the 2027 draft -- the first one the 3-2-1 restrictions apply to.
    # Seed real 2025+2026 history (pick_restrictions_321.py) so simulated
    # 2027 lottery draws correctly enforce "no repeat #1" (blocks
    # Washington) and "no 3-straight top-5" (blocks Utah).
    #
    # teams_by_year (darko_ratings.py-derived, see build_future_year_teams)
    # overrides the 2028-2032 drafts with DARKO+longevity-evolved ratings;
    # 2027 and 2033 fall back to `teams` (the flat 2026-27 market ratings),
    # same as before this parameter existed.
    assets, unresolved = build_pick_assets(team_name, teams_for_simulation=teams,
                                            trials=trials, seed=GRADING_SEED,
                                            history=DEFAULT_2027_HISTORY,
                                            teams_by_year=teams_by_year)
    graded = grade_pick_portfolio(assets)
    return graded, unresolved


def write_report(all_results: Dict[str, Tuple[List[dict], List[tuple]]], path: str) -> None:
    lines = ["# NBA Draft Pick Grades -- Full League Run", ""]
    lines.append(f"2027-draft ratings calibrated from consensus market win totals (DraftKings/"
                 f"FanDuel/Hard Rock/Caesars 2026-27 O/U lines); the {FIRST_DRAFT_YEAR_COVERED}-"
                 f"{FIRST_DRAFT_YEAR_COVERED + MAX_OFFSET - 1} drafts use DARKO DPM + career "
                 f"longevity data instead, calibrated against those same market ratings "
                 f"(darko_ratings.py); 2033 falls back to the flat 2026-27 market ratings. "
                 f"Picks graded 1-10 via the swap-resolved pipeline. {TRIALS_PER_TEAM} simulation "
                 f"trials per team per draft year.")
    lines.append("")

    lines.append("## League summary: average pick grade by team")
    lines.append("")
    lines.append("| Team | Avg grade | Picks graded | Unresolved |")
    lines.append("|---|---|---|---|")
    summary_rows = []
    for name, (graded, unresolved) in all_results.items():
        avg = sum(g["grade"] for g in graded) / len(graded) if graded else 0.0
        summary_rows.append((name, avg, len(graded), len(unresolved)))
    summary_rows.sort(key=lambda r: -r[1])
    for name, avg, n_graded, n_unresolved in summary_rows:
        lines.append(f"| {name} | {avg:.2f} | {n_graded} | {n_unresolved} |")
    lines.append("")

    for name, (graded, unresolved) in all_results.items():
        lines.append(f"## {name}")
        lines.append("")
        lines.append("| Pick | Grade | Label |")
        lines.append("|---|---|---|")
        for g in sorted(graded, key=lambda g: -g["grade"]):
            lines.append(f"| {g['label']} | {g['grade']:.1f} | {g['grade_label']} |")
        if unresolved:
            lines.append("")
            lines.append(f"**Unresolved ({len(unresolved)}):**")
            for year, text, reason in unresolved:
                lines.append(f"- {year}: {text} -- *{reason}*")
        lines.append("")

    with open(path, "w") as f:
        f.write("\n".join(lines))


def main():
    requested = sys.argv[1:] if len(sys.argv) > 1 else sorted(TEAM_FUTURE_PICKS.keys())

    print("Calibrating market ratings for all 30 teams...")
    t0 = time.time()
    teams = build_real_league()
    print(f"  done in {time.time() - t0:.1f}s")

    print(f"\nBuilding DARKO+longevity-evolved ratings for the "
          f"{FIRST_DRAFT_YEAR_COVERED}-{FIRST_DRAFT_YEAR_COVERED + MAX_OFFSET - 1} drafts...")
    t0 = time.time()
    teams_by_year = build_future_year_teams(teams)
    print(f"  done in {time.time() - t0:.1f}s")

    print(f"\nGrading {len(requested)} team(s), {TRIALS_PER_TEAM} trials each...")
    t0 = time.time()
    all_results: Dict[str, Tuple[List[dict], List[tuple]]] = {}
    for i, name in enumerate(requested, 1):
        graded, unresolved = grade_team(name, teams, teams_by_year=teams_by_year)
        all_results[name] = (graded, unresolved)
        print(f"  [{i}/{len(requested)}] {name}: {len(graded)} picks graded, "
              f"{len(unresolved)} unresolved  ({time.time() - t0:.1f}s elapsed)")

    write_report(all_results, RESULTS_FILE)
    print(f"\nFull report written to {RESULTS_FILE}")

    print("\n=== League summary: average pick grade by team ===")
    summary_rows = []
    for name in requested:
        graded, _ = all_results[name]
        if graded:
            avg = sum(g["grade"] for g in graded) / len(graded)
            summary_rows.append((name, avg, len(graded)))
    summary_rows.sort(key=lambda r: -r[1])
    for name, avg, n in summary_rows:
        print(f"  {name:<28} avg grade {avg:5.2f}  ({n} picks graded)")


if __name__ == "__main__":
    main()
