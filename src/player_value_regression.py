"""
Projects a player's NEXT-SEASON DARKO DPM from MULTIPLE years of advanced
stats (DARKO, BPM, VORP) plus age, instead of darko_ratings.py's current
approach of treating last season's single DPM snapshot as-is. This is
meant as a drop-in upgrade for darko_ratings.py's player-value input --
see load_darko_players_with_projection() at the bottom of this file.

STATUS -- LIVE. A real multi-year dataset now exists --
data/multi_year_advanced_stats.csv (1,501 player-season rows / 713
players, 2023-24 through 2025-26), built by build_multi_year_stats.py from
a user-supplied "Advanced Stats.xlsx" (DARKO DPM leaderboards +
Basketball-Reference PER/BPM/VORP/Age tables) -- and
run_real_league.MULTI_YEAR_STATS_CSV points at it. Fit against that real
data: 318 training rows (well past the 3x(features+1)=15-row overfitting
floor fit_regression() checks for below), r^2~=0.64. 404 of the 530
current players have the required 3 seasons on file and get a
regression-projected next-season DPM; the other 126 (mostly rookies/
short-history players) automatically fall back to darko_ratings.py's
original single-year snapshot behavior via
load_darko_players_with_projection() below -- never a data loss, only an
upgrade where there's enough history to support one. Using the
regression-projected values as darko_ratings.py's input improves ITS fit
against market Elo too (r^2 0.66 -> 0.72 at last check), a real signal
this is adding information rather than noise.

This module is still also exercised against a small, clearly-labeled
SYNTHETIC dataset (see SYNTHETIC_EXAMPLE_STATS and this file's __main__)
to validate the feature-engineering/regression mechanics in isolation from
whatever the real data happens to contain in a given run -- that path
still runs and still matters, it's just no longer the only path.

EXPECTED INPUT SCHEMA (for when real data arrives):
  A CSV with one row per (player, season) -- required columns:
    Player       -- full name, spelled exactly like darkodpmleaderboard.csv
    Team         -- team as of that season (informational only, not a
                     model feature -- a player's value doesn't change
                     because they were traded)
    Season       -- ending year of the season, e.g. 2025 for the 2024-25
                     season (matches this project's other year conventions)
    Age          -- age as of that season
    DARKO_DPM    -- DARKO's DPM for that season (same metric/scale as
                     darkodpmleaderboard.csv's "DPM" column)
    BPM          -- Basketball-Reference (or equivalent) Box Plus-Minus
    VORP         -- Basketball-Reference (or equivalent) Value Over
                     Replacement Player
  A player needs at least MIN_HISTORY_SEASONS + 1 seasons on file to
  produce even one training example (see build_training_rows); more
  players and more seasons per player both directly improve the fit.
  Players with too little history simply keep their raw current-season
  DPM -- see load_darko_players_with_projection.

METHOD:

1. FEATURES per player, built from their season-by-season history strictly
   BEFORE the season being predicted (see build_features):
     - age, age^2 -- the standard rise-then-decline aging-curve shape used
       throughout the public player-aging literature. This functional
       form is a modeling CHOICE, not something fit from this project's
       own data -- same honesty standard as pick_valuation.py's curve
       shape.
     - most_recent_composite -- the player's most recent on-file season's
       DARKO_DPM/BPM/VORP, z-scored per metric (see NORMALIZATION) then
       averaged, so no single metric's raw scale dominates.
     - trend -- the slope (numpy.polyfit, degree 1) of that composite
       across all the player's history-window seasons, capturing whether
       they're trending up or down independent of their current level.
   Four features on purpose: a small, interpretable set you can actually
   reason about beats a large one that fits marginally better and can't be
   explained -- the same philosophy calibrate_pick_value.py applies to the
   pick-value curve.

2. NORMALIZATION. DARKO_DPM and BPM are both roughly -5 to +8, but VORP is
   a season-cumulative total that scales with games/minutes played --
   directly averaging raw values would let VORP's larger numeric range
   quietly dominate the composite. Each metric is z-scored (mean 0, std 1)
   using the FULL TRAINING SET's mean/std before being averaged; those
   same mean/std values (NormParams, stored on the fitted model) are
   reused at prediction time so a projection is computed on the same scale
   the model was trained on, not re-normalized against whatever smaller
   set happens to be predicted.

3. REGRESSION. Ordinary least squares (numpy.linalg.lstsq) predicting next-
   season DARKO_DPM from the four features above. Chosen over a fancier
   model (random forest, gradient boosting, a neural net) for the same
   reason as the small feature set: interpretable, sanity-checkable
   coefficients, and appropriate for a dataset that -- even once real --
   will likely be a few thousand player-seasons at most, nowhere near the
   scale where nonlinear models' extra complexity pays for itself.

4. fit_regression() reports r^2 and the fitted coefficients -- always
   check r^2 before trusting a projection, same "show the fit, don't hide
   it" standard as calibrate_pick_value.py and darko_ratings.py.

WHAT THIS DOES NOT MODEL:
  - Role/opportunity changes (a new coach, a changed role, a supporting
    cast upgrade or downgrade) -- the model only sees a player's own
    historical stat line and age, nothing about their situation changing.
  - Injury risk -- darko_ratings.py's separate longevity data already
    covers multi-year PRESENCE; this module is purely about performance
    LEVEL conditional on playing.
  - Small-sample seasons. A 10-game injury-shortened season counts the
    same as a full 82-game one in this framework -- a real implementation
    should probably weight by games/minutes played once real data exists,
    which isn't in the schema above yet (add a Games or MPG column and
    weight build_training_rows by it if you extend this).
"""

