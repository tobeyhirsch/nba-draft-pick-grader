"""
The "picks feed forward" multi-year simulation: unlike the rest of this
pipeline (where every draft year 2027-2033 is simulated as its own
INDEPENDENT trial batch against a fixed set of ratings -- see
draft_pipeline_321.py's and run_real_league.py's docstrings), this module
runs a genuinely SEQUENTIAL, per-trial-correlated simulation: within one
simulated "world," 2027's season and draft actually happen first, real
draft-pick ownership (trades, protections, swaps, same-year conditionals --
see pick_ownership_resolver.py) is resolved against THAT trial's actual
results to determine which team really receives each pick, the player each
team ends up drafting is assumed to pan out according to
pick_outcome_model.py's real-outcome-tier probabilities, THAT team's
projected rating for 2028 is bumped accordingly, THEN 2028's season and
draft are simulated using that world's now-updated ratings, and so on
through 2033. Run many worlds and average, and you get an honest answer to
"how much does actually drafting well in 2027 tend to compound into a
team's strength by 2030, 2033, etc." -- which the rest of the pipeline
cannot answer, because nowhere else does one year's simulated draft
outcome affect a later year's simulated ratings.

THE SEQUENCE, PER SIMULATED WORLD, PER YEAR (2027 through 2033):
  1. Project that season's team strength (base decay-only DARKO projection
     for the year, plus this world's accumulated draft-value delta from
     every PRIOR year's ACTUALLY-OWNED picks -- see step 7).
  2. Run the lottery/draft-order simulation
     (draft_pipeline_321._simulate_321_draft_core), including the
     no-repeat-#1 / no-3-straight-top-5 restrictions
     (pick_restrictions_321.py), chained forward exactly like the rest of
     the pipeline via advance_history(). This determines each team's OWN
     natural first- and second-round SLOT (pick number 1-60) -- who EARNED
     which pick by their own record, not who ends up drafting with it.
  3. Resolve the ACTUAL ownership of every one of those 60 picks this trial
     via pick_ownership_resolver.resolve_pick_ownership_for_year(), which
     evaluates draft_picks_data.py's real trade/protection/swap/same-year-
     conditional language against this trial's actual pick numbers.
  4. That resolution directly answers "which team actually receives each
     pick" -- pick_ownership_resolver.py credits nobody for a pick whose
     fate depends on a fragment its scope doesn't cover (a cross-YEAR
     conditional, nested/elliptical text, or a fragment that genuinely
     conflicts with another team's claim on the same physical pick in the
     raw source data -- see that module's docstring), rather than falling
     back to the natural-slot team and risking a silent double-count.
  5. sample_outcome_tier() (pick_outcome_model.py, fit from the 2015-2025
     draft-outcomes spreadsheet) samples a career-outcome tier for each
     pick, by PICK NUMBER (a pick's real difficulty/value is about where in
     the draft it falls, regardless of who ends up owning it).
  6. That outcome is credited to the team that step 3/4 says actually OWNS
     the pick -- NOT automatically to the team whose record generated it.
  7. team_dpm_delta() (pick_outcome_model.py) converts tier + pick number +
     years-since-drafted into an assumed DPM contribution (ramping in over
     the player's first four years), added to the OWNING team's
     accumulated draft-value delta, then converted to the same Elo scale
     team ratings already use via the pipeline's existing DARKO-to-Elo fit.
  8. That updated rating feeds step 1 for the NEXT year, and the cycle
     repeats through 2033.

WHY THIS IS A SEPARATE MODULE, NOT A CHANGE TO run_real_league.py's
EXISTING FUNCTIONS: build_projected_standings() and
build_restriction_history_by_year() are both intentionally NOT fully
correlated across years (see the latter's docstring) -- that's a
consistent, documented modeling choice for the rest of the pipeline, which
mostly cares about "grade the picks a team owns," not "simulate the
league's future." This module is additive: it doesn't change any existing
function's behavior, it adds a genuinely different (more correlated, more
expensive) simulation for the specific question "how does drafting well
now compound forward."

SCOPE LIMITATIONS (read before trusting the output):
- Pick ownership is resolved to the SAME extent pick_resolver.py/
  swap_resolver.py already resolve it elsewhere in this pipeline: simple/
  protected picks, flat swaps, same-year cross-pick conditionals, and
  2-level nested swaps (410 of 451 real fragments, 91%). The remaining 9%
  (cross-year conditionals, nested/elliptical text, a handful of genuine
  same-pick conflicts in the raw source data -- see
  pick_ownership_resolver.py) credit nobody for that specific pick that
  trial, rather than guessing. This UNDER-counts total league-wide draft
  value slightly (a small number of real picks go uncredited to anyone
  some trials) but never mis-attributes a pick to the wrong team.
- The talent-arrival mechanism (pick_outcome_model.py) is three documented
  judgment calls (tier-to-DPM mapping, minutes ramp, second-round
  extrapolation) layered on top of real historical tier-probability data --
  see that module's docstring for exactly which numbers are real and which
  are assumptions.
- This does NOT replace darko_ratings.py's existing decay-only evolution
  model; it starts from that model's output (teams_by_year) and ADDS the
  draft-value delta on top, so the existing "can only ever go flat-or-
  down" ceiling is now allowed to be broken specifically by teams' real
  drafted/acquired picks.
"""

