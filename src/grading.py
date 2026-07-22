"""
Grading layer -- turns pick_valuation.py's numbers into an actual letter
grade, for the two distinct questions worth keeping separate:

  1. TRADE GRADE (grade_trade): did a team give up appropriate value for
     what it received, in expectation? Compares total value in vs. total
     value out, using full pick-probability distributions where available
     (not just "the pick turned out to be #7 so here's its value").

  2. SELECTION GRADE (grade_selection): given the slot a team actually
     picked at, did they take the best player available relative to a
     ranked board of alternatives? This is a *relative-to-the-field*
     question, not a value-curve question -- it needs your own prospect
     rankings as an input, not pick_valuation.py.

ASSUMPTION -- the letter-grade thresholds:
The mapping from "value_received - value_given" (in pick_valuation's
0-100-per-pick-1 units) to a letter grade is an ARBITRARY scale set below
in TRADE_GRADE_THRESHOLDS. There's no ground truth for "how many value-curve
units equal a B+"; this should ideally be calibrated against a history of
real trades and how they were received/graded by the market, not treated as
authoritative out of the box. The same caveat applies to
SELECTION_GRADE_PERCENTILES for grade_selection().
"""

from dataclasses import dataclass
from typing import Dict, List, Sequence

from pick_valuation import expected_value_of_distribution, pick_value

# --- Trade grading -----------------------------------------------------

# value_diff = value_received - value_given, in pick_valuation's 0-100 units.
# ARBITRARY thresholds -- see module docstring. Calibrate against real
# trade history before treating these as meaningful in an absolute sense;
# they're most useful for relative comparison between trades you grade with
# this same scale.
TRADE_GRADE_THRESHOLDS = [
    (25, "A+"), (15, "A"), (8, "A-"),
    (3, "B+"), (0, "B"), (-3, "B-"),
    (-8, "C+"), (-15, "C"), (-25, "C-"),
    (-40, "D"),
]
TRADE_GRADE_FLOOR = "F"


@dataclass
class TradeAsset:
    """
    One asset in a trade. Either:
      - a known, already-resolved pick (set `pick_number`), or
      - an unresolved future pick (set `pick_probabilities`, a
        {pick_number: probability} dict -- e.g. straight from
        pick_valuation.distribution_from_counts()), or
      - a player or other asset with a manually-assigned value on the same
        0-100 scale as pick_value() (set `manual_value`) -- this module
        doesn't project player trade value itself; that's a separate,
        much harder problem (you'd need surplus value over the player's
        remaining contract, not just their DARKO).
    """
    label: str
    pick_number: int = None
    pick_probabilities: Dict[int, float] = None
    manual_value: float = None

    def value(self) -> float:
        if self.manual_value is not None:
            return self.manual_value
        if self.pick_probabilities is not None:
            return expected_value_of_distribution(self.pick_probabilities)
        if self.pick_number is not None:
            return pick_value(self.pick_number)
        raise ValueError(f"Asset {self.label!r} has no value source set")


def _letter_for_value_diff(value_diff: float) -> str:
    for threshold, letter in TRADE_GRADE_THRESHOLDS:
        if value_diff >= threshold:
            return letter
    return TRADE_GRADE_FLOOR


def grade_trade(assets_received: Sequence[TradeAsset],
                 assets_given: Sequence[TradeAsset]) -> Dict[str, object]:
    """
    Returns a dict with total value in/out, the net diff, and a letter
    grade. Grades from the perspective of whoever "received"
    `assets_received` in exchange for `assets_given`.
    """
    value_received = sum(a.value() for a in assets_received)
    value_given = sum(a.value() for a in assets_given)
    diff = value_received - value_given
    return {
        "value_received": value_received,
        "value_given": value_given,
        "value_diff": diff,
        "grade": _letter_for_value_diff(diff),
    }


# --- Selection grading ---------------------------------------------------

# Percentile-of-the-board thresholds -- ARBITRARY, see module docstring.
# "Percentile" here = how the selected player ranks among players still on
# the board at the time of the pick (1.0 = top-ranked player taken, 0.0 =
# bottom of the available board taken).
SELECTION_GRADE_PERCENTILES = [
    (0.95, "A+"), (0.85, "A"), (0.70, "A-"),
    (0.55, "B+"), (0.40, "B"), (0.25, "B-"),
    (0.15, "C+"), (0.08, "C"), (0.03, "C-"),
]
SELECTION_GRADE_FLOOR = "D"


def grade_selection(selected_player: str, board_at_time_of_pick: Sequence[str]) -> Dict[str, object]:
    """
    board_at_time_of_pick: prospect names in rank order, BEST first,
    representing your own big board of everyone still available at that
    slot (already-drafted players removed). This does NOT come from
    pick_valuation.py -- it requires an actual prospect ranking model,
    which is a separate project (translated stats, athletic testing,
    age-adjusted production, etc.) not built here.

    Returns the player's rank, percentile among the field, and a letter
    grade for the pick relative to what was available.
    """
    if selected_player not in board_at_time_of_pick:
        raise ValueError(f"{selected_player!r} not found in the provided board")

    n = len(board_at_time_of_pick)
    rank = board_at_time_of_pick.index(selected_player) + 1  # 1 = best available
    percentile = 1.0 - (rank - 1) / n  # rank 1 of n -> percentile 1.0

    grade = SELECTION_GRADE_FLOOR
    for threshold, letter in SELECTION_GRADE_PERCENTILES:
        if percentile >= threshold:
            grade = letter
            break

    return {
        "selected_player": selected_player,
        "rank_among_available": rank,
        "board_size": n,
        "percentile": percentile,
        "grade": grade,
    }


if __name__ == "__main__":
    # --- Trade grade example ---
    # Team A trades an established veteran (manually valued) for Team B's
    # unresolved, lottery-protected 2027 first.
    received = [TradeAsset("Team B's 2027 first (lottery-range)",
                            pick_probabilities={3: 0.15, 7: 0.25, 12: 0.30, 16: 0.30})]
    given = [TradeAsset("Established starter, 1 year left", manual_value=35.0)]
    result = grade_trade(received, given)
    print("Trade grade example:")
    print(f"  Value received: {result['value_received']:.1f}")
    print(f"  Value given:    {result['value_given']:.1f}")
    print(f"  Net diff:       {result['value_diff']:+.1f}")
    print(f"  Grade:          {result['grade']}")

    # --- Selection grade example ---
    board = ["Prospect A", "Prospect B", "Prospect C", "Prospect D", "Prospect E",
             "Prospect F", "Prospect G", "Prospect H", "Prospect I", "Prospect J"]
    pick_result = grade_selection("Prospect C", board)
    print("\nSelection grade example (10-player board, took 3rd-ranked prospect):")
    print(f"  Rank among available: {pick_result['rank_among_available']} / {pick_result['board_size']}")
    print(f"  Percentile: {pick_result['percentile']:.2f}")
    print(f"  Grade: {pick_result['grade']}")
