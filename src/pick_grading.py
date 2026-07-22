"""
Grades a SINGLE draft pick asset on a 1-10 scale. This is a different
question from grading.py's grade_trade() (which compares two sides of a
trade) -- this module answers "how good is this one pick, by itself?"

SCALE DEFINITION -- read this before trusting a number:
The 1-10 grade is the pick's PERCENTILE RANK against all 60 draft slots
(picks 1-60), rescaled to 1-10. Concretely: a grade of 7.5 means this pick
is worth more than ~72% of all possible picks in a draft. This is anchored
to something concrete (percentile of the pick_valuation.py curve) rather
than picking round-number cutoffs out of thin air -- but it inherits every
assumption baked into pick_valuation.pick_value() itself (see that module's
docstring). If you replace the value curve with a real regression, this
scale automatically re-calibrates with it.

THREE ADDITIONAL ASSUMPTIONS specific to this module:

1. PROTECTION HANDLING. A protected pick (e.g. "top-4 protected") does not
   convey to the receiving team in the years it lands in the protected
   range -- in those scenarios, the receiving team gets nothing (or
   whatever fallback asset the protection converts to, e.g. a future
   second-rounder). This module treats protected-range outcomes as
   contributing `fallback_value` (default 0.0) rather than the pick's
   face value, and does NOT renormalize the remaining probability -- the
   protection genuinely destroys value in those scenarios, it doesn't
   redistribute it.

2. TIME DISCOUNTING. A future pick is discounted by
   `(1 - annual_discount_rate) ** years_away`. This exists because a 2029
   pick carries more uncertainty (team situation, draft class strength,
   CBA changes) than an identical 2027 pick, independent of projected team
   quality -- NOT because of any real financial time-value-of-money
   argument. `DEFAULT_ANNUAL_DISCOUNT` below is a judgment call, not a
   fitted number.

3. UNCERTAIN PICKS USE FULL-DISTRIBUTION EXPECTED VALUE, not the
   most-likely single slot -- same convexity reasoning as
   pick_valuation.py: a pick that could land anywhere from #3 to #16 needs
   its whole distribution evaluated, not just its average slot.
"""

import bisect
from dataclasses import dataclass
from typing import Dict, Optional, Tuple

from pick_valuation import pick_value, expected_value_of_distribution

DEFAULT_ANNUAL_DISCOUNT = 0.07  # see assumption 2 above -- adjust freely
REFERENCE_PICK_RANGE = range(1, 61)  # picks 1-60, i.e. both rounds

_REFERENCE_VALUES_SORTED = sorted(pick_value(p) for p in REFERENCE_PICK_RANGE)

GRADE_LABELS = [
    (9.0, "Elite"), (7.5, "Great"), (6.0, "Good"), (5.0, "Above average"),
    (4.0, "Average"), (2.5, "Below average"), (1.5, "Weak"),
]
GRADE_LABEL_FLOOR = "Fringe / throw-in"


def percentile_of_value(value: float) -> float:
    """Fraction of all 60 draft slots worth <= this value. 1.0 = best possible, ~0 = worst."""
    idx = bisect.bisect_right(_REFERENCE_VALUES_SORTED, value)
    return idx / len(_REFERENCE_VALUES_SORTED)


def value_to_grade(value: float) -> float:
    """Value (0-100 pick_valuation scale) -> 1-10 grade via percentile rank."""
    return round(1.0 + 9.0 * percentile_of_value(value), 1)


def label_for_grade(grade: float) -> str:
    for threshold, label in GRADE_LABELS:
        if grade >= threshold:
            return label
    return GRADE_LABEL_FLOOR


