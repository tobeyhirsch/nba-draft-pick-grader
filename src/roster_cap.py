"""
Roster & cap-sheet layer.

This is deliberately the "softest" module in the pipeline. Unlike the
lottery mechanics (which are exact rules) or the Elo conversion (a
documented but fixed approximation), what a front office actually DOES with
its cap sheet -- who they re-sign, whether they use the full mid-level
exception, whether they dip below the second apron -- is a judgment call,
not something to fake precision on. This module gives you the plumbing
(accurate current thresholds, rookie-scale cost estimates, apron status)
and stops short of pretending to predict actual transactions.

CURRENT THRESHOLDS -- 2026-27 season (confirmed via league announcement,
July 2026):
    Salary cap:        $164,961,000
    Salary floor:      $148,465,000
    Luxury tax line:   $200,428,000
    First apron:       $209,015,000
    Second apron:      $221,686,000
These are set once a year and WILL be stale by the time you read this in a
future season -- re-check before using for anything beyond a demo. The
league projected roughly 5.5% cap growth for 2027-28 as of mid-2026
(unofficial, subject to change), which is what CAP_GROWTH_ASSUMPTION below
uses to project forward.

ROOKIE SCALE -- IMPORTANT CAVEAT:
The NBA's actual rookie scale is a published table (exact first-year salary
per pick, 1-30, as a set dollar figure that scales with the cap). This
module does NOT reproduce that official table verbatim, because doing so
from memory risks getting individual pick values wrong. Instead,
`estimate_rookie_scale_salary()` uses a documented parametric APPROXIMATION
(smooth exponential decay from pick 1 to pick 30, anchored to a rough
pick-1 value as a fraction of the cap). Treat these numbers as
directionally correct (pick 1 costs much more than pick 30, decay is
steepest at the top of the lottery) but NOT contract-accurate. For real cap
planning, replace this function with the league's actual rookie scale
table (published each year, e.g. via Basketball Reference or Spotrac).
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional

# --- 2026-27 season thresholds (see module docstring for source/caveats) ---
SALARY_CAP_2026_27 = 164_961_000
SALARY_FLOOR_2026_27 = 148_465_000
LUXURY_TAX_2026_27 = 200_428_000
FIRST_APRON_2026_27 = 209_015_000
SECOND_APRON_2026_27 = 221_686_000

CAP_GROWTH_ASSUMPTION = 0.055  # ~5.5% per year, per league's mid-2026 informal projection


def project_cap(base_year_cap: float, years_forward: int,
                 growth_rate: float = CAP_GROWTH_ASSUMPTION) -> float:
    """Naive compounding projection -- real cap growth depends on league revenue and is not smooth."""
    return base_year_cap * ((1 + growth_rate) ** years_forward)


@dataclass
class Contract:
    player_name: str
    team: str
    salary_by_year: Dict[int, float]         # {season_start_year: salary}
    guaranteed_by_year: Dict[int, bool] = field(default_factory=dict)  # default: assume guaranteed
    player_option_years: List[int] = field(default_factory=list)
    team_option_years: List[int] = field(default_factory=list)

    def salary(self, year: int) -> float:
        return self.salary_by_year.get(year, 0.0)

    def is_guaranteed(self, year: int) -> bool:
        return self.guaranteed_by_year.get(year, True)


@dataclass
class CapSheet:
    team: str
    contracts: List[Contract]

    def total_salary(self, year: int, guaranteed_only: bool = True) -> float:
        total = 0.0
        for c in self.contracts:
            if guaranteed_only and not c.is_guaranteed(year):
                continue
            total += c.salary(year)
        return total

    def cap_space(self, year: int, cap: float = SALARY_CAP_2026_27) -> float:
        """Positive = room under the cap. Negative = already over (soft cap, not necessarily illegal)."""
        return cap - self.total_salary(year)

    def apron_status(self, year: int,
                      first_apron: float = FIRST_APRON_2026_27,
                      second_apron: float = SECOND_APRON_2026_27,
                      tax_line: float = LUXURY_TAX_2026_27) -> str:
        total = self.total_salary(year, guaranteed_only=False)  # apron uses a broader salary definition in reality; simplified here
        if total > second_apron:
            return "second_apron"
        if total > first_apron:
            return "first_apron"
        if total > tax_line:
            return "luxury_tax"
        return "under_tax"

    def expiring_contracts(self, year: int) -> List[Contract]:
        """Contracts with no salary on the books for `year` but salary in year-1."""
        return [c for c in self.contracts if c.salary(year) == 0 and c.salary(year - 1) > 0]


# --- Rookie scale approximation (see module docstring caveat) ---
ROOKIE_SCALE_PICK1_FRACTION_OF_CAP = 0.13  # pick 1 ~ 13% of the cap, roughly matching recent scale deals
ROOKIE_SCALE_DECAY = 0.11                   # decay rate per pick number, tuned so pick 30 << pick 1


def estimate_rookie_scale_salary(pick_number: int, cap: float = SALARY_CAP_2026_27) -> float:
    """
    APPROXIMATION -- see module docstring. Returns an estimated first-year
    rookie-scale salary for a given pick number (1-30, or up to 60 for
    second-rounders, though the real scale doesn't cover picks 31-60 at all
    -- second-round deals are individually negotiated, often at/near
    minimum salary. This function still returns a smoothly decaying number
    for convenience, but treat anything past pick 30 as illustrative only.
    """
    if pick_number < 1:
        raise ValueError("pick_number must be >= 1")
    pick1_value = cap * ROOKIE_SCALE_PICK1_FRACTION_OF_CAP
    return pick1_value * (1 - ROOKIE_SCALE_DECAY) ** (pick_number - 1)


def project_incoming_rookie_cost(pick_probabilities: Dict[int, float],
                                  cap: float = SALARY_CAP_2026_27) -> float:
    """
    Expected rookie-scale cap hold for a team, given a probability
    distribution over which pick they'll end up with (e.g. straight from
    monte_carlo_pick_distribution or monte_carlo_321_pick_distribution,
    normalized to probabilities). Useful for connecting the lottery-sim
    output back into cap planning: "what should we budget for our likely
    incoming rookie?"
    """
    return sum(prob * estimate_rookie_scale_salary(pick, cap=cap)
               for pick, prob in pick_probabilities.items())


if __name__ == "__main__":
    # Sanity checks
    print("Rookie scale approximation (illustrative, not the official table):")
    for pick in [1, 5, 10, 14, 20, 30]:
        print(f"  Pick {pick:>2}: ${estimate_rookie_scale_salary(pick):,.0f}")

    sample = CapSheet(
        team="Sample Team",
        contracts=[
            Contract("Star Player", "Sample Team", {2026: 45_000_000, 2027: 48_000_000}),
            Contract("Starter", "Sample Team", {2026: 22_000_000, 2027: 24_000_000}),
            Contract("Expiring Vet", "Sample Team", {2026: 15_000_000}),  # no 2027 salary -> expiring
            Contract("Role Player", "Sample Team", {2026: 8_000_000, 2027: 8_500_000}),
        ],
    )
    print(f"\n{sample.team} 2026 total salary: ${sample.total_salary(2026):,.0f}")
    print(f"Cap space vs. {SALARY_CAP_2026_27:,.0f} cap: ${sample.cap_space(2026):,.0f}")
    print(f"Apron status: {sample.apron_status(2026)}")
    print(f"Expiring after 2026: {[c.player_name for c in sample.expiring_contracts(2027)]}")

    example_dist = {1: 0.14, 2: 0.13, 3: 0.12, 4: 0.11, 5: 0.10, 6: 0.09,
                     7: 0.08, 8: 0.07, 9: 0.06, 10: 0.05, 11: 0.03, 12: 0.02}
    print(f"\nExpected rookie cap hold given this pick distribution: "
          f"${project_incoming_rookie_cost(example_dist):,.0f}")