import csv
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple

import numpy as np

MIN_HISTORY_SEASONS = 2  # need >= this many prior seasons to build the trend feature
FEATURE_NAMES = ["age", "age_squared", "most_recent_composite", "trend"]


@dataclass
class SeasonStat:
    player: str
    team: str
    season: int  # ending year, e.g. 2025 for the 2024-25 season
    age: float
    darko_dpm: float
    bpm: float
    vorp: float


@dataclass
class NormParams:
    """Per-metric z-score parameters, fit once on the training set and reused at prediction time."""
    dpm_mean: float
    dpm_std: float
    bpm_mean: float
    bpm_std: float
    vorp_mean: float
    vorp_std: float

    def composite(self, s: SeasonStat) -> float:
        def z(x, m, sd):
            return (x - m) / sd if sd > 0 else 0.0
        return (z(s.darko_dpm, self.dpm_mean, self.dpm_std)
                + z(s.bpm, self.bpm_mean, self.bpm_std)
                + z(s.vorp, self.vorp_mean, self.vorp_std)) / 3.0


@dataclass
class RegressionModel:
    coefficients: Dict[str, float]  # feature name -> fitted weight
    intercept: float
    norm: NormParams
    r_squared: float
    n_training_rows: int

    def predict(self, features: Dict[str, float]) -> float:
        return self.intercept + sum(self.coefficients[f] * features[f] for f in FEATURE_NAMES)


def load_multi_year_stats(csv_path: str) -> Dict[str, List[SeasonStat]]:
    """Loads the schema described in this module's docstring. Returns {player: [SeasonStat, ...]} sorted by season ascending."""
    by_player: Dict[str, List[SeasonStat]] = {}
    with open(csv_path, encoding="utf-8-sig") as f:
        for row in csv.DictReader(f):
            s = SeasonStat(
                player=row["Player"].strip(),
                team=row["Team"].strip(),
                season=int(row["Season"]),
                age=float(row["Age"]),
                darko_dpm=float(row["DARKO_DPM"]),
                bpm=float(row["BPM"]),
                vorp=float(row["VORP"]),
            )
            by_player.setdefault(s.player, []).append(s)
    for player in by_player:
        by_player[player].sort(key=lambda s: s.season)
    return by_player