@dataclass
class PickAsset:
    """
    Describes one pick a team owns (their own, or acquired via trade).

    Exactly one of `pick_number` or `pick_probabilities` should be set:
      - pick_number: use when the pick has already happened / the exact
        slot is known.
      - pick_probabilities: {pick_number: probability} for an unresolved
        future pick -- e.g. straight from
        pick_valuation.distribution_from_counts(monte_carlo_..._counts, trials).

    protection_range: (low, high) inclusive pick numbers in which this pick
        does NOT convey to its owner (e.g. (1, 4) for "top-4 protected").
        Leave as None for an unprotected pick.
    fallback_value: what the pick is worth in protected-range scenarios
        (default 0.0 -- i.e. it's simply lost that year). If the protection
        converts to something specific (e.g. "becomes an unprotected 2nd if
        it doesn't convey"), pass that asset's pick_value() here instead.
    years_away: 0 for this year's pick, 1 for next year's, etc. -- drives
        the time discount.
    """
    label: str
    pick_number: Optional[int] = None
    pick_probabilities: Optional[Dict[int, float]] = None
    protection_range: Optional[Tuple[int, int]] = None
    fallback_value: float = 0.0
    years_away: int = 0

    def _raw_value(self) -> float:
        if self.pick_number is not None:
            if self.protection_range and self.protection_range[0] <= self.pick_number <= self.protection_range[1]:
                return self.fallback_value
            return pick_value(self.pick_number)

        if self.pick_probabilities is not None:
            total_prob = sum(self.pick_probabilities.values())
            if total_prob <= 0:
                raise ValueError(f"{self.label!r}: pick_probabilities must sum to > 0")
            if not self.protection_range:
                return expected_value_of_distribution(self.pick_probabilities)

            lo, hi = self.protection_range
            ev = 0.0
            for pick, prob in self.pick_probabilities.items():
                p = prob / total_prob
                if lo <= pick <= hi:
                    ev += p * self.fallback_value
                else:
                    ev += p * pick_value(pick)
            return ev

        raise ValueError(f"{self.label!r} needs either pick_number or pick_probabilities set")

    def discounted_value(self, annual_discount_rate: float = DEFAULT_ANNUAL_DISCOUNT) -> float:
        return self._raw_value() * ((1 - annual_discount_rate) ** self.years_away)

    def grade(self, annual_discount_rate: float = DEFAULT_ANNUAL_DISCOUNT) -> Dict[str, object]:
        raw = self._raw_value()
        discounted = self.discounted_value(annual_discount_rate)
        grade_score = value_to_grade(discounted)
        return {
            "label": self.label,
            "raw_value": round(raw, 1),
            "discounted_value": round(discounted, 1),
            "years_away": self.years_away,
            "grade": grade_score,
            "grade_label": label_for_grade(grade_score),
        }


def grade_pick_portfolio(assets: list) -> list:
    """Grades each pick in a list SEPARATELY (not aggregated) -- returns one dict per asset."""
    return [a.grade() for a in assets]


if __name__ == "__main__":
    examples = [
        PickAsset("This year's own pick, #3 overall", pick_number=3),
        PickAsset("This year's own pick, #27 overall", pick_number=27),
        PickAsset("Late 2nd-rounder, #58 overall", pick_number=58),
        PickAsset(
            "2027 lottery-range pick (uncertain, unprotected)",
            pick_probabilities={2: 0.10, 5: 0.15, 8: 0.20, 12: 0.25, 16: 0.20, 20: 0.10},
            years_away=1,
        ),
        PickAsset(
            "2028 top-4-protected first from a good team",
            pick_probabilities={4: 0.05, 8: 0.10, 14: 0.25, 20: 0.30, 25: 0.30},
            protection_range=(1, 4),
            years_away=2,
        ),
        PickAsset(
            "2029 unprotected first, contender-owned (likely late)",
            pick_probabilities={22: 0.20, 25: 0.30, 28: 0.30, 30: 0.20},
            years_away=3,
        ),
    ]

    print(f"{'Pick':<48}{'Raw':>7}{'Disc.':>8}{'Grade':>8}  Label")
    for asset in examples:
        g = asset.grade()
        print(f"{g['label']:<48}{g['raw_value']:>7.1f}{g['discounted_value']:>8.1f}"
              f"{g['grade']:>8.1f}  {g['grade_label']}")
