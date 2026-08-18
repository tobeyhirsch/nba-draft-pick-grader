"""
Full real-league orchestrator: real market-calibrated ratings
(market_ratings.py), real conferences (conferences.py), real pick
ownership (draft_picks_data.py), real swap resolution (swap_resolver.py /
pick_resolver.py) -- runs the entire 30-team pipeline end to end and grades
every pick every team owns, 1-10.

Run with:
  python run_real_league.py                 # grade every team (slow, see below)
  python run_real_league.py "Boston Celtics" "Atlanta Hawks"   # grade just these

Writes a full results report to league_pick_grades.md, and the projected
standings each year's picks are actually simulated from to
projected_standings.md (see build_projected_standings), in addition to
printing a summary. 2027 and 2033's standings will come out identical --
both use the same base market ratings with the same seed (2033 falls
outside darko_ratings.py's evolved-ratings window, see its docstring), not
a bug.

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
import re
import sys
import time
from typing import Dict, List, Optional, Sequence, Tuple

from market_ratings import load_market_win_totals, build_calibrated_teams
from conferences import TEAM_CONFERENCE
from draft_picks_data import TEAM_FUTURE_PICKS
from pick_resolver import build_pick_assets
from pick_grading import grade_pick_portfolio
from pick_restrictions_321 import DEFAULT_2027_HISTORY
from standings_sim import Team, expected_wins
from data_paths import find_data_file
from darko_ratings import (
    all_teams_net_ratings, fit_darko_to_elo,
    future_year_teams, MAX_OFFSET, FIRST_DRAFT_YEAR_COVERED,
)
from player_value_regression import load_darko_players_with_projection

# Checks several common data/ locations relative to THIS file (see
# data_paths.py) rather than assuming one fixed layout -- works whether
# data/ sits next to this file or as a sibling of a src/ folder it's in.
MARKET_XLSX = find_data_file("market_win_totals.xlsx", os.path.dirname(os.path.abspath(__file__)))
CALIBRATION_SEED = 11
GRADING_SEED = 5
TRIALS_PER_TEAM = 2000  # lower = faster/noisier, higher = slower/tighter
STANDINGS_TRIALS = 2000  # trials per year for the projected-standings report (build_projected_standings)
RESULTS_FILE = "league_pick_grades.md"
STANDINGS_FILE = "projected_standings.md"
FINAL_DRAFT_YEAR = FIRST_DRAFT_YEAR_COVERED + MAX_OFFSET  # 2033 -- outside darko_ratings.py's window, falls back to base

# Real multi-year advanced-stats CSV (schema documented in
# player_value_regression.py; built by build_multi_year_stats.py from the
# user-supplied "Advanced Stats.xlsx" -- DARKO DPM + Basketball-Reference
# PER/BPM/VORP/Age for 2023-24 through 2025-26) -- upgrades every eligible
# player's DPM input from a single-season snapshot to a regression-
# projected next-season value. Set back to None to fall back to
# darko_ratings.py's original single-year behavior, unchanged (see
# player_value_regression.py's STATUS note).
MULTI_YEAR_STATS_CSV = find_data_file("multi_year_advanced_stats.csv", os.path.dirname(os.path.abspath(__file__)))


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
    team, never up, which is why the window stops at 2032). Each player's
    DPM input comes from load_darko_players_with_projection() -- a
    regression-projected next-season value when MULTI_YEAR_STATS_CSV is
    set and that player has enough historical seasons, otherwise the same
    raw current-season DPM darko_ratings.load_darko_players() always used
    (see player_value_regression.py; MULTI_YEAR_STATS_CSV is None by
    default, so this is a no-op today).
    """
    players = load_darko_players_with_projection(MULTI_YEAR_STATS_CSV)
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


def build_projected_standings(base_teams: Sequence[Team], teams_by_year: Dict[int, List[Team]],
                               trials: int = STANDINGS_TRIALS, seed: int = CALIBRATION_SEED
                               ) -> Dict[int, Dict[str, float]]:
    """
    {draft_year: {team_name: avg_wins}} for every year this pipeline
    actually simulates a lottery for (2027 through FINAL_DRAFT_YEAR) --
    the SAME ratings that drive every pick distribution elsewhere (grade_team,
    build_pick_assets), run through standings_sim.expected_wins() with no
    lottery/draft-order machinery attached, so this is a direct readout of
    "what does the model think the standings look like," not a separately
    re-derived number that could drift out of sync with the pick grades.

    2027 uses base_teams (real 2026-27 market ratings) directly. 2028-2032
    use teams_by_year's DARKO+longevity-evolved ratings. FINAL_DRAFT_YEAR
    (2033) falls back to base_teams, same as everywhere else this fallback
    happens (see build_future_year_teams and pick_resolver.build_pick_assets).
    """
    years = [FIRST_DRAFT_YEAR_COVERED - 1] + list(range(FIRST_DRAFT_YEAR_COVERED,
                                                          FIRST_DRAFT_YEAR_COVERED + MAX_OFFSET)) + [FINAL_DRAFT_YEAR]
    result: Dict[int, Dict[str, float]] = {}
    for year in years:
        league = teams_by_year.get(year, base_teams)
        result[year] = expected_wins(league, trials=trials, seed=seed)
    return result