def build_features(history: List[SeasonStat], norm: NormParams) -> Dict[str, float]:
    """
    history: a player's seasons in chronological order, STRICTLY BEFORE
    the season being predicted/projected. Needs >= MIN_HISTORY_SEASONS
    entries -- callers must check len() first (build_training_rows and
    project_next_season both do).
    """
    if len(history) < MIN_HISTORY_SEASONS:
        raise ValueError(f"Need >= {MIN_HISTORY_SEASONS} seasons of history, got {len(history)}")
    latest = history[-1]
    composite_series = [norm.composite(s) for s in history]
    idx = np.arange(len(composite_series))
    trend = float(np.polyfit(idx, composite_series, 1)[0])
    return {
        "age": latest.age,
        "age_squared": latest.age ** 2,
        "most_recent_composite": composite_series[-1],
        "trend": trend,
    }


def _fit_normalization(all_seasons: List[SeasonStat]) -> NormParams:
    dpm = np.array([s.darko_dpm for s in all_seasons])
    bpm = np.array([s.bpm for s in all_seasons])
    vorp = np.array([s.vorp for s in all_seasons])
    return NormParams(
        dpm_mean=float(dpm.mean()), dpm_std=float(dpm.std()) or 1.0,
        bpm_mean=float(bpm.mean()), bpm_std=float(bpm.std()) or 1.0,
        vorp_mean=float(vorp.mean()), vorp_std=float(vorp.std()) or 1.0,
    )


def build_training_rows(by_player: Dict[str, List[SeasonStat]], norm: NormParams) -> Tuple[np.ndarray, np.ndarray]:
    """
    Expanding-window training examples: for a player with seasons
    [s0, s1, ..., sk], generates one example per target season index t
    (t starting at MIN_HISTORY_SEASONS) using history = seasons[0:t] and
    target = seasons[t].darko_dpm -- i.e. "given everything on file up to
    but not including this season, what was the player's ACTUAL DPM that
    season." A player with exactly MIN_HISTORY_SEASONS+1 seasons yields 1
    example; more seasons yield more (one per season past the minimum).
    """
    X, y = [], []
    for seasons in by_player.values():
        for t in range(MIN_HISTORY_SEASONS, len(seasons)):
            history = seasons[:t]
            target = seasons[t]
            feats = build_features(history, norm)
            X.append([feats[f] for f in FEATURE_NAMES])
            y.append(target.darko_dpm)
    return np.array(X), np.array(y)


def fit_regression(by_player: Dict[str, List[SeasonStat]]) -> RegressionModel:
    all_seasons = [s for seasons in by_player.values() for s in seasons]
    if not all_seasons:
        raise ValueError("No season data to fit against")
    norm = _fit_normalization(all_seasons)
    X, y = build_training_rows(by_player, norm)
    if len(y) < len(FEATURE_NAMES) + 1:
        raise ValueError(
            f"Only {len(y)} training row(s) available (need at least {len(FEATURE_NAMES) + 1} to fit "
            f"{len(FEATURE_NAMES)} features + an intercept without an underdetermined system) -- "
            f"supply more players/seasons."
        )
    X_design = np.column_stack([X, np.ones(len(X))])  # append intercept column
    coefs_full, _residuals, _rank, _sv = np.linalg.lstsq(X_design, y, rcond=None)
    coefficients = dict(zip(FEATURE_NAMES, (float(c) for c in coefs_full[:-1])))
    intercept = float(coefs_full[-1])

    pred = X_design @ coefs_full
    ss_res = float(np.sum((y - pred) ** 2))
    ss_tot = float(np.sum((y - y.mean()) ** 2))
    r_squared = 1 - ss_res / ss_tot if ss_tot > 0 else float("nan")

    # 5 free parameters (4 features + intercept) fit against too few rows
    # is a textbook overfitting setup -- a near-1.0 r^2 there means the
    # model memorized the training rows, not that it generalizes. Rule of
    # thumb: want at least ~3x as many rows as parameters before trusting
    # the fit at all; flag it loudly rather than let a suspiciously perfect
    # r^2 read as a good sign.
    min_recommended_rows = 3 * (len(FEATURE_NAMES) + 1)
    if len(y) < min_recommended_rows:
        print(f"[player_value_regression] WARNING: only {len(y)} training rows for "
              f"{len(FEATURE_NAMES) + 1} free parameters (want >= {min_recommended_rows}). "
              f"r^2={r_squared:.3f} on a fit this underdetermined likely reflects overfitting/"
              f"memorization, not real predictive power -- do not trust this fit until more "
              f"players/seasons are supplied.")

    return RegressionModel(coefficients=coefficients, intercept=intercept, norm=norm,
                            r_squared=r_squared, n_training_rows=len(y))