import random
from typing import Dict, List, Sequence, Tuple

from standings_sim import Team
from conferences import TEAM_CONFERENCE
from draft_pipeline_321 import _simulate_321_draft_core, simulate_second_round_order
from pick_restrictions_321 import DEFAULT_2027_HISTORY, advance_history
from pick_outcome_model import sample_outcome_tier, team_dpm_delta
from pick_ownership_resolver import resolve_pick_ownership_for_year
from team_codes import TEAM_NAME_TO_ABBREV
from darko_ratings import all_teams_net_ratings, fit_darko_to_elo, future_year_teams, MAX_OFFSET, FIRST_DRAFT_YEAR_COVERED
from player_value_regression import load_darko_players_with_projection, load_projection_context
from player_availability_model import load_availability_context

YEARS: List[int] = [2027, 2028, 2029, 2030, 2031, 2032, 2033]
FINAL_DRAFT_YEAR = FIRST_DRAFT_YEAR_COVERED + MAX_OFFSET  # 2033, matches run_real_league.py


def _build_base_by_year(base_teams: Sequence[Team], multi_year_stats_csv) -> Tuple[Dict[int, List[Team]], float]:
    """
    {year: teams} using the SAME darko_ratings.py decay-only evolution the
    rest of the pipeline uses (2027 and 2033 fall back to base_teams,
    2028-2032 use future_year_teams) -- this is the "no draft feedback"
    floor this module adds its delta on top of. Also returns the fitted
    DARKO-to-Elo slope (see darko_ratings.fit_darko_to_elo), reused below
    to convert a drafted player's assumed DPM contribution into the same
    Elo units team ratings are already expressed in.
    """
    players = load_darko_players_with_projection(multi_year_stats_csv)
    darko_now = all_teams_net_ratings(players, offset=0)
    market_elo = {t.name: t.rating for t in base_teams}
    slope, intercept, _r2 = fit_darko_to_elo(darko_now, market_elo)
    conferences = {t.name: t.conference for t in base_teams}
    projection_ctx = load_projection_context(multi_year_stats_csv) if multi_year_stats_csv else None
    availability_ctx = load_availability_context(multi_year_stats_csv) if multi_year_stats_csv else None

    by_year: Dict[int, List[Team]] = {2027: list(base_teams), FINAL_DRAFT_YEAR: list(base_teams)}
    for offset in range(1, MAX_OFFSET + 1):
        year = FIRST_DRAFT_YEAR_COVERED + offset - 1
        by_year[year] = future_year_teams(players, offset, slope, intercept, conferences,
                                           projection_ctx, availability_ctx)
    return by_year, slope


