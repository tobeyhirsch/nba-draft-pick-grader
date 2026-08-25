"""
Projects a player's NEXT-SEASON games-played AVAILABILITY (fraction of a
season actually played) from multi-year games history plus age -- the
Tier 1/2 "injury/health variance" data step scoped out in conversation
(darko_ratings.py's presence signals -- longevity, roster_continuity --
answer "is this player still in the league / still on this team," never
"how many games do they actually suit up for"). Mirrors
player_value_regression.py's structure (same multi-year-history + age
regression shape) applied to availability instead of skill.

STATUS -- LIVE against real data. data/multi_year_advanced_stats.csv now
has a "Games" column (added to build_multi_year_stats.py, sourced from
Basketball-Reference's "G" -- using a player's TOT/2TM/3TM/4TM rollup row
when one exists, so a mid-season TRADE isn't misread as missed games; see
that module's "AVAILABILITY DATA" docstring section for why that sourcing
rule deliberately differs from how Age/BPM/VORP/PER are read).

GAMES_PER_SEASON = 82 (the standard NBA season length for all three
seasons currently on file, 2023-24 through 2025-26 -- none were
lockout/COVID-shortened; revisit if a shortened season is ever added).
availability_rate = games / GAMES_PER_SEASON, clipped to [0, 1] at load
time -- exactly one row in the current dataset (Buddy Hield, 2023-24, 84
games) exceeds 82. That's not a data error: Basketball-Reference's
"2TM" rollup for a mid-season-traded player is the literal sum of his
games with each team, and the two teams' 82-game schedules don't fall on
identical calendar dates, so a traded player's combined total isn't
mathematically bounded by 82 the way a single team's is. Clipping to 1.0
there loses no real signal (he was clearly fully available) and keeps the
rate interpretable as a fraction everywhere else.

METHOD (same shape as player_value_regression.py):
  FEATURES per player, from their season-by-season history strictly
  BEFORE the season being predicted:
    - age, age^2 -- a rise-then-decline-shaped durability-by-age curve.
      Same as player_value_regression.py's age terms, this functional form
      is a modeling CHOICE, not fit from this project's own data.
    - most_recent_availability -- the player's most recent on-file
      season's availability_rate.
    - trend -- slope (numpy.polyfit, degree 1) of the availability-rate
      series across the player's history-window seasons.
  REGRESSION: OLS (numpy.linalg.lstsq) predicting next-season
  availability_rate from those four features, clipped to [0, 1] at
  prediction time (a raw OLS output isn't naturally bounded). Same "small,
  interpretable feature set" philosophy and same overfitting-row-count
  warning as player_value_regression.py's fit_regression().

THREE-TIER FALLBACK for a player without enough history to fit the trend
feature (MIN_HISTORY_SEASONS = 2 prior seasons needed) -- ordered from
most to least player-specific, same "use real data if you have ANY of it"
spirit as the rest of this project:
  1. Enough history (>= MIN_HISTORY_SEASONS) -- regression projection.
  2. Some history (1 season, not enough for a trend) -- that ONE real
     season's own availability_rate, unprojected. This differs from
     player_value_regression.py's equivalent fallback only in spirit, not
     mechanics: that module ALSO falls back to a player's own raw
     current-season figure when there's too little history for a trend.
  3. NO history at all (e.g. an incoming rookie never in this dataset) --
     a league-wide, AGE-CONDITIONED average availability_rate (never a
     flat unconditioned average -- durability correlates with age, and
     this project doesn't discard population-level signal just because
     individual signal is missing). Falls back further to the nearest
     age bucket with data, then to the unconditioned overall mean only if
     no age is supplied at all.

WHAT THIS DOES NOT MODEL:
  - Injury TYPE/severity/chronicity -- this is games-missed only, not WHY.
    Distinguishing a chronically injury-prone player from a one-off freak
    incident needs an injury event log (date, reason, duration) this
    project doesn't have access to yet -- Pro Sports Transactions was the
    one candidate source identified, but it sits behind active
    Cloudflare bot-detection and wasn't pulled from (see the conversation
    that scoped this module; that line hasn't moved, don't silently
    route around it here).
  - In-season game-to-game injury risk / load management -- this
    projects a SEASON-level rate, not "is this specific player playing
    tonight."
  - Role/opportunity effects on games played (e.g. a healthy player
    benched for a rebuild, or true rest-driven load management rather
    than injury) -- Basketball-Reference's G counts any game appearance
    regardless of reason for missing others, so this is genuinely about
    AVAILABILITY as observed, not a clean injury-only signal.
  - NOT YET WIRED into darko_ratings.py's team-rating pipeline -- this
    module is validated standalone (see __main__) the same way
    player_value_regression.py was before it was connected via
    ProjectionContext; connecting an availability multiplier into
    team_net_rating's presence() weighting is a natural follow-up, not
    done here.
"""