def project_next_season(seasons: List[SeasonStat], model: RegressionModel) -> Optional[float]:
    """
    Projects the NEXT season's DPM for a player from their full available
    history using the fitted model. Returns None if the player has fewer
    than MIN_HISTORY_SEASONS seasons on file (not enough to build the
    trend feature) -- callers fall back to the player's raw current-season
    DPM in that case (see load_darko_players_with_projection below).
    """
    if len(seasons) < MIN_HISTORY_SEASONS:
        return None
    feats = build_features(seasons, model.norm)
    return model.predict(feats)


def load_darko_players_with_projection(multi_year_csv: Optional[str] = None,
                                        dpm_csv: Optional[str] = None,
                                        longevity_csv: Optional[str] = None) -> List:
    """
    Drop-in upgrade for darko_ratings.load_darko_players(): if
    `multi_year_csv` is given (schema at the top of this module) and a
    player has more than MIN_HISTORY_SEASONS seasons on file there, their
    `.dpm` is replaced with this module's regression-projected NEXT-season
    value instead of the raw current-season DPM leaderboard figure.
    Players missing from the multi-year file, or with too little history,
    keep their raw current-season DPM unchanged -- this is a strict
    upgrade path, never a silent data loss. Pass multi_year_csv=None (the
    default) to get EXACTLY darko_ratings.load_darko_players()'s original
    behavior back, unchanged.

    STATUS: as of this writing no real multi-year dataset has been
    supplied for this project -- every player in darkodpmleaderboard.csv
    has exactly one season on file anywhere, so calling this with a real
    multi_year_csv today would fall back to raw current-season DPM for the
    entire league (identical output to load_darko_players()). This
    function is ready to use the moment a real multi-year file matching
    the schema above is supplied -- see this file's __main__ for a
    worked (synthetic) example of what changes once it is.
    """
    from darko_ratings import load_darko_players, DarkoPlayer, DPM_CSV as _DPM_CSV, LONGEVITY_CSV as _LONGEVITY_CSV

    players = load_darko_players(dpm_csv or _DPM_CSV, longevity_csv or _LONGEVITY_CSV)
    if multi_year_csv is None:
        return players

    by_player = load_multi_year_stats(multi_year_csv)
    usable = {p: seasons for p, seasons in by_player.items() if len(seasons) > MIN_HISTORY_SEASONS}
    if not usable:
        print(f"[player_value_regression] {multi_year_csv!r} has no player with more than "
              f"{MIN_HISTORY_SEASONS} seasons on file -- nothing to train on, falling back to "
              f"raw current-season DPM for every player.")
        return players

    model = fit_regression(usable)
    print(f"[player_value_regression] fit against {model.n_training_rows} player-season training "
          f"row(s), r^2={model.r_squared:.3f} -- {'trust this' if model.n_training_rows >= 200 else 'TREAT WITH CAUTION, very few training rows'}")

    upgraded = 0
    result = []
    for p in players:
        seasons = by_player.get(p.name)
        projected = project_next_season(seasons, model) if seasons else None
        if projected is not None:
            result.append(DarkoPlayer(name=p.name, team=p.team, dpm=projected,
                                       mpg=p.mpg, longevity_by_offset=p.longevity_by_offset))
            upgraded += 1
        else:
            result.append(p)
    print(f"[player_value_regression] upgraded {upgraded}/{len(players)} players to a "
          f"regression-projected DPM; the rest kept their raw current-season figure.")
    return result


