"""
Pick valuation layer: converts a draft slot (or a probability distribution
over slots, straight from lottery_sim / lottery_sim_321) into an expected
surplus-value number.

VALUE CURVE -- now calibrated from real career-outcome data, not assumed:
An earlier version of this module used a hand-tuned exponential-decay
curve (no real data behind it, just matching the commonly-cited SHAPE of
public trade value charts). `pick_value()` now instead comes from
calibrate_pick_value.py, which fits a curve against 271 real first-round
picks from the 2015-2023 draft classes (NBA_Draft_Picks_20152025.xlsx,
user-supplied), each tagged with a subjective career-outcome tier
(Superstar / Star-All-Star / Above-average starter / Contributor / Bust)
based on All-Star selections and career Win Shares/BPM/VORP. See that
script's docstring for the full method (tier->value-point assumption,
curve fit, second-round discount) -- the short version:

  - value(pick) = 3.218 + 53.284 / pick^0.7779, for picks 1-30, rescaled so
    pick 1 = 100.0. This form (fast initial drop, long flattening tail)
    matches what the data actually shows: Picks 1-5 average roughly TRIPLE
    the value of Picks 6-30, which are themselves fairly flat -- there's no
    strong further decline pick-by-pick once you're past the top 5. That's
    a materially different (and more front-loaded) shape than the old
    smooth exponential assumed.
  - Picks 31-60 (second round) have NO data in the source spreadsheet --
    it only covers first-round picks. The round-1 curve is extended past
    pick 30 with a flat, documented 0.4x haircut (SECOND_ROUND_DISCOUNT)
    reflecting non-guaranteed contracts and much lower NBA-rotation
    conversion rates for second-rounders historically -- this produces a
    real discontinuity right at the round boundary (pick 30 vs. 31), which
    is directionally correct (the guaranteed-contract cliff between rounds
    is a real, sudden drop in value, not a smooth curve through it).

Like the exponential curve before it, this remains a documented
APPROXIMATION, not a claim of precision: the tier->value-point mapping
(TIER_VALUE) is a judgment call (the spreadsheet's tiers are ordinal, not
cardinal), and the whole fit is against 9 draft classes' worth of outcomes,
which is a real but limited sample (n=271, and top-heavy small-N buckets
are visibly noisy -- see calibrate_pick_value.py's fit diagnostics). Re-run
that script if you get a larger/updated dataset.

Two related but different things you can compute with this module:
  1. pick_value(pick_number) -- value of a SPECIFIC, known slot.
  2. expected_value_of_distribution(pick_probs) -- value of a pick whose
     final slot is still uncertain (e.g. a team's projected 2027 first,
     before the lottery has actually happened). This is the version that
     should be used for grading trades made *before* the lottery runs --
     using the most-likely single slot instead systematically misprices
     uncertain/lottery-range picks. Because pick_value() is convex (steep
     decay, then flattens), Jensen's inequality means a pick with a WIDE
     range of possible outcomes is worth MORE than naively evaluating the
     curve at its average expected slot would suggest -- e.g. a coin flip
     between pick 3 and pick 14 is worth more than the curve's value at
     slot ~8-9, because the upside (pick 3) is worth disproportionately
     more than the downside (pick 14) costs. Always compute expected value
     over the full distribution, not the average slot number.
"""

from typing import Dict

# Fitted from calibrate_pick_value.py -- see that script and this module's
# docstring for the full derivation (271 real 2015-2023 first-round career
# outcomes -> tier value points -> nonlinear curve fit).
_CURVE_A = 53.284
_CURVE_B = 0.7779
_CURVE_C = 3.218
_PICK1_RAW = _CURVE_C + _CURVE_A / (1 ** _CURVE_B)
_SCALE = 100.0 / _PICK1_RAW  # normalizes pick 1 to exactly 100.0

SECOND_ROUND_DISCOUNT = 0.4  # flat haircut past pick 30 -- no real data covers round 2, see docstring
VALUE_FLOOR = 0.5            # no pick (even a throw-in second-rounder) is worth literally zero

# Kept for any external code still referencing the old constant name.
PICK1_VALUE = 100.0


def pick_value(pick_number: int) -> float:
    """
    Data-calibrated surplus value of a single, known draft slot (see module
    docstring for the fit). Values are on an arbitrary 0-100 scale (pick 1
    = 100), meant for RELATIVE comparison between picks/trades, not as a
    dollar or WAR figure.
    """
    if pick_number < 1:
        raise ValueError("pick_number must be >= 1")
    raw = _CURVE_C + _CURVE_A / (pick_number ** _CURVE_B)
    if pick_number > 30:
        raw *= SECOND_ROUND_DISCOUNT
    return max(_SCALE * raw, VALUE_FLOOR)


def expected_value_of_distribution(pick_probabilities: Dict[int, float]) -> float:
    """
    pick_probabilities: {pick_number: probability}, should sum to ~1.0
    (e.g. normalize monte_carlo_pick_distribution's counts by trial count
    before passing in).

    Returns the probability-weighted expected value -- correctly accounts
    for the convexity of pick_value() rather than evaluating the curve at
    a single "expected pick number."
    """
    total_prob = sum(pick_probabilities.values())
    if total_prob <= 0:
        raise ValueError("pick_probabilities must have positive total probability")
    return sum(prob * pick_value(pick) for pick, prob in pick_probabilities.items()) / total_prob


def distribution_from_counts(counts: Dict[int, int], trials: int) -> Dict[int, float]:
    """Convenience: turn monte_carlo_pick_distribution's raw counts into probabilities."""
    return {pick: count / trials for pick, count in counts.items()}


if __name__ == "__main__":
    print("Illustrative pick-value curve (0-100 scale, pick 1 = 100):")
    for pick in [1, 2, 3, 5, 8, 10, 14, 20, 30, 45, 60]:
        print(f"  Pick {pick:>2}: {pick_value(pick):5.1f}")

    # Demonstrates Jensen's inequality: a coin-flip between pick 3 and pick
    # 14 is worth MORE than the value at the "average slot" (~8-9), because
    # the curve is convex -- the upside of pick 3 outweighs the downside of
    # pick 14 disproportionately.
    coin_flip = {3: 0.5, 14: 0.5}
    naive_avg_pick_value = pick_value(round(3 * 0.5 + 14 * 0.5))
    correct_expected_value = expected_value_of_distribution(coin_flip)
    print(f"\n50/50 shot at pick 3 or pick 14:")
    print(f"  Value at the 'average slot' (~8-9), WRONG approach: {naive_avg_pick_value:.1f}")
    print(f"  Correct probability-weighted expected value:        {correct_expected_value:.1f}")
    print(f"  (Correct value is HIGHER -- convexity means uncertainty helps here.)")