from __future__ import annotations

import csv
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple

import numpy as np

GAMES_PER_SEASON = 82
MIN_HISTORY_SEASONS = 2  # need >= this many prior seasons to build the trend feature
FEATURE_NAMES = ["age", "age_squared", "most_recent_availability", "trend"]


@dataclass
class SeasonAvailability:
    player: str
    team: str
    season: int  # ending year, e.g. 2025 for the 2024-25 season
    age: float
    availability_rate: float  # games / GAMES_PER_SEASON, clipped to [0, 1]


@dataclass
class AvailabilityModel:
    coefficients: Dict[str, float]
    intercept: float
    r_squared: float
    n_training_rows: int
    age_baseline: Dict[int, float]  # rounded age -> league-wide mean availability_rate (Tier 3 fallback)

    def predict(self, features: Dict[str, float]) -> float:
        raw = self.intercept + sum(self.coefficients[f] * features[f] for f in FEATURE_NAMES)
        return float(np.clip(raw, 0.0, 1.0))


def load_availability_history(csv_path: str) -> Dict[str, List[SeasonAvailability]]:
    """Loads data/multi_year_advanced_stats.csv's Games column. Returns {player: [SeasonAvailability, ...]} sorted by season ascending."""
    by_player: Dict[str, List[SeasonAvailability]] = {}
    with open(csv_path, encoding="utf-8-sig") as f:
        for row in csv.DictReader(f):
            games = int(row["Games"])
            rate = min(1.0, games / GAMES_PER_SEASON)
            s = SeasonAvailability(
                player=row["Player"].strip(), team=row["Team"].strip(),
                season=int(row["Season"]), age=float(row["Age"]),
                availability_rate=rate,
            )
            by_player.setdefault(s.player, []).append(s)
    for player in by_player:
        by_player[player].sort(key=lambda s: s.season)
    return by_player


def build_features(history: List[SeasonAvailability], years_ahead: int = 1) -> Dict[str, float]:
    """
    history: a player's seasons in chronological order, STRICTLY BEFORE the
    season being predicted/projected. Needs >= MIN_HISTORY_SEASONS entries.

    years_ahead=1 (immediate next season) uses age/most_recent_availability/
    trend all as-is. years_ahead > 1 -- used to project a DIFFERENT
    availability rate for EACH future draft year instead of reusing one
    fixed value everywhere, the same fix already applied to
    player_value_regression.project_season -- advances only age/age^2 by
    (years_ahead - 1) extra years; most_recent_availability/trend stay
    anchored to the player's last REAL observed data, for the identical
    reason given in player_value_regression.project_season's docstring
    (no real data to recompute a trend from further out, and extrapolating
    a slope fit from a handful of seasons multiple years ahead would
    compound noise, not add signal).
    """
    if len(history) < MIN_HISTORY_SEASONS:
        raise ValueError(f"Need >= {MIN_HISTORY_SEASONS} seasons of history, got {len(history)}")
    if years_ahead < 1:
        raise ValueError(f"years_ahead must be >= 1, got {years_ahead}")
    latest = history[-1]
    rates = [s.availability_rate for s in history]
    idx = np.arange(len(rates))
    trend = float(np.polyfit(idx, rates, 1)[0])
    age = latest.age + (years_ahead - 1)
    return {
        "age": age,
        "age_squared": age ** 2,
        "most_recent_availability": rates[-1],
        "trend": trend,
    }


def _age_conditioned_baseline(by_player: Dict[str, List[SeasonAvailability]]) -> Dict[int, float]:
    """League-wide mean availability_rate by rounded age, pooled across every player-season on file -- the Tier 3 fallback."""
    by_age: Dict[int, List[float]] = {}
    for seasons in by_player.values():
        for s in seasons:
            by_age.setdefault(round(s.age), []).append(s.availability_rate)
    return {age: float(np.mean(rates)) for age, rates in by_age.items()}