def run_worlds(base_teams: Sequence[Team], num_worlds: int = 300, seed: int = 71,
                games_per_team: int = 82, multi_year_stats_csv=None
                ) -> Dict[int, Dict[str, List[Dict]]]:
    """
    Runs `num_worlds` independent sequential 2027-2033 simulations. Returns
    {year: {team_name: [per-world dict, one per world]}}, where each
    per-world dict is:
      "wins": int -- this world's simulated win total.
      "rating": float -- this world's rating USED to simulate that year,
        i.e. base decay-only projection + accumulated draft-value delta
        from every pick this team has ACTUALLY OWNED in prior years.
      "natural_pick_round1" / "natural_pick_round2": int -- this team's OWN
        first-/second-round draft SLOT this year (1-30 / 31-60), purely
        from its own record -- informational; does NOT necessarily say
        what this team drafts with, see "owned_picks".
      "owned_picks": List[Tuple[int, str]] -- every (pick_number, round_str)
        this team ACTUALLY receives this year once real trades/protections/
        swaps/conditionals are resolved (pick_ownership_resolver.py). Can
        be empty (all picks traded away), or contain more than 2 entries
        (a team that's acquired extra picks).
      "delta_from_picks": float -- Elo points added to this team's rating
        this year from every pick it has actually owned in prior years,
        cumulative.

    See this module's docstring for the full per-year sequence. Historical
    note: an earlier version of this function credited each team for its
    OWN natural draft slot only (`{**first_round, **second_round}`, which
    additionally had a key-collision bug that silently dropped every
    team's first-round credit -- see git history / the project README for
    that fix). This version routes outcomes through real pick ownership
    instead (`pick_ownership_resolver.resolve_pick_ownership_for_year`),
    per explicit follow-up request.
    """
    base_by_year, slope = _build_base_by_year(base_teams, multi_year_stats_csv)
    rng = random.Random(seed)

    results: Dict[int, Dict[str, List[Dict]]] = {year: {t.name: [] for t in base_teams} for year in YEARS}

    for _world in range(num_worlds):
        history = DEFAULT_2027_HISTORY
        # RECEIVING team_name -> list of (draft_year, pick_number, tier),
        # one entry per pick that team actually ended up owning that year
        # (0, 1, or several -- see resolve_pick_ownership_for_year).
        draft_history: Dict[str, List[Tuple[int, int, str]]] = {t.name: [] for t in base_teams}

        for year in YEARS:
            base_teams_this_year = base_by_year[year]
            this_year_teams: List[Team] = []
            deltas: Dict[str, float] = {}
            for t in base_teams_this_year:
                dpm_delta = 0.0
                for draft_year, pick_number, tier in draft_history[t.name]:
                    years_since = year - draft_year
                    dpm_delta += team_dpm_delta(pick_number, tier, years_since)
                elo_delta = slope * dpm_delta
                deltas[t.name] = elo_delta
                this_year_teams.append(Team(name=t.name, rating=t.rating + elo_delta, conference=t.conference))

            wins, first_round = _simulate_321_draft_core(this_year_teams, rng=rng,
                                                           games_per_team=games_per_team, history=history)
            second_round = simulate_second_round_order(first_round, wins)
            history = advance_history(history, first_round)

            # Real pick ownership for this trial -- who actually receives
            # each of the 60 (team's own natural slot) picks, per
            # draft_picks_data.py's trade/protection/swap/conditional text.
            pick_numbers_by_code = {
                TEAM_NAME_TO_ABBREV[name]: {"1st": first_round[name], "2nd": second_round[name]}
                for name in first_round
            }
            owned = resolve_pick_ownership_for_year(pick_numbers_by_code, year)

            for t in this_year_teams:
                results[year][t.name].append({
                    "wins": wins[t.name],
                    "rating": t.rating,
                    "natural_pick_round1": first_round[t.name],
                    "natural_pick_round2": second_round[t.name],
                    "owned_picks": list(owned.get(t.name, [])),
                    "delta_from_picks": deltas[t.name],
                })

            # Credit outcomes to whoever actually OWNS each pick, not
            # whoever's record produced it.
            for team_name, picks in owned.items():
                for pick_number, _round_str in picks:
                    tier = sample_outcome_tier(pick_number, rng)
                    draft_history[team_name].append((year, pick_number, tier))

    return results


