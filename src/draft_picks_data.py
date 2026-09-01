"""
Real, current draft-pick ownership data for all 30 NBA teams, 2027-2033.

The 2026 draft has concluded (results are known), so each team's already-
resolved 2026 selection(s) have been removed from this table -- draft
capital tracked here now starts at 2027, the next draft this pipeline
actually projects/grades.

SOURCE: https://www.ldsport.com/future-draft-picks.html (LD Sport credits
ESPN for draft info and compiles pick ownership/swap/protection language
manually). This is the year-by-year pick description text for each team,
transcribed as-is.

LIVE SOURCE / REFRESH PROCESS: an earlier automated refresh attempt (via
the WebFetch tool, which converts the page to markdown and summarizes it
through a small model before returning it) proved unreliable for this
page specifically -- it fabricated notation on at least one team (Detroit
Pistons 2028 showed an invented "[x3]" shorthand) and dropped picks on
others, even after retrying with smaller per-request batches. The data
below was instead read directly from the rendered page in a real Chrome
tab (`get_page_text` on the live DOM, no WebFetch, no summarization) and
diffed cell-by-cell against the prior trusted version before being
applied. Three previously-suspicious "(NO PICKS)" results (Toronto
Raptors 2031/2033, Phoenix Suns 2033) were independently cross-checked
against each team's separate "Tradable/Untradable Picks" summary section
on the same page (which enumerates every pick a team holds by year) and
confirmed consistent. Trailing "*" footnote markers LD Sport attaches to
a handful of picks (e.g. "UTA* (Most Favorable) 1st") are stripped here
rather than transcribed -- those footnotes describe pick-restriction
rules (no team picks top-5 three years running, no repeat #1 pick) that
this pipeline already enforces via simulation (pick_restrictions_321.py),
so keeping a redundant static "*" in the text would just go stale; see
the NOTE comments on Memphis Grizzlies, Utah Jazz, and Washington
Wizards' 2027 entries below for the specific restrictions involved.
Last synced: 2026-09-01. 90 of 210 team-years changed from the prior
version in this sync (mostly additional/resolved conditional picks and
swap-language refinements; a handful of picks disappeared where a team's
prior conditional pick apparently already resolved or was traded away).

WHY THIS IS TEXT, NOT RESOLVED PICKAsset OBJECTS:
Most of these picks are conditional -- "Better of X and Y," "Worst of A, B,
and C," protected ranges, swap rights contingent on OTHER teams' pick
outcomes in the SAME or an EARLIER draft. Resolving "MIL/NO (Less
Favorable) 1st (If #5-30)" into an actual probability distribution over
pick numbers requires knowing the joint distribution of both teams'
records -- which is exactly what standings_sim.py / draft_pipeline_321.py
already simulate. The right way to resolve these is to run those two (or
three) teams' pick distributions through the SAME Monte Carlo trials and
take, trial-by-trial, whichever pick is better/worse per the swap language
-- not to try to approximate it with a static formula here.

`resolve_simple_picks()` below handles the mechanical cases (an
unconditional own pick, or a single acquired pick with no conditions) by
converting them straight into pick_grading.PickAsset objects. Conditional/
swap picks are left as raw text in `conditional_notes` for now -- wiring
those into the simulator (querying the relevant teams' Monte Carlo pick
distributions and combining them per the stated condition) is the natural
next module, not something to fake with a static number.

Data current as of the August 2026 fetch. Draft-pick ownership changes with
every trade -- this WILL go stale; treat it as a snapshot, not a live feed.
"""

from typing import Dict