def write_standings_report(standings_by_year: Dict[int, Dict[str, float]], conferences: Dict[str, str],
                            path: str) -> None:
    lines = ["# Projected Standings -- Underlying the Pick Value Projections", ""]
    lines.append(f"Average simulated wins per team per season ({STANDINGS_TRIALS} trials each), for the "
                 f"SAME ratings that drive every pick distribution/grade in {RESULTS_FILE}: real 2026-27 "
                 f"market ratings for {FIRST_DRAFT_YEAR_COVERED - 1}, DARKO+longevity-evolved ratings "
                 f"(darko_ratings.py) for {FIRST_DRAFT_YEAR_COVERED}-{FIRST_DRAFT_YEAR_COVERED + MAX_OFFSET - 1}, "
                 f"and the flat {FIRST_DRAFT_YEAR_COVERED - 1} market ratings again for "
                 f"{FINAL_DRAFT_YEAR} (outside darko_ratings.py's window -- see its module docstring for why "
                 f"the window stops where it does). These are regular-season win projections only -- no "
                 f"play-in/lottery/draft-order logic runs here, that all happens downstream in "
                 f"draft_pipeline_321.py using these same ratings.")
    lines.append("")

    for year in sorted(standings_by_year):
        wins = standings_by_year[year]
        lines.append(f"## {year - 1}-{str(year)[2:]} season (feeds the {year} draft)")
        lines.append("")
        for conf in ["East", "West"]:
            conf_teams = sorted((n for n in wins if conferences.get(n) == conf), key=lambda n: -wins[n])
            if not conf_teams:
                continue
            leader_wins = wins[conf_teams[0]]
            lines.append(f"### {conf}")
            lines.append("")
            lines.append("| Rank | Team | Avg W | Avg L | GB |")
            lines.append("|---|---|---|---|---|")
            for i, name in enumerate(conf_teams, 1):
                w = wins[name]
                gb = leader_wins - w
                lines.append(f"| {i} | {name} | {w:.1f} | {82 - w:.1f} | {gb:.1f} |")
            lines.append("")

    with open(path, "w") as f:
        f.write("\n".join(lines))


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


def pick_round(label: str) -> str:
    """
    "1st" or "2nd", read off a graded pick's label. Every label this
    pipeline generates embeds its round as a standalone "1st"/"2nd" token
    (see pick_resolver.py's `label = f"{year} {team_code} {round_str}..."`
    and swap_resolver.swap_to_pick_asset's equivalent) -- this doesn't
    re-derive anything, it just reads that token back out for report
    presentation. Returns "Unknown" (and the label is still shown, just
    grouped separately) if a label somehow doesn't carry one, rather than
    silently mis-bucketing it.
    """
    if re.search(r"\b1st\b", label):
        return "1st"
    if re.search(r"\b2nd\b", label):
        return "2nd"
    return "Unknown"


def _split_by_round(graded: List[dict]) -> Dict[str, List[dict]]:
    by_round: Dict[str, List[dict]] = {"1st": [], "2nd": [], "Unknown": []}
    for g in graded:
        by_round[pick_round(g["label"])].append(g)
    return by_round


def _avg_grade(picks: List[dict]) -> Optional[float]:
    return sum(g["grade"] for g in picks) / len(picks) if picks else None