def summarize(results: Dict[int, Dict[str, List[Dict]]]) -> Dict[int, Dict[str, Dict[str, float]]]:
    """
    {year: {team: {"avg_wins", "avg_rating", "avg_delta_from_picks",
    "avg_picks_owned"}}} -- per-team, per-year averages across all worlds.
    avg_delta_from_picks is the headline number: how many Elo points, on
    average, has this team's ACTUALLY-OWNED picks added to (or, if
    negative, subtracted from) its rating by this year. avg_picks_owned is
    a diagnostic: how many picks (round 1 + round 2, summed across all
    years up to and including this one) this team has actually ended up
    owning on average -- a team that trades away picks should trend well
    below 2/year, one that accumulates them well above.
    """
    summary: Dict[int, Dict[str, Dict[str, float]]] = {}
    for year, by_team in results.items():
        summary[year] = {}
        for team, world_rows in by_team.items():
            n = len(world_rows)
            summary[year][team] = {
                "avg_wins": sum(r["wins"] for r in world_rows) / n,
                "avg_rating": sum(r["rating"] for r in world_rows) / n,
                "avg_delta_from_picks": sum(r["delta_from_picks"] for r in world_rows) / n,
                "avg_picks_owned_this_year": sum(len(r["owned_picks"]) for r in world_rows) / n,
            }
    return summary


if __name__ == "__main__":
    import time
    from market_ratings import load_market_win_totals, build_calibrated_teams
    from data_paths import find_data_file
    import os

    market_xlsx = find_data_file("market_win_totals.xlsx", os.path.dirname(os.path.abspath(__file__)))
    win_totals = load_market_win_totals(market_xlsx)
    base_teams = build_calibrated_teams(win_totals, TEAM_CONFERENCE, seed=11, trials_per_iteration=400, iterations=30)

    NUM_WORLDS = int(os.environ.get("SEQ_SIM_WORLDS", "50"))
    print(f"Running {NUM_WORLDS} sequential 2027-2033 worlds (real pick ownership routing)...")
    t0 = time.time()
    results = run_worlds(base_teams, num_worlds=NUM_WORLDS)
    print(f"Done in {time.time() - t0:.1f}s")

    summary = summarize(results)
    print("\nAvg rating-points-added-by-actually-owned-picks, by year (league average across 30 teams):")
    for year in YEARS:
        vals = [summary[year][t.name]["avg_delta_from_picks"] for t in base_teams]
        owned_vals = [summary[year][t.name]["avg_picks_owned_this_year"] for t in base_teams]
        print(f"  {year}: league avg delta = {sum(vals)/len(vals):+.2f} Elo, "
              f"min = {min(vals):+.2f}, max = {max(vals):+.2f}, "
              f"avg picks owned this year = {sum(owned_vals)/len(owned_vals):.2f}")

    print("\n2033 rankings by avg_delta_from_picks (top 5 / bottom 5):")
    ranked = sorted(base_teams, key=lambda t: -summary[2033][t.name]["avg_delta_from_picks"])
    for t in ranked[:5]:
        print(f"  {t.name}: {summary[2033][t.name]['avg_delta_from_picks']:+.2f}")
    print("  ...")
    for t in ranked[-5:]:
        print(f"  {t.name}: {summary[2033][t.name]['avg_delta_from_picks']:+.2f}")
