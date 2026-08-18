# NBA Draft Pick Grades -- Full League Run

2027-draft ratings calibrated from consensus market win totals (DraftKings/FanDuel/Hard Rock/Caesars 2026-27 O/U lines); the 2028-2032 drafts use DARKO DPM + career longevity data instead, calibrated against those same market ratings (darko_ratings.py); 2033 falls back to the flat 2026-27 market ratings. Picks graded 1-10 via the swap-resolved pipeline. 2000 simulation trials per team per draft year.

## League summary: average pick grade by team

| Team | Avg grade | Picks graded | Unresolved |
|---|---|---|---|
| Golden State Warriors | 7.19 | 8 | 2 |
| Miami Heat | 6.97 | 4 | 2 |
| Memphis Grizzlies | 6.12 | 13 | 6 |
| Sacramento Kings | 6.12 | 11 | 2 |
| Milwaukee Bucks | 5.64 | 7 | 2 |
| New Orleans Pelicans | 5.19 | 13 | 0 |
| Houston Rockets | 5.13 | 15 | 0 |
| Atlanta Hawks | 4.83 | 11 | 2 |
| Cleveland Cavaliers | 4.75 | 6 | 0 |
| Portland Trail Blazers | 4.74 | 17 | 0 |
| Los Angeles Lakers | 4.49 | 7 | 0 |
| Indiana Pacers | 4.45 | 13 | 0 |
| Los Angeles Clippers | 4.44 | 9 | 2 |
| Dallas Mavericks | 4.41 | 13 | 1 |
| Phoenix Suns | 4.40 | 7 | 1 |
| Toronto Raptors | 4.20 | 12 | 0 |
| Washington Wizards | 4.17 | 18 | 1 |
| Utah Jazz | 4.13 | 15 | 5 |
| Chicago Bulls | 3.92 | 19 | 0 |
| Orlando Magic | 3.91 | 10 | 2 |
| Charlotte Hornets | 3.68 | 23 | 3 |
| Boston Celtics | 3.65 | 10 | 2 |
| Brooklyn Nets | 3.39 | 29 | 4 |
| Minnesota Timberwolves | 3.19 | 7 | 2 |
| Philadelphia 76ers | 3.12 | 20 | 2 |
| Detroit Pistons | 2.90 | 20 | 3 |
| New York Knicks | 2.80 | 11 | 0 |
| Denver Nuggets | 2.80 | 5 | 3 |
| San Antonio Spurs | 2.66 | 18 | 4 |
| Oklahoma City Thunder | 2.65 | 22 | 7 |

## Atlanta Hawks

| Pick | Grade | Label |
|---|---|---|
| 2029 ATL 1st | 8.5 | Great |
| 2030 ATL 1st | 8.3 | Great |
| 2031 ATL 1st | 8.2 | Great |
| 2027 MIL/NO 1st (least favorable, swap-resolved) | 8.2 | Great |
| 2032 ATL 1st | 7.9 | Great |
| 2033 ATL 1st | 6.6 | Good |
| 2027 ATL 2nd | 1.4 | Fringe / throw-in |
| 2029 CLE 2nd | 1.0 | Fringe / throw-in |
| 2030 NYK 2nd | 1.0 | Fringe / throw-in |
| 2033 ATL 2nd | 1.0 | Fringe / throw-in |
| 2032 ATL/LAL 2nd (most favorable, swap-resolved) | 1.0 | Fringe / throw-in |

