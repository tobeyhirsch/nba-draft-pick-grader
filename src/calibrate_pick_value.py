"""
Derives pick_valuation.py's value curve from real career-outcome data
instead of an assumed smooth exponential decay.

SOURCE: NBA_Draft_Picks_20152025.xlsx (user-supplied), "Draft Picks
2015-2025" sheet -- every first-round pick (1-30) from the 2015-2025
drafts, each tagged with a subjective "Career Outcome Tier" (Superstar /
Star-All-Star / Above-average starter / Contributor-role player / Bust),
judged from All-Star/All-NBA selections and career Win Shares/BPM/VORP
through 2025-26. 2024 and 2025 picks are tagged "Too early to tell" and
excluded here (not enough career sample) -- leaves 271 scored picks across
the 2015-2023 draft classes (9 years x 30 picks, minus a few incomplete
entries).

METHOD:

1. ASSUMPTION -- map each ordinal tier to a cardinal "surplus value" point
   score. The spreadsheet's tiers are ORDINAL (Superstar > Star > ... >
   Bust) but not cardinal -- it doesn't say a Superstar is worth exactly
   how many Busts. TIER_VALUE below is a judgment call, not derived from
   the data: it's deliberately steep (Superstar >> the rest) because real
   surplus-value analyses of rookie-scale contracts consistently find
   superstar production is worth an order of magnitude more than a solid
   role player's, not a linear step apart. Bust is set near the project's
   existing VALUE_FLOOR (0.5) since the Legend defines it as "replacement
   level or out of the league" -- i.e. genuinely near-zero trade value.
   Change these five numbers and every downstream pick value moves with
   them; that's the one real lever in this whole calibration.

2. Fit a monotonic decay curve -- value(pick) = c + a / pick^b -- by
   nonlinear least squares against all 271 individual (pick, tier_value)
   observations (not just the 6 bucket means the spreadsheet's own "Stat
   Analysis"/"Charts" tabs report -- those buckets are only 44-46 picks
   each and visibly noisy, e.g. the 11-15 bucket's mean is HIGHER than the
   6-10 bucket's purely because Devin Booker/Donovan Mitchell/SGA/
   Haliburton/Bam Adebayo all happened to land picks 11-14 in this
   particular 9-year sample -- fitting against all 271 points lets that
   kind of small-sample luck average out instead of distorting the curve).
   This functional form (fast initial drop, then a long flattening tail)
   is the standard shape for real draft trade-value charts (Pelton's, SVA,
   etc.) and matches what the data actually shows: Picks 1-5 average value
   is roughly triple Picks 6-30's, which is themselves fairly flat/noisy
   (no clear further decline pick-by-pick from 6 through 30).

3. Round 2 (picks 31-60) has ZERO data in this spreadsheet -- it only
   covers first-round picks. Extending the fitted round-1 curve as-is
   would almost certainly overvalue second-round picks: they get
   non-guaranteed contracts and roster-spot competition a drafted
   first-rounder doesn't face, historically converting to rotation
   NBA players far less often. SECOND_ROUND_DISCOUNT below applies a flat
   documented haircut to the round-1 curve's continuation for pick > 30 --
   an assumption, not a fit, same honesty standard as step 1. This also
   produces a real discontinuity right at the round boundary (pick 30 vs.
   31), which is directionally correct: the rookie-scale guarantee cutoff
   between the rounds is a real cliff in draft value, not a smooth curve.

Run this file directly to see the fit diagnostics (bucket-level actual vs.
model comparison) and the resulting pick_value() table -- the numbers
printed here are exactly what's hardcoded into pick_valuation.py, with
this script as the reproducible source of truth for where they came from.
"""

import os

import numpy as np
from scipy.optimize import curve_fit

from data_paths import find_data_file

# Checks several common data/ locations relative to THIS file -- see data_paths.py.
XLSX_PATH = find_data_file("NBA_Draft_Picks_20152025.xlsx", os.path.dirname(os.path.abspath(__file__)))
SHEET_NAME = "Draft Picks 2015-2025"

# --- Step 1: tier -> surplus-value point assumption (see docstring) ---
TIER_VALUE = {
    "🟩 Superstar": 100.0,
    "🟦 Star / All-Star": 38.0,
    "🟨 Above-average starter": 14.0,
    "⬛ Contributor / role player": 4.0,
    "🟥 Bust": 0.5,
}

SECOND_ROUND_DISCOUNT = 0.4  # flat haircut applied to the fitted curve past pick 30 (see docstring step 3)
VALUE_FLOOR = 0.5


def load_scored_picks(xlsx_path: str = XLSX_PATH):
    import openpyxl
    wb = openpyxl.load_workbook(xlsx_path, data_only=True)
    ws = wb[SHEET_NAME]
    rows = list(ws.iter_rows(min_row=3, values_only=True))  # skip the two header rows
    return [(row[1], TIER_VALUE[row[5]]) for row in rows if row[5] in TIER_VALUE]


def fit_curve(scored_picks):
    picks = np.array([p for p, v in scored_picks], dtype=float)
    values = np.array([v for p, v in scored_picks], dtype=float)

    def model(pick, a, b, c):
        return c + a / np.power(pick, b)

    popt, _ = curve_fit(model, picks, values, p0=[100, 1, 5],
                         bounds=([0, 0.01, 0], [1000, 5, 50]), maxfev=20000)
    return tuple(popt)  # (a, b, c)


def raw_curve_value(pick_number: int, a: float, b: float, c: float) -> float:
    return c + a / (pick_number ** b)


if __name__ == "__main__":
    scored = load_scored_picks()
    print(f"Loaded {len(scored)} scored first-round picks (2015-2023 classes)")

    a, b, c = fit_curve(scored)
    print(f"\nFitted value(pick) = {c:.3f} + {a:.3f} / pick^{b:.4f}")

    scale = 100.0 / raw_curve_value(1, a, b, c)
    print(f"Normalization: multiply raw curve by {scale:.4f} so pick 1 = 100.0 exactly")

    print("\n--- Fit diagnostic: actual bucket mean value vs. model's average over that bucket ---")
    picks_arr = np.array([p for p, v in scored])
    values_arr = np.array([v for p, v in scored])
    for lo, hi in [(1, 5), (6, 10), (11, 15), (16, 20), (21, 25), (26, 30)]:
        actual = values_arr[(picks_arr >= lo) & (picks_arr <= hi)].mean()
        model_avg = np.mean([raw_curve_value(p, a, b, c) for p in range(lo, hi + 1)])
        print(f"  Picks {lo:>2}-{hi:<2}: actual={actual:6.2f}   model={model_avg:6.2f}")

    print("\n--- Resulting pick_value() table (matches pick_valuation.py exactly) ---")
    for p in [1, 2, 3, 4, 5, 6, 8, 10, 14, 20, 25, 30, 31, 35, 40, 45, 50, 55, 60]:
        raw = raw_curve_value(p, a, b, c)
        if p > 30:
            raw *= SECOND_ROUND_DISCOUNT
        val = max(scale * raw, VALUE_FLOOR)
        print(f"  Pick {p:>2}: {val:6.2f}")
