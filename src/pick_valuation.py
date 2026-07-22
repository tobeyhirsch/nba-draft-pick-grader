"""
Pick valuation layer: converts a draft slot (or a probability distribution
over slots, straight from lottery_sim / lottery_sim_321) into an expected
surplus-value number.

ASSUMPTION -- the value curve itself:
There is no universal, agreed-upon "true" draft value curve. Public trade
value charts (Kevin Pelton's, Bryan Frankel's SVA-based chart, various
front-office internal versions) broadly agree on shape (steep drop-off in
the top 5, flattening through the rest of the lottery, a long shallow tail
through the second round) but differ on exact numbers, and none of them are
reproduced here verbatim. `pick_value()` instead uses a documented
PARAMETRIC APPROXIMATION -- an exponential-decay curve fit to roughly match
that commonly observed shape, normalized to 100 at pick 1. This is meant to
be replaced with a real regression once you have historical data (e.g.
rookie-scale-cost-adjusted win shares or VORP by draft slot, regressed
against pick number) -- the function signature is the contract the rest of
the pipeline depends on, not the specific numbers inside it.

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

# Calibration: pick 1 = 100 (arbitrary units), decay rate chosen so the
# curve roughly matches the commonly cited shape of public trade value
# charts (steep through the lottery, flattens after ~pick 10-14).
PICK1_VALUE = 100.0
DECAY_RATE = 0.095   # tuned so pick 30 lands around 6-7, pick 60 near 1
VALUE_FLOOR = 0.5    # no pick (even a throw-in second-rounder) is worth literally zero


def pick_value(pick_number: int) -> float:
    """
    Approximate surplus value of a single, known draft slot.
    Values are on an arbitrary 0-100 scale (pick 1 = 100), meant for
    RELATIVE comparison between picks/trades, not as a dollar or WAR figure.
    """
    if pick_number < 1:
        raise ValueError("pick_number must be >= 1")
    raw = PICK1_VALUE * ((1 - DECAY_RATE) ** (pick_number - 1))
    return max(raw, VALUE_FLOOR)


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