def build_training_rows(by_player: Dict[str, List[SeasonAvailability]]) -> Tuple[np.ndarray, np.ndarray]:
    """Expanding-window training examples, same convention as player_value_regression.build_training_rows."""
    X, y = [], []
    for seasons in by_player.values():
        for t in range(MIN_HISTORY_SEASONS, len(seasons)):
            history = seasons[:t]
            target = seasons[t]
            feats = build_features(history)
            X.append([feats[f] for f in FEATURE_NAMES])
            y.append(target.availability_rate)
    return np.array(X), np.array(y)


def fit_availability_model(by_player: Dict[str, List[SeasonAvailability]]) -> AvailabilityModel:
    X, y = build_training_rows(by_player)
    if len(y) < len(FEATURE_NAMES) + 1:
        raise ValueError(
            f"Only {len(y)} training row(s) available (need at least {len(FEATURE_NAMES) + 1} to fit "
            f"{len(FEATURE_NAMES)} features + an intercept without an underdetermined system) -- "
            f"supply more players/seasons."
        )
    X_design = np.column_stack([X, np.ones(len(X))])
    coefs_full, _residuals, _rank, _sv = np.linalg.lstsq(X_design, y, rcond=None)
    coefficients = dict(zip(FEATURE_NAMES, (float(c) for c in coefs_full[:-1])))
    intercept = float(coefs_full[-1])

    pred = X_design @ coefs_full
    ss_res = float(np.sum((y - pred) ** 2))
    ss_tot = float(np.sum((y - y.mean()) ** 2))
    r_squared = 1 - ss_res / ss_tot if ss_tot > 0 else float("nan")

    min_recommended_rows = 3 * (len(FEATURE_NAMES) + 1)
    if len(y) < min_recommended_rows:
        print(f"[player_availability_model] WARNING: only {len(y)} training rows for "
              f"{len(FEATURE_NAMES) + 1} free parameters (want >= {min_recommended_rows}). "
              f"r^2={r_squared:.3f} on a fit this underdetermined likely reflects overfitting/"
              f"memorization, not real predictive power -- do not trust this fit until more "
              f"players/seasons are supplied.")

    age_baseline = _age_conditioned_baseline(by_player)

    # A weak fit here is EXPECTED, not a bug to chase: unlike skill (DPM),
    # which trends smoothly with age/recent form (player_value_regression.py
    # fits r^2~=0.64 on the same shape of features), games-missed is
    # dominated by acute, largely unpredictable events -- this number
    # being much lower is itself the honest finding "games history alone
    # explains only a small share of next-season availability," not a
    # signal something's wrong with the fit.
    if r_squared < 0.15:
        print(f"[player_availability_model] NOTE: r^2={r_squared:.3f} is genuinely low (compare "
              f"player_value_regression.py's ~0.64 on the same feature shape for skill) -- this "
              f"reflects that games-missed is dominated by largely unpredictable acute events, not "
              f"a fit-quality bug. Treat regression-tier projections as a weak prior, not a precise "
              f"forecast; this is exactly why the age-conditioned baseline exists as a real fallback "
              f"rather than a last resort to avoid.")

    return AvailabilityModel(coefficients=coefficients, intercept=intercept,
                              r_squared=r_squared, n_training_rows=len(y),
                              age_baseline=age_baseline)


def project_availability(player: str, by_player: Dict[str, List[SeasonAvailability]],
                          model: AvailabilityModel, years_ahead: int = 1,
                          age_if_no_history: Optional[float] = None) -> Tuple[float, str]:
    """
    Returns (projected_availability_rate, source) -- see module docstring's
    THREE-TIER FALLBACK section for what `source` can be: "regression",
    "own_last_season", "age_baseline", or "league_average".

    years_ahead: see build_features -- projects a DIFFERENT rate for each
    horizon instead of reusing years_ahead=1's value everywhere. Only
    affects the "regression" tier (age advances there); "own_last_season"
    has no further data to age-adjust from (same reasoning as
    player_value_regression's equivalent short-history fallback), and
    "age_baseline"/"league_average" are keyed by whatever age the caller
    passes in `age_if_no_history` directly (pass the age AT THE TARGET
    SEASON, already advanced -- this function doesn't advance it itself
    for those two tiers, since there's no per-player history to advance
    FROM).
    """
    history = by_player.get(player)
    if history and len(history) >= MIN_HISTORY_SEASONS:
        feats = build_features(history, years_ahead=years_ahead)
        return model.predict(feats), "regression"

    if history:  # some history, just not enough for a trend
        return history[-1].availability_rate, "own_last_season"

    if age_if_no_history is not None:
        rounded = round(age_if_no_history)
        if rounded in model.age_baseline:
            return model.age_baseline[rounded], "age_baseline"
        nearest = min(model.age_baseline, key=lambda a: abs(a - rounded))
        return model.age_baseline[nearest], "age_baseline"

    return float(np.mean(list(model.age_baseline.values()))), "league_average"