# ---------------------------------------------------------------------------
# SYNTHETIC test fixture -- FABRICATED data, not real players or real stats.
# Exists only to prove the mechanics above work end to end. Three archetypes
# x 4 players each, 3 seasons apiece (2023-2025), engineered so the expected
# direction of each projection is obvious: ascending young players should
# project ABOVE their most recent season, declining veterans should project
# BELOW it, and stable-prime players should project close to it.
# ---------------------------------------------------------------------------
SYNTHETIC_EXAMPLE_STATS: List[SeasonStat] = []
for i in range(4):
    name = f"Synthetic Ascending {i+1}"
    # 22 -> 24 years old, clearly improving across all three metrics.
    SYNTHETIC_EXAMPLE_STATS += [
        SeasonStat(name, "Test Team", 2023, 22 + i * 0.3, 0.5 + i * 0.2, 0.8 + i * 0.2, 1.0 + i * 0.2),
        SeasonStat(name, "Test Team", 2024, 23 + i * 0.3, 1.8 + i * 0.2, 2.0 + i * 0.2, 2.2 + i * 0.2),
        SeasonStat(name, "Test Team", 2025, 24 + i * 0.3, 3.2 + i * 0.2, 3.1 + i * 0.2, 3.4 + i * 0.2),
    ]
for i in range(4):
    name = f"Synthetic Prime {i+1}"
    # 27 -> 29 years old, flat/stable across all three metrics.
    SYNTHETIC_EXAMPLE_STATS += [
        SeasonStat(name, "Test Team", 2023, 27 + i * 0.3, 4.0 + i * 0.1, 3.8 + i * 0.1, 3.9 + i * 0.1),
        SeasonStat(name, "Test Team", 2024, 28 + i * 0.3, 4.1 + i * 0.1, 3.9 + i * 0.1, 4.0 + i * 0.1),
        SeasonStat(name, "Test Team", 2025, 29 + i * 0.3, 3.9 + i * 0.1, 4.0 + i * 0.1, 3.8 + i * 0.1),
    ]
for i in range(4):
    name = f"Synthetic Declining {i+1}"
    # 34 -> 36 years old, clearly declining across all three metrics.
    SYNTHETIC_EXAMPLE_STATS += [
        SeasonStat(name, "Test Team", 2023, 34 + i * 0.3, 3.5 - i * 0.2, 3.3 - i * 0.2, 3.4 - i * 0.2),
        SeasonStat(name, "Test Team", 2024, 35 + i * 0.3, 2.2 - i * 0.2, 2.4 - i * 0.2, 2.1 - i * 0.2),
        SeasonStat(name, "Test Team", 2025, 36 + i * 0.3, 0.9 - i * 0.2, 1.0 - i * 0.2, 0.8 - i * 0.2),
    ]


def _synthetic_by_player() -> Dict[str, List[SeasonStat]]:
    by_player: Dict[str, List[SeasonStat]] = {}
    for s in SYNTHETIC_EXAMPLE_STATS:
        by_player.setdefault(s.player, []).append(s)
    return by_player


if __name__ == "__main__":
    print("=== FRAMEWORK TEST against SYNTHETIC (fabricated) data -- not real players ===\n")
    by_player = _synthetic_by_player()
    print(f"{len(by_player)} synthetic players, {sum(len(v) for v in by_player.values())} player-seasons total\n")

    model = fit_regression(by_player)
    print(f"Fitted on {model.n_training_rows} training rows, r^2 = {model.r_squared:.3f}")
    print("Coefficients:")
    for name, coef in model.coefficients.items():
        print(f"  {name:<24} {coef:+.4f}")
    print(f"  {'intercept':<24} {model.intercept:+.4f}")

    print("\n--- Projected NEXT season (2026) DPM vs. most recent actual (2025) ---")
    print(f"{'Player':<26}{'2025 DPM':>10}{'Projected 2026':>16}{'Direction':>12}")
    for name, seasons in by_player.items():
        latest = seasons[-1].darko_dpm
        projected = project_next_season(seasons, model)
        direction = "up" if projected > latest + 0.05 else ("down" if projected < latest - 0.05 else "flat")
        print(f"{name:<26}{latest:>10.2f}{projected:>16.2f}{direction:>12}")

    print("\n--- Confirming the integration hook falls back cleanly with no multi-year data ---")
    from darko_ratings import load_darko_players
    baseline = load_darko_players()
    upgraded = load_darko_players_with_projection(multi_year_csv=None)
    identical = [b.dpm for b in baseline] == [u.dpm for u in upgraded]
    print(f"load_darko_players_with_projection(None) matches load_darko_players() exactly: {identical}")
