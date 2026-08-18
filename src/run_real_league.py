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
team) -- there's no caching/sharing of simulated seasons ACROSS different
teams' calls in the current pick_resolver design (each team's swaps
reference a different subset of the other 29 teams, so the trial batches
aren't directly reusable as-is without a bigger refactor). Grading all 30
teams at TRIALS_PER_TEAM=2000 takes roughly a minute and a half on this
project's reference hardware; raise TRIALS_PER_TEAM for tighter precision
on a small number of teams, lower it for a fast full-league smoke test.
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


def grade_team(team_name: str, teams: Sequence[Team],
               trials: int = TRIALS_PER_TEAM) -> Tuple[List[dict], List[tuple]]:
    # The market win totals this league is calibrated from are the 2026-27
    # season's O/U lines, so the resulting lottery this pipeline simulates
    # IS the 2027 draft -- the first one the 3-2-1 restrictions apply to.
    # Seed real 2025+2026 history (pick_restrictions_321.py) so simulated
    # 2027 lottery draws correctly enforce "no repeat #1" (blocks
    # Washington) and "no 3-straight top-5" (blocks Utah).
    assets, unresolved = build_pick_assets(team_name, teams_for_simulation=teams,
                                            trials=trials, seed=GRADING_SEED,
                                            history=DEFAULT_2027_HISTORY)
    graded = grade_pick_portfolio(assets)
    return graded, unresolved


def write_report(all_results: Dict[str, Tuple[List[dict], List[tuple]]], path: str) -> None:
    lines = ["# NBA Draft Pick Grades -- Full League Run", ""]
    lines.append(f"Ratings calibrated from consensus market win totals (DraftKings/FanDuel/"
                 f"Hard Rock/Caesars 2026-27 O/U lines); picks graded 1-10 via the swap-resolved "
                 f"pipeline. {TRIALS_PER_TEAM} simulation trials per team.")
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

    print(f"\nGrading {len(requested)} team(s), {TRIALS_PER_TEAM} trials each...")
    t0 = time.time()
    all_results: Dict[str, Tuple[List[dict], List[tuple]]] = {}
    for i, name in enumerate(requested, 1):
        graded, unresolved = grade_team(name, teams)
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