**Unresolved (2):**
- 2028: ATL/(CLE/UTA (Less Favorable)) (More Favorable) 1st -- *nested parens or a continuation fragment -- needs manual resolution*
- 2031: ATL/HOU (If #31-55) (More Favorable) 2nd -- *nested parens or a continuation fragment -- needs manual resolution*

## Boston Celtics

| Pick | Grade | Label |
|---|---|---|
| 2030 BOS 1st | 6.9 | Good |
| 2031 BOS 1st | 6.7 | Good |
| 2027 BOS 1st | 6.2 | Good |
| 2032 BOS 1st | 6.2 | Good |
| 2033 BOS 1st | 5.5 | Above average |
| 2030 CHA 2nd (protected, doesn't convey #31-55) | 1.0 | Fringe / throw-in |
| 2031 HOU 2nd (protected, doesn't convey #31-55) | 1.0 | Fringe / throw-in |
| 2032 BOS 2nd | 1.0 | Fringe / throw-in |
| 2033 BOS 2nd | 1.0 | Fringe / throw-in |
| 2031 BOS/CLE 2nd (least favorable, swap-resolved) | 1.0 | Fringe / throw-in |

**Unresolved (2):**
- 2028: BOS 1st (If #1) / BOS (If #2-30)/SA (Less Favorable) 1st -- *nested parens or a continuation fragment -- needs manual resolution*
- 2028: BOS 2nd (If #31-45) (If 2028 BOS 1st is #2-30) -- *depends on a different pick's outcome (needs multi-year simulation)*

## Brooklyn Nets

| Pick | Grade | Label |
|---|---|---|
| 2029 BKN 1st | 8.9 | Great |
| 2030 BKN 1st | 8.8 | Great |
| 2031 BKN 1st | 8.6 | Great |
| 2032 BKN 1st | 8.5 | Great |
| 2033 BKN 1st | 8.3 | Great |
| 2027 BKN/HOU 1st (least favorable, swap-resolved) | 6.6 | Good |
| 2027 NYK 1st | 6.0 | Good |
| 2029 NYK 1st | 5.5 | Above average |
| 2031 NYK 1st | 5.5 | Above average |
| 2032 DEN 1st | 5.5 | Above average |
| 2029 DAL/HOU/PHX 1st (least favorable, swap-resolved) | 5.5 | Above average |
| 2028 BKN 2nd | 2.6 | Below average |
| 2028 MEM 2nd | 1.9 | Weak |
| 2028 ATL 2nd | 1.0 | Fringe / throw-in |
| 2029 BKN 2nd | 1.0 | Fringe / throw-in |
| 2029 DAL 2nd | 1.0 | Fringe / throw-in |
| 2029 GS 2nd | 1.0 | Fringe / throw-in |
| 2029 MEM 2nd | 1.0 | Fringe / throw-in |
| 2030 BOS 2nd | 1.0 | Fringe / throw-in |
| 2030 BKN 2nd | 1.0 | Fringe / throw-in |
| 2030 DAL 2nd | 1.0 | Fringe / throw-in |
| 2030 LAL 2nd | 1.0 | Fringe / throw-in |
| 2031 BKN 2nd | 1.0 | Fringe / throw-in |
| 2031 LAL 2nd | 1.0 | Fringe / throw-in |
| 2032 BKN 2nd | 1.0 | Fringe / throw-in |
| 2032 DEN 2nd | 1.0 | Fringe / throw-in |
| 2032 MIA 2nd | 1.0 | Fringe / throw-in |
| 2032 TOR 2nd | 1.0 | Fringe / throw-in |
| 2033 BKN 2nd | 1.0 | Fringe / throw-in |

**Unresolved (4):**
- 2027: LAL 2nd (If 2027 LAL 1st is #5-30) -- *depends on a different pick's outcome (needs multi-year simulation)*
- 2028: BKN/NYK/PHI 1st (If #9-30)/PHX (Most Favorable) 1st -- *nested parens or a continuation fragment -- needs manual resolution*
- 2028: BKN/NYK/PHI 1st (If #9-30)/PHX (2nd Favorable) 1st -- *nested parens or a continuation fragment -- needs manual resolution*
- 2028: PHI 2nd (If 2028 PHI 1st is #1-8) -- *depends on a different pick's outcome (needs multi-year simulation)*

## Charlotte Hornets

| Pick | Grade | Label |
|---|---|---|
| 2027 CHA 1st | 9.1 | Elite |
| 2027 DAL 1st (protected, doesn't convey #1-2) | 8.3 | Great |
| 2028 CHA 1st | 8.1 | Great |
| 2033 CHA 1st | 8.1 | Great |
| 2029 CHA 1st | 7.9 | Great |
| 2030 CHA 1st | 7.6 | Great |
| 2031 CHA 1st | 7.0 | Good |
| 2032 CHA 1st | 6.4 | Good |
| 2027 MIA 1st (protected, doesn't convey #1-14) | 5.5 | Above average |
| 2027 NO/POR 2nd (most favorable, swap-resolved) | 3.7 | Below average |
| 2028 ORL 2nd | 1.0 | Fringe / throw-in |
| 2029 CHA 2nd | 1.0 | Fringe / throw-in |
| 2029 DEN 2nd | 1.0 | Fringe / throw-in |
| 2030 CHA 2nd (protected, doesn't convey #56-60) | 1.0 | Fringe / throw-in |
| 2031 CHA 2nd | 1.0 | Fringe / throw-in |
| 2031 MIL 2nd | 1.0 | Fringe / throw-in |
| 2031 PHX 2nd | 1.0 | Fringe / throw-in |
| 2032 CHA 2nd | 1.0 | Fringe / throw-in |
| 2032 MIL 2nd | 1.0 | Fringe / throw-in |
| 2033 CHA 2nd | 1.0 | Fringe / throw-in |
| 2027 BOS/ORL 2nd (least favorable, swap-resolved) | 1.0 | Fringe / throw-in |
| 2028 CHA/LAC 2nd (most favorable, swap-resolved) | 1.0 | Fringe / throw-in |
| 2030 LAC/UTA 2nd (most favorable, swap-resolved) | 1.0 | Fringe / throw-in |

**Unresolved (3):**
- 2028: MIA 1st (If 2027 MIA 1st is #15-30) -- *depends on a different pick's outcome (needs multi-year simulation)*
- 2028: MIA 2nd (If 2027 DAL 1st is #1-2) -- *depends on a different pick's outcome (needs multi-year simulation)*
- 2029: CLE/MIN (#6-30)/UTA (Least Favorable) 1st -- *nested parens or a continuation fragment -- needs manual resolution*

## Chicago Bulls

| Pick | Grade | Label |
|---|---|---|
| 2027 CHI 1st | 9.4 | Elite |
| 2028 CHI 1st | 9.1 | Elite |
| 2029 CHI 1st | 8.9 | Great |
| 2030 CHI 1st | 8.8 | Great |
| 2031 CHI 1st | 8.6 | Great |
| 2033 CHI 1st | 8.5 | Great |
| 2032 CHI 1st | 8.3 | Great |
| 2028 CHI 2nd | 1.9 | Weak |
| 2027 CLE 2nd | 1.0 | Fringe / throw-in |
| 2029 CHI 2nd | 1.0 | Fringe / throw-in |
| 2030 CHI 2nd | 1.0 | Fringe / throw-in |
| 2031 CHI 2nd | 1.0 | Fringe / throw-in |
| 2031 DEN 2nd | 1.0 | Fringe / throw-in |
| 2031 NYK 2nd | 1.0 | Fringe / throw-in |
| 2032 CHI 2nd | 1.0 | Fringe / throw-in |
| 2033 CHI 2nd | 1.0 | Fringe / throw-in |
| 2029 DET/MIL/NYK 2nd (least favorable, swap-resolved) | 1.0 | Fringe / throw-in |
| 2031 GS/MIN 2nd (most favorable, swap-resolved) | 1.0 | Fringe / throw-in |
| 2032 HOU/PHX 2nd (most favorable, swap-resolved) | 1.0 | Fringe / throw-in |

## Cleveland Cavaliers

| Pick | Grade | Label |
|---|---|---|
| 2030 CLE 1st | 5.5 | Above average |
| 2031 CLE 1st | 5.5 | Above average |
| 2032 CLE 1st | 5.5 | Above average |
| 2033 CLE 1st | 5.5 | Above average |
| 2028 ATL/CLE/UTA 1st (least favorable, swap-resolved) | 5.5 | Above average |
| 2033 CLE 2nd | 1.0 | Fringe / throw-in |

## Dallas Mavericks

| Pick | Grade | Label |
|---|---|---|
| 2031 DAL 1st | 8.6 | Great |
| 2032 DAL 1st | 8.3 | Great |
| 2033 DAL 1st | 8.2 | Great |
| 2029 LAL 1st | 6.7 | Good |
| 2028 DAL/OKC 1st (least favorable, swap-resolved) | 5.8 | Above average |
| 2027 DAL 1st (protected, doesn't convey #3-30) | 5.5 | Above average |
| 2030 DAL/SA 1st (least favorable, swap-resolved) | 5.5 | Above average |
| 2027 CHI 2nd | 3.7 | Below average |
| 2029 HOU 2nd | 1.0 | Fringe / throw-in |
| 2030 GS 1st (protected, doesn't convey #1-20) | 1.0 | Fringe / throw-in |
| 2030 PHI 2nd | 1.0 | Fringe / throw-in |
| 2032 DAL 2nd | 1.0 | Fringe / throw-in |
| 2033 DAL 2nd | 1.0 | Fringe / throw-in |

**Unresolved (1):**
- 2030: GS 2nd (If 2030 GS 1st is #1-20) -- *depends on a different pick's outcome (needs multi-year simulation)*

## Denver Nuggets

| Pick | Grade | Label |
|---|---|---|
| 2031 DEN 1st | 5.5 | Above average |
| 2033 DEN 1st | 5.5 | Above average |
| 2027 DEN 1st (protected, doesn't convey #6-30) | 1.0 | Fringe / throw-in |
| 2028 DEN 2nd (protected, doesn't convey #34-60) | 1.0 | Fringe / throw-in |
| 2033 DEN 2nd | 1.0 | Fringe / throw-in |

**Unresolved (3):**
- 2028: DEN 1st (If #1-5 and 2027 DEN 1st is #1-5) -- *doesn't match any known pattern*
- 2029: DEN 1st (If #1-5, 2027 DEN 1st is #1-5 and 2028 DEN 1st is #1-5) / DEN 1st (If #1-5) (If 2027 DEN 1st is #6-30) -- *depends on a different pick's outcome (needs multi-year simulation)*
- 2030: DEN 1st (If #1-5 and 2029 DEN 1st is #1-5) (If 2027 DEN 1st is #6-30) / DEN 1st (If #1-5) (If 2027 DEN 1st is #1-5 and 2028 DEN 1st is #6-30) -- *depends on a different pick's outcome (needs multi-year simulation)*

## Detroit Pistons

| Pick | Grade | Label |
|---|---|---|
| 2027 DET 1st | 6.9 | Good |
| 2028 DET 1st | 5.5 | Above average |
| 2029 DET 1st | 5.5 | Above average |
| 2030 DET 1st | 5.5 | Above average |
| 2031 DET 1st | 5.5 | Above average |
| 2032 DET 1st | 5.5 | Above average |
| 2033 DET 1st | 5.5 | Above average |
| 2027 MIL 2nd | 4.0 | Average |
| 2027 BKN/DAL 2nd (least favorable, swap-resolved) | 3.0 | Below average |
| 2027 DET 2nd | 1.0 | Fringe / throw-in |
| 2029 DET 2nd | 1.0 | Fringe / throw-in |
| 2029 MIL 2nd | 1.0 | Fringe / throw-in |
| 2029 NYK 2nd | 1.0 | Fringe / throw-in |
| 2030 DET 2nd | 1.0 | Fringe / throw-in |
| 2030 MIN 2nd | 1.0 | Fringe / throw-in |
| 2031 DAL 2nd | 1.0 | Fringe / throw-in |
| 2031 DET 2nd | 1.0 | Fringe / throw-in |
| 2032 DET 2nd | 1.0 | Fringe / throw-in |
| 2033 DET 2nd | 1.0 | Fringe / throw-in |
| 2031 GS/MIN 2nd (least favorable, swap-resolved) | 1.0 | Fringe / throw-in |

**Unresolved (3):**
- 2028: (CHA/LAC (Less Favorable))/DET (If #31-55)/MIA 2nd (If 2027 DAL 1st is #3-30)/NYK (Most Favorable) 2nd -- *depends on a different pick's outcome (needs multi-year simulation)*
- 2028: (2nd Favorable) 2nd -- *nested parens or a continuation fragment -- needs manual resolution*
- 2028: (3rd Favorable) 2nd -- *nested parens or a continuation fragment -- needs manual resolution*

## Golden State Warriors

| Pick | Grade | Label |
|---|---|---|
| 2027 GS 1st | 8.6 | Great |
| 2029 GS 1st | 8.5 | Great |
| 2028 GS 1st | 8.3 | Great |
| 2030 GS 1st (protected, doesn't convey #21-30) | 8.2 | Great |
| 2031 GS 1st | 8.2 | Great |
| 2032 GS 1st | 8.1 | Great |
| 2033 GS 1st | 6.6 | Good |
| 2033 GS 2nd | 1.0 | Fringe / throw-in |

**Unresolved (2):**
- 2030: GS 2nd (If 2030 GS 1st is #21-30) -- *depends on a different pick's outcome (needs multi-year simulation)*
- 2032: GS 2nd (#31-50) -- *parenthetical range with no 'If' -- unclear if it's a real condition*

## Houston Rockets

| Pick | Grade | Label |
|---|---|---|
| 2029 DAL/HOU/PHX 1st (most favorable, swap-resolved) | 9.4 | Elite |
| 2027 BKN/HOU 1st (most favorable, swap-resolved) | 9.2 | Elite |
| 2027 PHX 1st | 8.9 | Great |
| 2029 DAL/HOU/PHX 1st (rank 2 of 3, swap-resolved) | 7.8 | Great |
| 2031 HOU 1st | 7.0 | Good |
| 2030 HOU 1st | 6.9 | Good |
| 2032 HOU 1st | 6.9 | Good |
| 2028 HOU 1st | 6.6 | Good |
| 2033 HOU 1st | 5.5 | Above average |
| 2027 MEM 2nd | 3.7 | Below average |
| 2028 HOU 2nd | 1.0 | Fringe / throw-in |
| 2029 SAC 2nd | 1.0 | Fringe / throw-in |
| 2033 HOU 2nd | 1.0 | Fringe / throw-in |
| 2027 NO/POR 2nd (least favorable, swap-resolved) | 1.0 | Fringe / throw-in |
| 2031 ATL/HOU 2nd (least favorable, swap-resolved) | 1.0 | Fringe / throw-in |

## Indiana Pacers

| Pick | Grade | Label |
|---|---|---|
| 2028 IND 1st | 9.1 | Elite |
| 2030 IND 1st | 8.6 | Great |
| 2027 IND 1st | 8.5 | Great |
| 2031 IND 1st | 8.5 | Great |
| 2032 IND 1st | 8.1 | Great |
| 2033 IND 1st | 6.4 | Good |
| 2027 UTA 2nd | 2.6 | Below average |
| 2030 IND 2nd | 1.0 | Fringe / throw-in |
| 2032 IND 2nd | 1.0 | Fringe / throw-in |
| 2033 IND 2nd | 1.0 | Fringe / throw-in |
| 2028 IND/PHX 2nd (least favorable, swap-resolved) | 1.0 | Fringe / throw-in |
| 2029 IND/WAS 2nd (least favorable, swap-resolved) | 1.0 | Fringe / throw-in |
| 2031 IND/MEM/MIA 2nd (least favorable, swap-resolved) | 1.0 | Fringe / throw-in |

## Los Angeles Clippers

| Pick | Grade | Label |
|---|---|---|
| 2029 IND 1st | 8.9 | Great |
| 2033 LAC 1st | 8.5 | Great |
| 2030 LAC 1st | 6.1 | Good |
| 2031 LAC 1st | 5.8 | Above average |
| 2032 LAC 1st | 5.8 | Above average |
| 2028 DAL 2nd | 1.9 | Weak |
| 2031 LAC 2nd | 1.0 | Fringe / throw-in |
| 2032 LAC 2nd | 1.0 | Fringe / throw-in |
| 2033 LAC 2nd | 1.0 | Fringe / throw-in |

**Unresolved (2):**
- 2027: DEN (If #6-30)/LAC/OKC (Least Favorable) 1st -- *nested parens or a continuation fragment -- needs manual resolution*
- 2029: LAC 1st (If #1-3) / LAC (If #4-30)/PHI (Less Favorable) 1st -- *nested parens or a continuation fragment -- needs manual resolution*

## Los Angeles Lakers

| Pick | Grade | Label |
|---|---|---|
| 2028 LAL 1st | 6.9 | Good |
| 2030 LAL 1st | 6.0 | Good |
| 2031 LAL 1st | 5.5 | Above average |
| 2032 LAL 1st | 5.5 | Above average |
| 2033 LAL 1st | 5.5 | Above average |
| 2027 LAL 1st (protected, doesn't convey #5-30) | 1.0 | Fringe / throw-in |
| 2033 LAL 2nd | 1.0 | Fringe / throw-in |

## Memphis Grizzlies

| Pick | Grade | Label |
|---|---|---|
| 2027 MEM 1st | 9.2 | Elite |
| 2028 MEM 1st | 9.1 | Elite |
| 2027 CLE/MIN/UTA 1st (most favorable, swap-resolved) | 8.8 | Great |
| 2031 MEM 1st | 8.6 | Great |
| 2032 MEM 1st | 8.3 | Great |
| 2033 MEM 1st | 8.3 | Great |
| 2030 ORL 1st | 8.2 | Great |
| 2031 PHX 1st | 8.2 | Great |
| 2027 LAL 1st (protected, doesn't convey #1-4) | 6.9 | Good |
| 2029 POR 2nd | 1.0 | Fringe / throw-in |
| 2030 MEM 2nd (protected, doesn't convey #51-60) | 1.0 | Fringe / throw-in |
| 2033 MEM 2nd | 1.0 | Fringe / throw-in |
| 2032 MEM/PHI 2nd (most favorable, swap-resolved) | 1.0 | Fringe / throw-in |

**Unresolved (6):**
- 2027: LAL 2nd (If 2027 LAL 1st is #1-4) -- *depends on a different pick's outcome (needs multi-year simulation)*
- 2029: MEM/ORL (If #3-30) (More Favorable) 1st -- *nested parens or a continuation fragment -- needs manual resolution*
- 2029: ORL 2nd (If 2029 ORL 1st is #1-2) -- *depends on a different pick's outcome (needs multi-year simulation)*
- 2030: MEM/(PHX/WAS (Less Favorable)) (More Favorable) 1st -- *nested parens or a continuation fragment -- needs manual resolution*
- 2031: (IND/MIA (Less Favorable))/MEM (More Favorable) 2nd -- *nested parens or a continuation fragment -- needs manual resolution*
- 2032: GS 2nd (#51-60) -- *parenthetical range with no 'If' -- unclear if it's a real condition*

## Miami Heat

| Pick | Grade | Label |
|---|---|---|
| 2029 MIA 1st | 8.8 | Great |
| 2032 MIA 1st | 8.1 | Great |
| 2027 MIA 1st (protected, doesn't convey #15-30) | 5.5 | Above average |
| 2030 MIA/MIL/POR 1st (least favorable, swap-resolved) | 5.5 | Above average |

**Unresolved (2):**
- 2027: HOU/IND/MIA/OKC/SA (Least Favorable) 2nd -- *doesn't match any known pattern*
- 2028: MIA 1st (If 2027 MIA 1st is #15-30) -- *depends on a different pick's outcome (needs multi-year simulation)*

## Milwaukee Bucks

| Pick | Grade | Label |
|---|---|---|
| 2033 MIL 1st | 8.3 | Great |
| 2031 MIA 1st | 8.2 | Great |
| 2031 MIL 1st | 7.8 | Great |
| 2032 MIL 1st | 7.5 | Great |
| 2033 MIA 1st | 5.7 | Above average |
| 2033 MIA 2nd | 1.0 | Fringe / throw-in |
| 2033 MIL 2nd | 1.0 | Fringe / throw-in |

**Unresolved (2):**
- 2028: ((BKN/PHI (If #9-30)/PHX (Least Favorable)/WAS (More Favorable))/MIL/POR (Least Favorable) 1st -- *nested parens or a continuation fragment -- needs manual resolution*
- 2030: MIA/(MIL/POR (Less Favorable)) (More Favorable) 1st -- *nested parens or a continuation fragment -- needs manual resolution*

## Minnesota Timberwolves

| Pick | Grade | Label |
|---|---|---|
| 2028 MIN 1st | 7.3 | Good |
| 2032 MIN 1st | 5.5 | Above average |
| 2033 MIN 1st | 5.5 | Above average |
| 2029 MIN 1st (protected, doesn't convey #6-30) | 1.0 | Fringe / throw-in |
| 2030 MEM 2nd (protected, doesn't convey #31-50) | 1.0 | Fringe / throw-in |
| 2032 MIN 2nd | 1.0 | Fringe / throw-in |
| 2033 MIN 2nd | 1.0 | Fringe / throw-in |

**Unresolved (2):**
- 2029: MIN 2nd (If 2029 MIN 1st is #6-30) -- *depends on a different pick's outcome (needs multi-year simulation)*
- 2030: MIN 1st (If #1) / MIN (If #2-30)/(DAL/SA (More Favorable)) (Less Favorable) 1st -- *nested parens or a continuation fragment -- needs manual resolution*

## New Orleans Pelicans

| Pick | Grade | Label |
|---|---|---|
| 2027 MIL/NO 1st (most favorable, swap-resolved) | 9.5 | Elite |
| 2028 NO 1st | 9.1 | Elite |
| 2029 NO 1st | 8.9 | Great |
| 2030 NO 1st | 8.8 | Great |
| 2031 NO 1st | 8.6 | Great |
| 2032 NO 1st | 8.3 | Great |
| 2033 NO 1st | 8.3 | Great |
| 2031 TOR 2nd | 1.0 | Fringe / throw-in |
| 2032 NO 2nd | 1.0 | Fringe / throw-in |
| 2033 NO 2nd | 1.0 | Fringe / throw-in |
| 2027 MIL/NO 1st (least favorable, swap-resolved) | 1.0 | Fringe / throw-in |
| 2027 HOU/IND/MIA/OKC 2nd (rank 2 of 4, swap-resolved) | 1.0 | Fringe / throw-in |
| 2030 NO/ORL 2nd (least favorable, swap-resolved) | 1.0 | Fringe / throw-in |

## New York Knicks

| Pick | Grade | Label |
|---|---|---|
| 2030 NYK 1st | 5.5 | Above average |
| 2032 NYK 1st | 5.5 | Above average |
| 2033 NYK 1st | 5.5 | Above average |
| 2028 BKN/NYK 1st (least favorable, swap-resolved) | 5.5 | Above average |
| 2027 WAS 2nd | 2.8 | Below average |
| 2027 NYK 2nd | 1.0 | Fringe / throw-in |
| 2028 BOS 2nd (protected, doesn't convey #31-45) | 1.0 | Fringe / throw-in |
| 2032 NYK 2nd | 1.0 | Fringe / throw-in |
| 2033 NYK 2nd | 1.0 | Fringe / throw-in |
| 2027 HOU/IND/MIA/OKC 2nd (rank 3 of 4, swap-resolved) | 1.0 | Fringe / throw-in |
| 2028 IND/PHX 2nd (least favorable, swap-resolved) | 1.0 | Fringe / throw-in |

## Oklahoma City Thunder

| Pick | Grade | Label |
|---|---|---|
| 2028 DAL/OKC 1st (most favorable, swap-resolved) | 9.2 | Elite |
| 2027 SA 1st (protected, doesn't convey #1-16) | 5.5 | Above average |
| 2029 OKC 1st | 5.5 | Above average |
| 2030 OKC 1st | 5.5 | Above average |
| 2031 OKC 1st | 5.5 | Above average |
| 2032 OKC 1st | 5.5 | Above average |
| 2033 OKC 1st | 5.5 | Above average |
| 2028 UTA 2nd | 2.0 | Weak |
| 2029 ATL 2nd | 1.0 | Fringe / throw-in |
| 2029 BOS 2nd | 1.0 | Fringe / throw-in |
| 2029 MIA 2nd | 1.0 | Fringe / throw-in |
| 2029 OKC 2nd | 1.0 | Fringe / throw-in |
| 2030 ATL 2nd | 1.0 | Fringe / throw-in |
| 2030 DEN 2nd | 1.0 | Fringe / throw-in |
| 2030 HOU 2nd | 1.0 | Fringe / throw-in |
| 2030 MIA 2nd | 1.0 | Fringe / throw-in |
| 2030 OKC 2nd | 1.0 | Fringe / throw-in |
| 2031 OKC 2nd | 1.0 | Fringe / throw-in |
| 2032 OKC 2nd | 1.0 | Fringe / throw-in |
| 2033 OKC 2nd | 1.0 | Fringe / throw-in |
| 2031 NO/ORL 2nd (least favorable, swap-resolved) | 1.0 | Fringe / throw-in |
| 2032 ATL/LAL 2nd (least favorable, swap-resolved) | 1.0 | Fringe / throw-in |

**Unresolved (7):**
- 2027: DEN (If #6-30)/LAC/OKC (Most Favorable) 1st -- *nested parens or a continuation fragment -- needs manual resolution*
- 2027: (2nd Most Favorable) 1st -- *nested parens or a continuation fragment -- needs manual resolution*
- 2027: CHA 2nd (If 2027 SA 1st is #1-16) -- *depends on a different pick's outcome (needs multi-year simulation)*
- 2027: SAC 2nd (If 2027 SA 1st is #1-16) -- *depends on a different pick's outcome (needs multi-year simulation)*
- 2028: DEN 1st (If #6-30, If 2027 DEN 1st is #1-5) -- *doesn't match any known pattern*
- 2029: DEN 1st (conditional chain) -- *doesn't match any known pattern*
- 2030: DEN 1st (conditional chain) -- *doesn't match any known pattern*

## Orlando Magic

| Pick | Grade | Label |
|---|---|---|
| 2027 ORL 1st | 8.8 | Great |
| 2031 ORL 1st | 7.9 | Great |
| 2032 ORL 1st | 7.6 | Great |
| 2033 ORL 1st | 7.0 | Good |
| 2028 LAL/WAS 2nd (most favorable, swap-resolved) | 2.8 | Below average |
| 2030 MIL 2nd | 1.0 | Fringe / throw-in |
| 2032 ORL 2nd | 1.0 | Fringe / throw-in |
| 2033 ORL 2nd | 1.0 | Fringe / throw-in |
| 2030 NO/ORL 2nd (most favorable, swap-resolved) | 1.0 | Fringe / throw-in |
| 2031 NO/ORL 2nd (most favorable, swap-resolved) | 1.0 | Fringe / throw-in |

**Unresolved (2):**
- 2029: ORL 1st (If #1-2) / MEM/ORL (If #3-30) (Less Favorable) 1st -- *nested parens or a continuation fragment -- needs manual resolution*
- 2029: ORL 2nd (If 2029 ORL 1st is #3-30) -- *depends on a different pick's outcome (needs multi-year simulation)*

## Philadelphia 76ers

| Pick | Grade | Label |
|---|---|---|
| 2030 PHI 1st | 7.6 | Great |
| 2031 PHI 1st | 7.3 | Good |
| 2028 LAC 1st | 7.2 | Good |
| 2032 PHI 1st | 7.0 | Good |
| 2027 PHI 1st | 6.9 | Good |
| 2028 PHI 1st (protected, doesn't convey #9-30) | 5.5 | Above average |
| 2033 PHI 1st | 5.5 | Above average |
| 2027 GS/PHX 2nd (most favorable, swap-resolved) | 2.6 | Below average |
| 2027 HOU/IND/MIA/OKC 2nd (most favorable, swap-resolved) | 1.9 | Weak |
| 2027 PHI 2nd | 1.0 | Fringe / throw-in |
| 2028 DET 2nd (protected, doesn't convey #31-55) | 1.0 | Fringe / throw-in |
| 2028 GS 2nd | 1.0 | Fringe / throw-in |
| 2028 MIL 2nd | 1.0 | Fringe / throw-in |
| 2028 OKC 2nd | 1.0 | Fringe / throw-in |
| 2029 PHI 2nd | 1.0 | Fringe / throw-in |
| 2030 WAS 2nd | 1.0 | Fringe / throw-in |
| 2031 PHI 2nd | 1.0 | Fringe / throw-in |
| 2033 PHI 2nd | 1.0 | Fringe / throw-in |
| 2030 PHX/POR 2nd (most favorable, swap-resolved) | 1.0 | Fringe / throw-in |
| 2032 MEM/PHI 2nd (least favorable, swap-resolved) | 1.0 | Fringe / throw-in |

**Unresolved (2):**
- 2028: PHI 2nd (If 2028 PHI 1st is #9-30) -- *depends on a different pick's outcome (needs multi-year simulation)*
- 2029: LAC (If #4-30)/PHI (More Favorable) 1st -- *nested parens or a continuation fragment -- needs manual resolution*

## Phoenix Suns

| Pick | Grade | Label |
|---|---|---|
| 2032 PHX 1st | 7.9 | Great |
| 2033 PHX 1st | 7.5 | Great |
| 2030 MEM/PHX/WAS 1st (least favorable, swap-resolved) | 6.4 | Good |
| 2027 CLE/MIN/UTA 1st (least favorable, swap-resolved) | 6.0 | Good |
| 2029 PHX 2nd | 1.0 | Fringe / throw-in |
| 2033 PHX 2nd | 1.0 | Fringe / throw-in |
| 2032 HOU/PHX 2nd (least favorable, swap-resolved) | 1.0 | Fringe / throw-in |

**Unresolved (1):**
- 2028: BKN/PHI (If #9-30)/PHX/WAS (Least Favorable) 1st -- *nested parens or a continuation fragment -- needs manual resolution*

## Portland Trail Blazers

| Pick | Grade | Label |
|---|---|---|
| 2028 MIL/POR 1st (most favorable, swap-resolved) | 9.2 | Elite |
| 2029 BOS/MIL/POR 1st (most favorable, swap-resolved) | 9.2 | Elite |
| 2030 MIL/POR 1st (most favorable, swap-resolved) | 8.9 | Great |
| 2028 ORL 1st | 8.5 | Great |
| 2027 POR 1st | 8.3 | Great |
| 2031 POR 1st | 8.1 | Great |
| 2032 POR 1st | 7.8 | Great |
| 2033 POR 1st | 6.1 | Good |
| 2029 BOS/MIL/POR 1st (least favorable, swap-resolved) | 5.5 | Above average |
| 2028 SAC 2nd | 2.0 | Weak |
| 2027 MIN 2nd | 1.0 | Fringe / throw-in |
| 2028 POR 2nd | 1.0 | Fringe / throw-in |
| 2031 POR 2nd | 1.0 | Fringe / throw-in |
| 2032 POR 2nd | 1.0 | Fringe / throw-in |
| 2033 POR 2nd | 1.0 | Fringe / throw-in |
| 2027 NO/POR 2nd (least favorable, swap-resolved) | 1.0 | Fringe / throw-in |
| 2029 IND/WAS 2nd (least favorable, swap-resolved) | 1.0 | Fringe / throw-in |

## Sacramento Kings

| Pick | Grade | Label |
|---|---|---|
| 2027 SAC 1st | 9.2 | Elite |
| 2028 SAC 1st | 9.2 | Elite |
| 2029 SAC 1st | 9.1 | Elite |
| 2030 SAC 1st | 8.9 | Great |
| 2032 SAC 1st | 8.5 | Great |
| 2033 SAC 1st | 8.2 | Great |
| 2031 MIN 1st | 5.7 | Above average |
| 2031 SAC/SA 1st (least favorable, swap-resolved) | 5.5 | Above average |
| 2027 SA 1st (protected, doesn't convey #17-30) | 1.0 | Fringe / throw-in |
| 2032 SAC 2nd | 1.0 | Fringe / throw-in |
| 2033 SAC 2nd | 1.0 | Fringe / throw-in |

**Unresolved (2):**
- 2027: CHA 2nd (If 2027 SA 1st is #17-30) -- *depends on a different pick's outcome (needs multi-year simulation)*
- 2027: SAC 2nd (If 2027 SA 1st is #17-30) -- *depends on a different pick's outcome (needs multi-year simulation)*

## San Antonio Spurs

| Pick | Grade | Label |
|---|---|---|
| 2031 SAC/SA 1st (most favorable, swap-resolved) | 8.8 | Great |
| 2027 ATL 1st | 8.6 | Great |
| 2029 SA 1st | 5.5 | Above average |
| 2032 SA 1st | 5.5 | Above average |
| 2033 SA 1st | 5.5 | Above average |
| 2028 NO 2nd | 1.9 | Weak |
| 2028 MIN 2nd | 1.0 | Fringe / throw-in |
| 2028 SA 2nd | 1.0 | Fringe / throw-in |
| 2029 LAC 2nd | 1.0 | Fringe / throw-in |
| 2029 NO 2nd | 1.0 | Fringe / throw-in |
| 2029 SA 2nd | 1.0 | Fringe / throw-in |
| 2030 CLE 2nd | 1.0 | Fringe / throw-in |
| 2030 SAC 2nd | 1.0 | Fringe / throw-in |
| 2030 SA 2nd | 1.0 | Fringe / throw-in |
| 2031 SAC 2nd | 1.0 | Fringe / throw-in |
| 2031 SA 2nd | 1.0 | Fringe / throw-in |
| 2032 SA 2nd | 1.0 | Fringe / throw-in |
| 2033 SA 2nd | 1.0 | Fringe / throw-in |

**Unresolved (4):**
- 2027: (HOU/IND/MIA/OKC (Least Favorable))/SA (More Favorable) 2nd -- *nested parens or a continuation fragment -- needs manual resolution*
- 2028: BOS (If #2-30)/SA (More Favorable) 1st -- *nested parens or a continuation fragment -- needs manual resolution*
- 2028: BOS 2nd (If #31-45) (If 2028 BOS 1st is #1) -- *depends on a different pick's outcome (needs multi-year simulation)*
- 2030: DAL/MIN (If #2-30)/SA (Most Favorable) 1st -- *nested parens or a continuation fragment -- needs manual resolution*

## Toronto Raptors

| Pick | Grade | Label |
|---|---|---|
| 2027 TOR 1st | 8.3 | Great |
| 2028 TOR 1st | 7.0 | Good |
| 2029 TOR 1st | 6.6 | Good |
| 2030 TOR 1st | 6.1 | Good |
| 2033 TOR 1st | 6.1 | Good |
| 2031 TOR 1st | 5.8 | Above average |
| 2032 TOR 1st | 5.5 | Above average |
| 2027 TOR 2nd | 1.0 | Fringe / throw-in |
| 2028 TOR 2nd | 1.0 | Fringe / throw-in |
| 2029 TOR 2nd | 1.0 | Fringe / throw-in |
| 2030 TOR 2nd | 1.0 | Fringe / throw-in |
| 2033 TOR 2nd | 1.0 | Fringe / throw-in |

## Utah Jazz

| Pick | Grade | Label |
|---|---|---|
| 2028 CLE/UTA 1st (most favorable, swap-resolved) | 9.1 | Elite |
| 2030 UTA 1st | 8.8 | Great |
| 2031 UTA 1st | 8.6 | Great |
| 2032 UTA 1st | 8.3 | Great |
| 2033 UTA 1st | 8.1 | Great |
| 2027 CLE/MIN/UTA 1st (rank 2 of 3, swap-resolved) | 7.2 | Good |
| 2027 LAC 2nd | 3.5 | Below average |
| 2027 BOS/ORL 2nd (most favorable, swap-resolved) | 1.4 | Fringe / throw-in |
| 2027 DEN 2nd | 1.0 | Fringe / throw-in |
| 2028 CLE 2nd | 1.0 | Fringe / throw-in |
| 2029 UTA 2nd | 1.0 | Fringe / throw-in |
| 2032 CLE 2nd | 1.0 | Fringe / throw-in |
| 2033 UTA 2nd | 1.0 | Fringe / throw-in |
| 2030 LAC/UTA 2nd (least favorable, swap-resolved) | 1.0 | Fringe / throw-in |
| 2031 BOS/CLE 2nd (most favorable, swap-resolved) | 1.0 | Fringe / throw-in |

**Unresolved (5):**
- 2028: (CHA/LAC (Less Favorable))/DET (If #31-55)/MIA (If 2027 DAL 1st is #3-30)/NYK (Least Favorable) 2nd -- *depends on a different pick's outcome (needs multi-year simulation)*
- 2029: CLE/MIN (If #6-30)/UTA (Most Favorable) 1st -- *nested parens or a continuation fragment -- needs manual resolution*
- 2029: (2nd Favorable) 1st -- *nested parens or a continuation fragment -- needs manual resolution*
- 2029: MIN 2nd (If 2029 MIN 1st is #1-5) -- *depends on a different pick's outcome (needs multi-year simulation)*
- 2031: (IND/MIA (More Favorable))/UTA (Less Favorable) 2nd -- *nested parens or a continuation fragment -- needs manual resolution*

## Washington Wizards

| Pick | Grade | Label |
|---|---|---|
| 2027 WAS 1st | 9.2 | Elite |
| 2030 PHX/WAS 1st (most favorable, swap-resolved) | 9.2 | Elite |
| 2029 WAS 1st | 8.9 | Great |
| 2031 WAS 1st | 8.8 | Great |
| 2032 WAS 1st | 8.5 | Great |
| 2033 WAS 1st | 8.5 | Great |
| 2029 BOS/MIL/POR 1st (rank 2 of 3, swap-resolved) | 7.2 | Good |
| 2027 BKN/DAL 2nd (most favorable, swap-resolved) | 4.2 | Average |
| 2027 GS/PHX 2nd (least favorable, swap-resolved) | 1.6 | Weak |
| 2028 DEN 2nd (protected, doesn't convey #31-33) | 1.0 | Fringe / throw-in |
| 2029 LAL 2nd | 1.0 | Fringe / throw-in |
| 2031 WAS 2nd | 1.0 | Fringe / throw-in |
| 2032 UTA 2nd | 1.0 | Fringe / throw-in |
| 2032 WAS 2nd | 1.0 | Fringe / throw-in |
| 2033 WAS 2nd | 1.0 | Fringe / throw-in |
| 2028 LAL/WAS 2nd (least favorable, swap-resolved) | 1.0 | Fringe / throw-in |
| 2030 PHX/POR 2nd (least favorable, swap-resolved) | 1.0 | Fringe / throw-in |
| 2031 IND/MIA/UTA 2nd (most favorable, swap-resolved) | 1.0 | Fringe / throw-in |

**Unresolved (1):**
- 2028: (BKN/PHI (If #9-30)/PHX (Least Favorable))/(MIL/POR (Less Favorable)/WAS (Most Favorable)) -- *nested parens or a continuation fragment -- needs manual resolution*