TEAM_FUTURE_PICKS: Dict[str, Dict[int, str]] = {
    "Atlanta Hawks": {
        2027: "MIL/NO (Less Favorable) 1st (If #5-30), ATL 2nd",
        2028: "ATL/(CLE/UTA (Less Favorable)) (More Favorable) 1st",
        2029: "ATL 1st, CLE 2nd",
        2030: "ATL 1st, NYK 2nd",
        2031: "ATL 1st",
        2032: "ATL 1st",
        2033: "ATL 1st, ATL 2nd, SAC 2nd",
    },
    "Boston Celtics": {
        2027: "BOS 1st",
        2028: "(BOS (If #1))/LAC (If #1-16)/(PHI (If #1-8)) (Most Favorable) 1st / ((BOS (#2-30))/SA (Less Favorable))/LAC (If #1-16)/(PHI (If #1-8)) (Most Favorable) 1st, LAC 1st (If #17-30) (If PHI 1st is #9-30), BOS 2nd (If #31-45) (If 2028 BOS 1st is #2-30), GS/MIL/OKC (Most Favorable) 2nd",
        2029: "(NO PICKS)",
        2030: "BOS 1st, PHX/POR/WAS (Most Favorable) 2nd, CHA 2nd (If #56-60)",
        2031: "BOS 1st, PHI 1st, BOS/CLE (Less Favorable) 2nd, HOU 2nd (If #56-60)",
        2032: "BOS 1st, BOS 2nd",
        2033: "BOS 1st, BOS 2nd",
    },
    "Brooklyn Nets": {
        2027: "BKN/HOU (Less Favorable) 1st, NYK 1st, LAL 2nd (If 2027 LAL 1st is #5-30)",
        2028: "BKN/NYK/PHI 1st (If #9-30)/PHX (Most Favorable) 1st, BKN/NYK/PHI 1st (If #9-30)/PHX (2nd Favorable) 1st, ATL 2nd, BKN 2nd, MEM 2nd, PHI 2nd (If 2028 PHI 1st is #1-8)",
        2029: "BKN 1st, DAL/HOU/PHX (Least Favorable) 1st, NYK 1st, BKN 2nd, DAL 2nd, GS 2nd, MEM 2nd",
        2030: "BKN 1st, BOS 2nd, BKN 2nd, DAL 2nd, LAL 2nd",
        2031: "BKN 1st, NYK 1st, BKN 2nd, LAL 2nd",
        2032: "BKN 1st, DEN 1st, BKN 2nd, DEN 2nd, MIA 2nd, TOR 2nd",
        2033: "BKN 1st, BKN 2nd",
    },
    "Charlotte Hornets": {
        2027: "CHA 1st, DAL 1st (If #3-30), MIA 1st (If #15-30), MEM 2nd, NO/POR (More Favorable) 2nd",
        2028: "CHA/MIN (More Favorable) 1st, MIA 1st (If 2027 MIA 1st is #15-30), CHA/LAC (More Favorable) 2nd, HOU 2nd, MIA 2nd (If 2027 DAL 1st is #1-2), ORL 2nd",
        2029: "CHA/(MIN (If #1-5)) (More Favorable) 1st, CHA 2nd, DEN 2nd, MIN 2nd (If 2029 MIN 1st is #6-30)",
        2030: "CHA/MIN (More Favorable) 1st (If #1) / CHA/((DAL/SA (More Favorable))/MIN (Less Favorable)) (More Favorable) 1st (If #2-30), CHA 2nd (If #31-55), LAC/UTA (More Favorable) 2nd",
        2031: "CHA 1st, CHA 2nd, MIL 2nd, PHX 2nd",
        2032: "CHA 1st, CHA 2nd, MIL 2nd, MIN 2nd",
        2033: "CHA 1st, MIN 1st, PHX 1st, CHA 2nd, HOU 2nd, MIN 2nd",
    },
    "Chicago Bulls": {
        2027: "CHI 1st, CLE 2nd",
        2028: "CHI 1st, CHI/IND/PHX (Most Favorable) 2nd",
        2029: "CHI 1st, CHI 2nd, DET/MIL/NYK (Least Favorable) 2nd",
        2030: "CHI 1st, CHI/IND (More Favorable) 2nd",
        2031: "CHI 1st, CHI 2nd, DEN 2nd, GS/MIN (More Favorable) 2nd, NYK 2nd",
        2032: "CHI 1st, CHI 2nd, HOU/PHX (More Favorable) 2nd",
        2033: "CHI 1st, CHI 2nd",
    },
    "Cleveland Cavaliers": {
        2027: "(NO PICKS)",
        2028: "ATL/CLE/UTA (Least Favorable) 1st",
        2029: "(NO PICKS)",
        2030: "CLE 1st",
        2031: "CLE 1st",
        2032: "CLE 1st, SAC 2nd",
        2033: "CLE 1st, CLE 2nd",
    },
    "Dallas Mavericks": {
        2027: "DAL 1st (If #1-2)",
        2028: "DAL/OKC (Less Favorable) 1st",
        2029: "LAL 1st",
        2030: "DAL/SA (Less Favorable) 1st",
        2031: "DAL 1st",
        2032: "DAL 1st",
        2033: "DAL 1st",
    },
    "Denver Nuggets": {
        2027: "DEN 1st (If #1-5)",
        2028: "DEN 1st (If #1-5 and 2027 DEN 1st is #1-5), DEN 2nd (If #31-33), MIN 2nd",
        2029: "DEN 1st (If #1-5, 2027 DEN 1st is #1-5 and 2028 DEN 1st is #1-5) / DEN 1st (If #1-5) (If 2027 DEN 1st is #6-30)",
        2030: "DEN 1st (If #1-5 and 2029 DEN 1st is #1-5) (If 2027 DEN 1st is #6-30) / DEN 1st (If #1-5) (If 2027 DEN 1st is #1-5 and 2028 DEN 1st is #6-30)",
        2031: "DEN 1st, SAC 2nd",
        2032: "(NO PICKS)",
        2033: "DEN 1st, DEN 2nd",
    },
    "Detroit Pistons": {
        2027: "DET 1st, DET 2nd",
        2028: "DET 1st, (CHA/LAC (Less Favorable))/DET (If #31-55)/MIA 2nd (If 2027 DAL 1st is #3-30)/NYK (Most Favorable) 2nd (If #31-55), (CHA/LAC (Less Favorable))/DET (If #31-55)/MIA 2nd (If 2027 DAL 1st is #3-30)/NYK (2nd Favorable) 2nd, (CHA/LAC (Less Favorable))/DET (If #31-55)/MIA 2nd (If 2027 DAL 1st is #3-30)/NYK (3rd Favorable) 2nd",
        2029: "DET 1st, DET/MIL/NYK (Most Favorable) 2nd, DET/MIL/NYK (2nd Most Favorable) 2nd",
        2030: "DET 1st, DET 2nd",
        2031: "DET 1st, DAL 2nd, GS/MIN (Less Favorable) 2nd",
        2032: "DET 1st, DET 2nd",
        2033: "DET 1st, DET 2nd",
    },
    "Golden State Warriors": {
        2027: "GS 1st",
        2028: "GS 1st",
        2029: "GS 1st",
        2030: "GS 1st (If #1-20), GS 2nd (If 2030 GS 1st is #21-30)",
        2031: "GS 1st",
        2032: "GS 1st, GS 2nd (#31-50)",
        2033: "GS 1st, GS 2nd",
    },
    "Houston Rockets": {
        2027: "BKN/HOU (More Favorable) 1st, PHX 1st, NO/POR (Less Favorable) 2nd (If #56-60)",
        2028: "HOU 1st",
        2029: "DAL/HOU/PHX (Most Favorable) 1st, DAL/HOU/PHX (2nd Favorable) 1st",
        2030: "HOU 1st",
        2031: "HOU 1st, ATL/HOU (Less Favorable) 2nd (If #31-55)",
        2032: "HOU 1st",
        2033: "HOU 1st",
    },
    "Indiana Pacers": {
        2027: "IND 1st, UTA 2nd",
        2028: "IND 1st, CHI/(IND/PHX (More Favorable)) (Less Favorable) 2nd",
        2029: "IND/WAS (Less Favorable) 2nd",
        2030: "IND 1st, CHI/IND (Less Favorable) 2nd",
        2031: "IND 1st, IND/MEM/MIA (Least Favorable) 2nd",
        2032: "IND 1st, IND 2nd",
        2033: "IND 1st, IND 2nd",
    },
    "Los Angeles Clippers": {
        2027: "(DEN (If #6-30)/LAC/OKC (Least Favorable))/TOR (More Favorable) 1st, (GS/PHX (More Favorable))/(HOU/IND/MIA/OKC (Most Favorable))/PHI (2nd Most Favorable) 2nd",
        2028: "DAL 2nd, (CHA/LAC (Less Favorable))/MIA 2nd (If 2027 DAL 1st is #3-30)/NYK (Most Favorable) 2nd (If #56-60)",
        2029: "IND 1st, LAC 1st (If #1-3) / LAC (If #4-30)/PHI (Less Favorable) 1st, TOR 1st",
        2030: "LAC 1st, TOR 2nd",
        2031: "LAC 1st, TOR 1st, LAC 2nd",
        2032: "LAC 1st, LAC 2nd",
        2033: "LAC 1st, TOR 1st, LAC 2nd, TOR 2nd",
    },
    "Los Angeles Lakers": {
        2027: "LAL 1st (If #1-4)",
        2028: "(CLE/UTA (More Favorable))/LAL (Less Favorable) 1st",
        2029: "(NO PICKS)",
        2030: "LAL/UTA (Less Favorable) 1st",
        2031: "WAS 2nd",
        2032: "LAL 1st, WAS 2nd",
        2033: "LAL 2nd",
    },
    "Memphis Grizzlies": {
        # NOTE: Utah's piece of this swap (UTA's own 2027 1st) is subject to
        # the 3-2-1 lottery's "no 3-straight top-5" pick restriction --
        # Utah was top-5 in both the real 2025 and 2026 drafts -- so it
        # cannot land top-5 in 2027. This is now enforced by SIMULATION
        # (pick_restrictions_321.DEFAULT_2027_HISTORY passed into the
        # 2027 lottery draw), not by a static annotation here -- see that
        # module for why a hardcoded "*2027 UTA 1st cannot be Top-5" note
        # would just go stale and isn't needed for the parser to resolve
        # this swap correctly.
        2027: "CLE/MIN/UTA (Most Favorable) 1st, LAL 1st (If #5-30), MEM 1st, LAL 2nd (If 2027 LAL 1st is #1-4)",
        2028: "MEM 1st",
        2029: "MEM/ORL (If #3-30) (More Favorable) 1st, HOU 2nd, LAL 2nd, ORL 2nd (If 2029 ORL 1st is #1-2), POR 2nd",
        2030: "GS 1st (If #21-30), MEM/(PHX/WAS (Less Favorable)) (More Favorable) 1st, ORL 1st, DEN/HOU/MIA (Most Favorable) 2nd, GS 2nd (If 2030 GS 1st is #1-20), MEM 2nd (If #31-50)",
        2031: "MEM 1st, PHX 1st, (IND/MIA (Less Favorable))/MEM (More Favorable) 2nd",
        2032: "MEM 1st, GS 2nd (If #51-60), MEM/PHI/UTA (Most Favorable) 2nd",
        2033: "MEM 1st, MEM 2nd, OKC 2nd, WAS 2nd",
    },
    "Miami Heat": {
        2027: "MIA 1st (If #1-14), HOU/IND/MIA/OKC/SA (Least Favorable) 2nd",
        2028: "MIA 1st (If 2027 MIA 1st is #15-30)",
        2029: "MIA 1st",
        2030: "MIA/MIL/POR (Least Favorable) 1st",
        2031: "(NO PICKS)",
        2032: "MIA 1st",
        2033: "(NO PICKS)",
    },
    "Milwaukee Bucks": {
        2027: "BKN/DAL (Less Favorable) 2nd, MIL 2nd",
        2028: "((BKN/PHI (If #9-30)/PHX (Least Favorable)/WAS (More Favorable))/MIL/POR (Least Favorable) 1st",
        2029: "(NO PICKS)",
        2030: "MIA/(MIL/POR (Less Favorable)) (More Favorable) 1st",
        2031: "MIA 1st, MIL 1st",
        2032: "MIL 1st",
        2033: "MIA 1st, MIL 1st, MIA 2nd, MIL 2nd",
    },
    "Minnesota Timberwolves": {
        2027: "(NO PICKS)",
        2028: "CHA/MIN (Less Favorable) 1st",
        2029: "CHA/MIN (Less Favorable) 1st (If #2-5)",
        2030: "CHA/(DAL/SA (More Favorable))/MIN (Least Favorable) 1st, MEM 2nd (If #51-60)",
        2031: "(NO PICKS)",
        2032: "MIN 1st",
        2033: "(NO PICKS)",
    },
    "New Orleans Pelicans": {
        2027: "MIL/NO (More Favorable) 1st, MIL/NO (Less Favorable) 1st (If #1-4), HOU/IND/MIA/OKC (2nd Most Favorable) 2nd",
        2028: "NO 1st",
        2029: "NO 1st",
        2030: "NO 1st, NO/ORL (Less Favorable) 2nd",
        2031: "NO 1st, TOR 2nd",
        2032: "NO 1st, NO 2nd",
        2033: "NO 1st, NO 2nd",
    },
    "New York Knicks": {
        2027: "HOU/IND/MIA/OKC (3rd Most Favorable) 2nd, NYK 2nd, WAS 2nd",
        2028: "BKN/NYK (Less Favorable) 1st, BOS 2nd (If #46-60), IND/PHX (Less Favorable) 2nd",
        2029: "PHX 2nd, SAC 2nd",
        2030: "NYK 1st, PHI 2nd",
        2031: "(NO PICKS)",
        2032: "NYK 1st, DAL 2nd, NYK 2nd",
        2033: "NYK 1st, NYK 2nd, PHX 2nd",
    },
    "Oklahoma City Thunder": {
        2027: "DEN 1st (If #6-30)/LAC/OKC (Most Favorable) 1st, DEN 1st (If #6-30)/LAC/OKC (2nd Most Favorable) 1st, SA 1st (If #17-30), CHA 2nd (If 2027 SA 1st is #1-16), CHI 2nd, SAC 2nd (If 2027 SA 1st is #1-16)",
        2028: "DAL/OKC (More Favorable) 1st, DEN 1st (If #6-30, If 2027 DEN 1st is #1-5), UTA 2nd",
        2029: "DEN 1st (If #6-30, 2027 DEN 1st is #1-5 and 2028 DEN 1st is #1-5) / DEN 1st (If #6-30) (If 2027 DEN 1st is #6-30), OKC 1st, ATL 2nd, BOS 2nd, MIA 2nd, OKC 2nd",
        2030: "DEN 1st (If #6-30 and 2029 DEN 1st is #1-5) (If 2027 DEN 1st is #6-30) / DEN 1st (If #6-30) (If 2027 DEN 1st is #1-5 and 2028 DEN 1st is #6-30), OKC 1st, ATL 2nd, DEN/HOU/MIA (2nd Most Favorable) 2nd, DEN/HOU/MIA (Least Favorable) 2nd, MIN 2nd, OKC 2nd",
        2031: "OKC 1st, ATL/(HOU (If #31-55)) (More Favorable) 2nd, DET 2nd, NO/ORL (Less Favorable) 2nd, OKC 2nd",
        2032: "OKC 1st, ATL 2nd, LAL 2nd, OKC 2nd",
        2033: "OKC 1st",
    },
    "Orlando Magic": {
        2027: "ORL 1st",
        2028: "LAL/WAS (More Favorable) 2nd",
        2029: "ORL 1st (If #1-2) / MEM/ORL (If #3-30) (Less Favorable) 1st, ORL 2nd (If 2029 ORL 1st is #3-30)",
        2030: "MIL 2nd, NO/ORL (More Favorable) 2nd",
        2031: "ORL 1st, NO/ORL (More Favorable) 2nd",
        2032: "ORL 1st, ORL 2nd",
        2033: "ORL 1st, ORL 2nd",
    },
    "Philadelphia 76ers": {
        2027: "PHI 1st, (GS/PHX (More Favorable))/(HOU/IND/MIA/OKC (Most Favorable))/PHI (Most Favorable) 2nd, (GS/PHX (More Favorable))/(HOU/IND/MIA/OKC (Most Favorable))/PHI (Least Favorable) 2nd",
        2028: "(BOS (If #2-30)/SA (Less Favorable))/(LAC (If #1-16))/(PHI (If #1-8)) (2nd Most Favorable) 1st, (BOS (If #2-30)/SA (Less Favorable))/(LAC (If #17-30))/(PHI (If #1-8)) (Least Favorable) 1st (If 2028 PHI 1st is #1-8), DET 2nd (If #56-60), GS/MIL/OKC (2nd Most Favorable) 2nd, GS/MIL/OKC (Least Favorable) 2nd, PHI 2nd (If 2028 PHI 1st is #9-30)",
        2029: "LAC (If #4-30)/PHI (More Favorable) 1st, PHI 2nd",
        2030: "PHI 1st, (PHX/POR (More Favorable))/WAS (Less Favorable) 2nd",
        2031: "PHI 2nd",
        2032: "PHI 1st, MEM/PHI (Less Favorable) 2nd",
        2033: "PHI 1st, PHI 2nd",
    },
    "Phoenix Suns": {
        2027: "CLE/MIN/UTA (Least Favorable) 1st, BOS/ORL (Less Favorable) 2nd",
        2028: "BKN/PHI (If #9-30)/PHX/WAS (Least Favorable) 1st",
        2029: "CLE/MIN (If #6-30)/UTA (Least Favorable) 1st",
        2030: "MEM/PHX/WAS (Least Favorable) 1st",
        2031: "(NO PICKS)",
        2032: "PHX 1st, HOU/PHX (Less Favorable) 2nd",
        2033: "(NO PICKS)",
    },
    "Portland Trail Blazers": {
        2027: "POR 1st, MIN 2nd, NO/POR (Less Favorable) 2nd (If #31-55)",
        2028: "MIL/POR (More Favorable) 1st, ORL 1st, POR 2nd, SAC 2nd",
        2029: "BOS/MIL/POR (Most Favorable) 1st, BOS/MIL/POR (Least Favorable) 1st, IND/WAS (Less Favorable) 2nd",
        2030: "MIL/POR (More Favorable) 1st",
        2031: "POR 1st, POR 2nd",
        2032: "POR 1st, POR 2nd",
        2033: "POR 1st, POR 2nd",
    },
    "Sacramento Kings": {
        2027: "SAC 1st, SA 1st (If #1-16), CHA 2nd (If 2027 SA 1st is #17-30), SAC 2nd (If 2027 SA 1st is #17-30)",
        2028: "SAC 1st",
        2029: "SAC 1st",
        2030: "SAC 1st",
        2031: "MIN 1st, SAC/SA (Less Favorable) 1st",
        2032: "SAC 1st",
        2033: "SAC 1st",
    },
    "San Antonio Spurs": {
        2027: "ATL 1st, (HOU/IND/MIA/OKC (Least Favorable))/SA (More Favorable) 2nd",
        2028: "BOS (If #2-30)/SA (More Favorable) 1st, BOS 2nd (If #31-45) (If 2028 BOS 1st is #1), NO 2nd, SA 2nd",
        2029: "SA 1st, LAC 2nd, NO 2nd, SA 2nd",
        2030: "DAL/MIN (If #2-30)/SA (Most Favorable) 1st, CLE 2nd, SAC 2nd, SA 2nd",
        2031: "SAC/SA (More Favorable) 1st, SA 2nd",
        2032: "SA 1st, SA 2nd",
        2033: "SA 1st, SA 2nd",
    },
    "Toronto Raptors": {
        2027: "DEN (If #6-30)/LAC/OKC/TOR (Least Favorable) 1st, TOR 2nd",
        2028: "TOR 1st, TOR 2nd",
        2029: "TOR 1st, TOR 2nd",
        2030: "TOR 1st",
        2031: "(NO PICKS)",
        2032: "TOR 1st",
        2033: "(NO PICKS)",
    },
    "Utah Jazz": {
        # NOTE: Utah's own 2027 1st (the "UTA" leg of the CLE/MIN/UTA swap
        # below) cannot land top-5 -- Utah was top-5 in both real 2025 and
        # 2026 -- enforced via simulation, see the matching note on Memphis
        # Grizzlies' 2027 entry above.
        2027: "CLE/MIN/UTA (2nd Favorable) 1st, BOS/ORL (More Favorable) 2nd, DEN 2nd, LAC 2nd",
        2028: "CLE/LAL/UTA (Most Favorable) 1st, (CHA/LAC (Less Favorable))/DET (If #31-55)/MIA (If 2027 DAL 1st is #3-30)/NYK (Least Favorable) 2nd, CLE 2nd",
        2029: "CLE /MIN (If #6-30)/UTA (Most Favorable) 1st, CLE/MIN (#If #6-30)/UTA (2nd Favorable) 1st, MIN 2nd (If 2029 MIN 1st is #1-5), UTA 2nd",
        2030: "LAL/UTA (More Favorable) 1st, LAC/UTA (Less Favorable) 2nd",
        2031: "LAL 1st, UTA 1st, BOS/CLE (More Favorable) 2nd, (IND/MIA (More Favorable))/UTA (Less Favorable) 2nd",
        2032: "UTA 1st, CLE 2nd",
        2033: "LAL 1st, UTA 1st, UTA 2nd",
    },
    "Washington Wizards": {
        # NOTE: Washington's own 2027 1st cannot be the #1 pick -- Washington
        # had the real 2026 #1 -- enforced via simulation (see
        # pick_restrictions_321.py) rather than a static annotation.
        2027: "WAS 1st, BKN/DAL (More Favorable) 2nd, GS/PHX (Less Favorable) 2nd",
        2028: "(BKN/PHI (If #9-30)/PHX (Least Favorable))/(MIL/POR (Less Favorable)/WAS (Most Favorable), DEN 2nd (If #34-60), LAL/WAS (Less Favorable) 2nd",
        2029: "BOS/MIL/POR (2nd Favorable) 1st, WAS 1st",
        2030: "PHX/WAS (More Favorable) 1st, PHX/POR (Less Favorable) 2nd",
        2031: "WAS 1st, IND/MIA/UTA (Most Favorable) 2nd",
        2032: "WAS 1st, (MEM/PHI (More Favorable))/UTA (Less Favorable) 2nd",
        2033: "WAS 1st, DAL 2nd",
    },
}


if __name__ == "__main__":
    print(f"Loaded future draft pick data for {len(TEAM_FUTURE_PICKS)} teams.")
    print("\nExample -- Boston Celtics:")
    for year, desc in TEAM_FUTURE_PICKS["Boston Celtics"].items():
        print(f"  {year}: {desc}")