@dataclass
class AvailabilityContext:
    """Bundles a fitted AvailabilityModel with the multi-year history it
    was fit from, so a caller (darko_ratings.py) can request a given
    player's availability rate at any years_ahead horizon on demand --
    same pattern as player_value_regression.ProjectionContext."""
    model: AvailabilityModel
    by_player: Dict[str, List[SeasonAvailability]]

    def rate_at(self, player: str, years_ahead: int, age_if_no_history: Optional[float] = None) -> Tuple[float, str]:
        return project_availability(player, self.by_player, self.model,
                                     years_ahead=years_ahead, age_if_no_history=age_if_no_history)


def load_availability_context(csv_path: str) -> Optional["AvailabilityContext"]:
    """Loads csv_path (data/multi_year_advanced_stats.csv's Games column)
    and fits an AvailabilityModel, returning an AvailabilityContext callers
    can query at any years_ahead horizon. Returns None if the file has no
    usable player -- callers should fall back to no-op (unweighted)
    behavior in that case, same convention as
    player_value_regression.load_projection_context."""
    by_player = load_availability_history(csv_path)
    has_enough_history = any(len(seasons) >= MIN_HISTORY_SEASONS for seasons in by_player.values())
    if not has_enough_history:
        print(f"[player_availability_model] {csv_path!r} has no player with >= {MIN_HISTORY_SEASONS} "
              f"seasons on file -- nothing to train on.")
        return None
    # Pass the FULL by_player (not pre-filtered to >= MIN_HISTORY_SEASONS)
    # -- build_training_rows already naturally contributes zero rows for a
    # short-history player (its range() is empty), so filtering here would
    # only have the side effect of shrinking _age_conditioned_baseline's
    # population for no benefit; a 1-season player still contributes real
    # signal to "average availability at age 23," it just can't train the
    # regression itself.
    model = fit_availability_model(by_player)
    return AvailabilityContext(model=model, by_player=by_player)


if __name__ == "__main__":
    from data_paths import find_data_file
    import os

    csv_path = find_data_file("multi_year_advanced_stats.csv", os.path.dirname(os.path.abspath(__file__)))
    by_player = load_availability_history(csv_path)
    print(f"Loaded availability history for {len(by_player)} players, "
          f"{sum(len(v) for v in by_player.values())} player-seasons total")

    model = fit_availability_model(by_player)
    print(f"\nFitted on {model.n_training_rows} training rows, r^2 = {model.r_squared:.3f}")
    print("Coefficients:")
    for name, coef in model.coefficients.items():
        print(f"  {name:<28} {coef:+.4f}")
    print(f"  {'intercept':<28} {model.intercept:+.4f}")

    tier_counts = {"regression": 0, "own_last_season": 0, "age_baseline": 0, "league_average": 0}
    for player, seasons in by_player.items():
        _, source = project_availability(player, by_player, model, age_if_no_history=seasons[-1].age)
        tier_counts[source] += 1
    print(f"\nFallback tier breakdown across {len(by_player)} players with >=1 season on file:")
    for tier, count in tier_counts.items():
        print(f"  {tier:<18} {count}")
    print(f"  (a brand-new player with ZERO seasons on file -- not exercised above, since every "
          f"player iterated here has at least one -- would land in 'age_baseline' or 'league_average')")

    print(f"\nAge-conditioned baseline (Tier 3 fallback), sample ages:")
    for age in [20, 23, 27, 30, 33, 36, 39]:
        if age in model.age_baseline:
            print(f"  age {age}: {model.age_baseline[age]:.3f} ({model.age_baseline[age]*GAMES_PER_SEASON:.0f} games/{GAMES_PER_SEASON})")

    print(f"\n--- Spot check: a few real players' next-season projections ---")
    print(f"{'Player':<26}{'Last season rate':>18}{'Projected next':>16}{'Source':>18}")
    for name in ["LeBron James", "Joel Embiid", "Victor Wembanyama", "Zion Williamson", "Kawhi Leonard"]:
        if name not in by_player:
            print(f"{name:<26}  (not in dataset)")
            continue
        seasons = by_player[name]
        last_rate = seasons[-1].availability_rate
        projected, source = project_availability(name, by_player, model, age_if_no_history=seasons[-1].age)
        print(f"{name:<26}{last_rate:>18.3f}{projected:>16.3f}{source:>18}")