def write_report(all_results: Dict[str, Tuple[List[dict], List[tuple]]], path: str) -> None:
    lines = ["# NBA Draft Pick Grades -- Full League Run", ""]
    lines.append(f"2027-draft ratings calibrated from consensus market win totals (DraftKings/"
                 f"FanDuel/Hard Rock/Caesars 2026-27 O/U lines); the {FIRST_DRAFT_YEAR_COVERED}-"
                 f"{FIRST_DRAFT_YEAR_COVERED + MAX_OFFSET - 1} drafts use DARKO DPM + career "
                 f"longevity data instead, calibrated against those same market ratings "
                 f"(darko_ratings.py); 2033 falls back to the flat 2026-27 market ratings. "
                 f"Picks graded 1-10 via the swap-resolved pipeline. {TRIALS_PER_TEAM} simulation "
                 f"trials per team per draft year. Grades and averages below are split by round --"
                 f" 2nd-round picks carry the pick_valuation.py 0.4x haircut baked into their value, "
                 f"so mixing rounds into one average would understate 1st-round strength and "
                 f"overstate 2nd-round weakness relative to each other.")
    lines.append("")

    lines.append("## League summary: average pick grade by team, split by round")
    lines.append("")
    lines.append("| Team | Avg 1st-rd grade | 1st-rd picks | Avg 2nd-rd grade | 2nd-rd picks | Unresolved |")
    lines.append("|---|---|---|---|---|---|")
    summary_rows = []
    for name, (graded, unresolved) in all_results.items():
        by_round = _split_by_round(graded)
        avg1, avg2 = _avg_grade(by_round["1st"]), _avg_grade(by_round["2nd"])
        summary_rows.append((name, avg1, len(by_round["1st"]), avg2, len(by_round["2nd"]), len(unresolved)))
    # Rank by 1st-round average (the higher-value round); teams with no
    # resolved 1st-round picks at all sort to the bottom rather than
    # crashing on a None comparison.
    summary_rows.sort(key=lambda r: (r[1] is None, -(r[1] or 0)))
    for name, avg1, n1, avg2, n2, n_unresolved in summary_rows:
        avg1_str = f"{avg1:.2f}" if avg1 is not None else "--"
        avg2_str = f"{avg2:.2f}" if avg2 is not None else "--"
        lines.append(f"| {name} | {avg1_str} | {n1} | {avg2_str} | {n2} | {n_unresolved} |")
    lines.append("")

    for name, (graded, unresolved) in all_results.items():
        lines.append(f"## {name}")
        lines.append("")
        by_round = _split_by_round(graded)

        for round_label in ["1st", "2nd"]:
            picks = by_round[round_label]
            avg = _avg_grade(picks)
            lines.append(f"### {round_label} Round Picks"
                         + (f" (avg grade {avg:.2f})" if avg is not None else " (none)"))
            lines.append("")
            if picks:
                lines.append("| Pick | Grade | Label |")
                lines.append("|---|---|---|")
                for g in sorted(picks, key=lambda g: -g["grade"]):
                    lines.append(f"| {g['label']} | {g['grade']:.1f} | {g['grade_label']} |")
                lines.append("")

        if by_round["Unknown"]:
            lines.append(f"### Round could not be determined from label ({len(by_round['Unknown'])})")
            lines.append("")
            lines.append("| Pick | Grade | Label |")
            lines.append("|---|---|---|")
            for g in sorted(by_round["Unknown"], key=lambda g: -g["grade"]):
                lines.append(f"| {g['label']} | {g['grade']:.1f} | {g['grade_label']} |")
            lines.append("")

        if unresolved:
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

    print(f"\nProjecting standings for {FIRST_DRAFT_YEAR_COVERED - 1}-{FINAL_DRAFT_YEAR} "
          f"({STANDINGS_TRIALS} trials/year) -- the same ratings driving every pick below...")
    t0 = time.time()
    conferences = {t.name: t.conference for t in teams}
    standings_by_year = build_projected_standings(teams, teams_by_year)
    write_standings_report(standings_by_year, conferences, STANDINGS_FILE)
    print(f"  done in {time.time() - t0:.1f}s -- written to {STANDINGS_FILE}")

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

    print("\n=== League summary: average pick grade by team, split by round ===")
    summary_rows = []
    for name in requested:
        graded, _ = all_results[name]
        by_round = _split_by_round(graded)
        avg1, avg2 = _avg_grade(by_round["1st"]), _avg_grade(by_round["2nd"])
        if avg1 is not None or avg2 is not None:
            summary_rows.append((name, avg1, len(by_round["1st"]), avg2, len(by_round["2nd"])))
    summary_rows.sort(key=lambda r: (r[1] is None, -(r[1] or 0)))
    for name, avg1, n1, avg2, n2 in summary_rows:
        avg1_str = f"{avg1:5.2f}" if avg1 is not None else " --  "
        avg2_str = f"{avg2:5.2f}" if avg2 is not None else " --  "
        print(f"  {name:<28} 1st-rd avg {avg1_str} ({n1:>2} picks)   "
              f"2nd-rd avg {avg2_str} ({n2:>2} picks)")


if __name__ == "__main__":
    main()
