# NBA Draft Pick Grades -- Full League Run

2027-draft ratings calibrated from consensus market win totals (DraftKings/FanDuel/Hard Rock/Caesars 2026-27 O/U lines); the 2028-2032 drafts use DARKO DPM + career longevity data instead, calibrated against those same market ratings (darko_ratings.py); 2033 falls back to the flat 2026-27 market ratings. Picks graded 1-10 via the swap-resolved pipeline. 2000 simulation trials per team per draft year. Grades and averages below are split by round -- 2nd-round picks carry the pick_valuation.py 0.4x haircut baked into their value, so mixing rounds into one average would understate 1st-round strength and overstate 2nd-round weakness relative to each other.

## League summary: average pick grade by team, split by round

| Team | Avg 1st-rd grade | 1st-rd picks | Avg 2nd-rd grade | 2nd-rd picks | Unresolved |
|---|---|---|---|---|---|
| Chicago Bulls | 8.40 | 7 | 1.10 | 12 | 0 |
| Washington Wizards | 8.40 | 7 | 1.52 | 6 | 1 |
| Houston Rockets | 7.83 | 9 | 1.00 | 2 | 0 |
| Atlanta Hawks | 7.80 | 7 | 1.26 | 5 | 0 |
| Portland Trail Blazers | 7.74 | 9 | 1.06 | 8 | 0 |
| Indiana Pacers | 7.65 | 6 | 1.30 | 7 | 0 |
| Milwaukee Bucks | 7.50 | 6 | 1.82 | 4 | 1 |
| New Orleans Pelicans | 7.44 | 8 | 1.06 | 5 | 0 |
| Los Angeles Clippers | 7.35 | 8 | 1.23 | 7 | 3 |
| Utah Jazz | 6.84 | 9 | 1.35 | 10 | 3 |
| Golden State Warriors | 6.80 | 8 | 1.00 | 2 | 0 |
| Miami Heat | 6.78 | 5 | 1.00 | 1 | 0 |
| Dallas Mavericks | 6.60 | 7 | -- | 0 | 0 |
| Sacramento Kings | 6.60 | 11 | -- | 0 | 0 |
| New York Knicks | 6.55 | 4 | 1.17 | 12 | 0 |
| Brooklyn Nets | 6.40 | 13 | 1.02 | 18 | 2 |
| Phoenix Suns | 6.40 | 3 | 1.00 | 2 | 2 |
| Boston Celtics | 6.31 | 7 | 1.11 | 7 | 2 |
| Detroit Pistons | 6.24 | 7 | 1.00 | 8 | 3 |
| Cleveland Cavaliers | 6.18 | 5 | 1.00 | 2 | 0 |
| Charlotte Hornets | 6.17 | 12 | 1.29 | 18 | 2 |
| Memphis Grizzlies | 6.16 | 14 | 1.00 | 11 | 1 |
| Orlando Magic | 6.12 | 5 | 1.10 | 6 | 1 |
| Toronto Raptors | 5.90 | 4 | 1.30 | 3 | 1 |
| San Antonio Spurs | 5.60 | 6 | 1.00 | 12 | 2 |
| Minnesota Timberwolves | 5.50 | 3 | 1.00 | 1 | 1 |
| Philadelphia 76ers | 5.48 | 5 | 1.30 | 10 | 3 |
| Oklahoma City Thunder | 4.90 | 9 | 1.12 | 17 | 6 |
| Denver Nuggets | 4.60 | 3 | 1.00 | 4 | 3 |
| Los Angeles Lakers | 4.42 | 4 | 1.00 | 3 | 0 |

## Atlanta Hawks

### 1st Round Picks (avg grade 7.80)

| Pick | Grade | Label |
|---|---|---|
| 2028 ATL/(CLE/UTA Less Favorable) (More Favorable) 1st (nested swap-resolved) | 8.6 | Great |
| 2029 ATL 1st | 8.3 | Great |
| 2030 ATL 1st | 8.3 | Great |
| 2031 ATL 1st | 8.3 | Great |
| 2027 MIL/NO 1st (least favorable, swap-resolved) | 8.1 | Great |
| 2032 ATL 1st | 7.5 | Great |
| 2033 ATL 1st | 5.5 | Above average |

### 2nd Round Picks (avg grade 1.26)

| Pick | Grade | Label |
|---|---|---|
| 2027 ATL 2nd | 2.3 | Weak |
| 2029 CLE 2nd | 1.0 | Fringe / throw-in |
| 2030 NYK 2nd | 1.0 | Fringe / throw-in |
| 2033 ATL 2nd | 1.0 | Fringe / throw-in |
| 2033 SAC 2nd | 1.0 | Fringe / throw-in |

## Boston Celtics

### 1st Round Picks (avg grade 6.31)

| Pick | Grade | Label |
|---|---|---|
| 2030 BOS 1st | 8.1 | Great |
| 2031 PHI 1st | 8.1 | Great |
| 2031 BOS 1st | 7.9 | Great |
| 2032 BOS 1st | 7.0 | Good |
| 2027 BOS 1st | 6.6 | Good |
| 2033 BOS 1st | 5.5 | Above average |
| 2028 BOS 2nd (conveys only if BOS 1st is #2-30, own protection (46, 60), conditional-resolved) | 1.0 | Fringe / throw-in |

### 2nd Round Picks (avg grade 1.11)

| Pick | Grade | Label |
|---|---|---|
| 2028 GS/MIL/OKC 2nd (most favorable, swap-resolved) | 1.8 | Weak |
| 2030 CHA 2nd (protected, doesn't convey #31-55) | 1.0 | Fringe / throw-in |
| 2031 HOU 2nd (protected, doesn't convey #31-55) | 1.0 | Fringe / throw-in |
| 2032 BOS 2nd | 1.0 | Fringe / throw-in |
| 2033 BOS 2nd | 1.0 | Fringe / throw-in |
| 2030 PHX/POR/WAS 2nd (most favorable, swap-resolved) | 1.0 | Fringe / throw-in |
| 2031 BOS/CLE 2nd (least favorable, swap-resolved) | 1.0 | Fringe / throw-in |

**Unresolved (2):**
- 2028: (BOS (If #1))/LAC (If #1-16)/(PHI (If #1-8)) (Most Favorable) 1st / ((BOS (#2-30))/SA (Less Favorable))/LAC (If #1-16)/(PHI (If #1-8)) (Most Favorable) 1st -- *nested parens or a continuation fragment -- needs manual resolution*
- 2028: LAC 1st (If #17-30) (If PHI 1st is #9-30) -- *nested parens or a continuation fragment -- needs manual resolution*

## Brooklyn Nets

### 1st Round Picks (avg grade 6.40)

| Pick | Grade | Label |
|---|---|---|
| 2029 BKN 1st | 9.1 | Elite |
| 2030 BKN 1st | 8.9 | Great |
| 2033 BKN 1st | 8.9 | Great |
| 2029 NYK 1st | 8.2 | Great |
| 2031 BKN 1st | 8.1 | Great |
| 2031 NYK 1st | 7.2 | Good |
| 2032 BKN 1st | 7.0 | Good |
| 2027 BKN/HOU 1st (least favorable, swap-resolved) | 6.7 | Good |
| 2027 NYK 1st | 6.1 | Good |
| 2032 DEN 1st | 5.5 | Above average |
| 2029 DAL/HOU/PHX 1st (least favorable, swap-resolved) | 5.5 | Above average |
| 2027 LAL 2nd (conveys only if LAL 1st is #5-30, conditional-resolved) | 1.0 | Fringe / throw-in |
| 2028 PHI 2nd (conveys only if PHI 1st is #1-8, conditional-resolved) | 1.0 | Fringe / throw-in |

### 2nd Round Picks (avg grade 1.02)

| Pick | Grade | Label |
|---|---|---|
| 2028 MEM 2nd | 1.3 | Fringe / throw-in |
| 2028 BKN 2nd | 1.1 | Fringe / throw-in |
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

**Unresolved (2):**
- 2028: BKN/NYK/PHI 1st (If #9-30)/PHX (Most Favorable) 1st -- *nested parens or a continuation fragment -- needs manual resolution*
- 2028: BKN/NYK/PHI 1st (If #9-30)/PHX (2nd Favorable) 1st -- *nested parens or a continuation fragment -- needs manual resolution*

## Charlotte Hornets

### 1st Round Picks (avg grade 6.17)

| Pick | Grade | Label |
|---|---|---|
| 2027 CHA 1st | 9.1 | Elite |
| 2028 CHA/MIN 1st (most favorable, swap-resolved) | 9.1 | Elite |
| 2027 DAL 1st (protected, doesn't convey #1-2) | 8.3 | Great |
| 2031 CHA 1st | 8.3 | Great |
| 2032 CHA 1st | 7.9 | Great |
| 2028 MIA 1st (conveys only if 2027 MIA 1st is #15-30, cross-year-conditional-resolved) | 6.7 | Good |
| 2033 CHA 1st | 6.1 | Good |
| 2027 MIA 1st (protected, doesn't convey #1-14) | 5.5 | Above average |
| 2033 MIN 1st | 5.5 | Above average |
| 2033 PHX 1st | 5.5 | Above average |
| 2028 MIA 2nd (conveys only if 2027 DAL 1st is #1-2, cross-year-conditional-resolved) | 1.0 | Fringe / throw-in |
| 2029 MIN 2nd (conveys only if MIN 1st is #6-30, conditional-resolved) | 1.0 | Fringe / throw-in |

### 2nd Round Picks (avg grade 1.29)

| Pick | Grade | Label |
|---|---|---|
| 2027 NO/POR 2nd (most favorable, swap-resolved) | 3.4 | Below average |
| 2027 MEM 2nd | 3.0 | Below average |
| 2028 CHA/LAC 2nd (most favorable, swap-resolved) | 1.9 | Weak |
| 2028 HOU 2nd | 1.0 | Fringe / throw-in |
| 2028 ORL 2nd | 1.0 | Fringe / throw-in |
| 2029 CHA 2nd | 1.0 | Fringe / throw-in |
| 2029 DEN 2nd | 1.0 | Fringe / throw-in |
| 2030 CHA 2nd (protected, doesn't convey #56-60) | 1.0 | Fringe / throw-in |
| 2031 CHA 2nd | 1.0 | Fringe / throw-in |
| 2031 MIL 2nd | 1.0 | Fringe / throw-in |
| 2031 PHX 2nd | 1.0 | Fringe / throw-in |
| 2032 CHA 2nd | 1.0 | Fringe / throw-in |
| 2032 MIL 2nd | 1.0 | Fringe / throw-in |
| 2032 MIN 2nd | 1.0 | Fringe / throw-in |
| 2033 CHA 2nd | 1.0 | Fringe / throw-in |
| 2033 HOU 2nd | 1.0 | Fringe / throw-in |
| 2033 MIN 2nd | 1.0 | Fringe / throw-in |
| 2030 LAC/UTA 2nd (most favorable, swap-resolved) | 1.0 | Fringe / throw-in |

**Unresolved (2):**
- 2029: CHA/(MIN (If #1-5)) (More Favorable) 1st -- *nested parens or a continuation fragment -- needs manual resolution*
- 2030: CHA/MIN (More Favorable) 1st (If #1) / CHA/((DAL/SA (More Favorable))/MIN (Less Favorable)) (More Favorable) 1st (If #2-30) -- *nested parens or a continuation fragment -- needs manual resolution*

## Chicago Bulls

### 1st Round Picks (avg grade 8.40)

| Pick | Grade | Label |
|---|---|---|
| 2027 CHI 1st | 9.2 | Elite |
| 2028 CHI 1st | 8.9 | Great |
| 2029 CHI 1st | 8.6 | Great |
| 2032 CHI 1st | 8.6 | Great |
| 2033 CHI 1st | 8.5 | Great |
| 2030 CHI 1st | 8.3 | Great |
| 2031 CHI 1st | 6.7 | Good |

### 2nd Round Picks (avg grade 1.10)

| Pick | Grade | Label |
|---|---|---|
| 2028 CHI/IND/PHX 2nd (most favorable, swap-resolved) | 2.2 | Weak |
| 2027 CLE 2nd | 1.0 | Fringe / throw-in |
| 2029 CHI 2nd | 1.0 | Fringe / throw-in |
| 2031 CHI 2nd | 1.0 | Fringe / throw-in |
| 2031 DEN 2nd | 1.0 | Fringe / throw-in |
| 2031 NYK 2nd | 1.0 | Fringe / throw-in |
| 2032 CHI 2nd | 1.0 | Fringe / throw-in |
| 2033 CHI 2nd | 1.0 | Fringe / throw-in |
| 2029 DET/MIL/NYK 2nd (least favorable, swap-resolved) | 1.0 | Fringe / throw-in |
| 2030 CHI/IND 2nd (most favorable, swap-resolved) | 1.0 | Fringe / throw-in |
| 2031 GS/MIN 2nd (most favorable, swap-resolved) | 1.0 | Fringe / throw-in |
| 2032 HOU/PHX 2nd (most favorable, swap-resolved) | 1.0 | Fringe / throw-in |

## Cleveland Cavaliers

### 1st Round Picks (avg grade 6.18)

| Pick | Grade | Label |
|---|---|---|
| 2031 CLE 1st | 6.7 | Good |
| 2032 CLE 1st | 6.6 | Good |
| 2030 CLE 1st | 6.4 | Good |
| 2028 ATL/CLE/UTA 1st (least favorable, swap-resolved) | 5.7 | Above average |
| 2033 CLE 1st | 5.5 | Above average |

### 2nd Round Picks (avg grade 1.00)

| Pick | Grade | Label |
|---|---|---|
| 2032 SAC 2nd | 1.0 | Fringe / throw-in |
| 2033 CLE 2nd | 1.0 | Fringe / throw-in |

## Dallas Mavericks

### 1st Round Picks (avg grade 6.60)

| Pick | Grade | Label |
|---|---|---|
| 2031 DAL 1st | 8.5 | Great |
| 2032 DAL 1st | 7.9 | Great |
| 2029 LAL 1st | 6.9 | Good |
| 2033 DAL 1st | 6.4 | Good |
| 2027 DAL 1st (protected, doesn't convey #3-30) | 5.5 | Above average |
| 2028 DAL/OKC 1st (least favorable, swap-resolved) | 5.5 | Above average |
| 2030 DAL/SA 1st (least favorable, swap-resolved) | 5.5 | Above average |

### 2nd Round Picks (none)

## Denver Nuggets

### 1st Round Picks (avg grade 4.60)

| Pick | Grade | Label |
|---|---|---|
| 2031 DEN 1st | 7.3 | Good |
| 2033 DEN 1st | 5.5 | Above average |
| 2027 DEN 1st (protected, doesn't convey #6-30) | 1.0 | Fringe / throw-in |

### 2nd Round Picks (avg grade 1.00)

| Pick | Grade | Label |
|---|---|---|
| 2028 DEN 2nd (protected, doesn't convey #34-60) | 1.0 | Fringe / throw-in |
| 2028 MIN 2nd | 1.0 | Fringe / throw-in |
| 2031 SAC 2nd | 1.0 | Fringe / throw-in |
| 2033 DEN 2nd | 1.0 | Fringe / throw-in |

**Unresolved (3):**
- 2028: DEN 1st (If #1-5 and 2027 DEN 1st is #1-5) -- *doesn't match any known pattern*
- 2029: DEN 1st (If #1-5, 2027 DEN 1st is #1-5 and 2028 DEN 1st is #1-5) / DEN 1st (If #1-5) (If 2027 DEN 1st is #6-30) -- *depends on a different pick's outcome (needs multi-year simulation)*
- 2030: DEN 1st (If #1-5 and 2029 DEN 1st is #1-5) (If 2027 DEN 1st is #6-30) / DEN 1st (If #1-5) (If 2027 DEN 1st is #1-5 and 2028 DEN 1st is #6-30) -- *depends on a different pick's outcome (needs multi-year simulation)*

## Detroit Pistons

### 1st Round Picks (avg grade 6.24)

| Pick | Grade | Label |
|---|---|---|
| 2028 DET 1st | 7.2 | Good |
| 2027 DET 1st | 7.0 | Good |
| 2029 DET 1st | 6.6 | Good |
| 2031 DET 1st | 6.4 | Good |
| 2030 DET 1st | 5.5 | Above average |
| 2032 DET 1st | 5.5 | Above average |
| 2033 DET 1st | 5.5 | Above average |

### 2nd Round Picks (avg grade 1.00)

| Pick | Grade | Label |
|---|---|---|
| 2027 DET 2nd | 1.0 | Fringe / throw-in |
| 2030 DET 2nd | 1.0 | Fringe / throw-in |
| 2031 DAL 2nd | 1.0 | Fringe / throw-in |
| 2032 DET 2nd | 1.0 | Fringe / throw-in |
| 2033 DET 2nd | 1.0 | Fringe / throw-in |
| 2029 DET/MIL/NYK 2nd (most favorable, swap-resolved) | 1.0 | Fringe / throw-in |
| 2029 DET/MIL/NYK 2nd (rank 2 of 3, swap-resolved) | 1.0 | Fringe / throw-in |
| 2031 GS/MIN 2nd (least favorable, swap-resolved) | 1.0 | Fringe / throw-in |

**Unresolved (3):**
- 2028: (CHA/LAC (Less Favorable))/DET (If #31-55)/MIA 2nd (If 2027 DAL 1st is #3-30)/NYK (Most Favorable) 2nd (If #31-55) -- *depends on a different pick's outcome (needs multi-year simulation)*
- 2028: (CHA/LAC (Less Favorable))/DET (If #31-55)/MIA 2nd (If 2027 DAL 1st is #3-30)/NYK (2nd Favorable) 2nd -- *depends on a different pick's outcome (needs multi-year simulation)*
- 2028: (CHA/LAC (Less Favorable))/DET (If #31-55)/MIA 2nd (If 2027 DAL 1st is #3-30)/NYK (3rd Favorable) 2nd -- *depends on a different pick's outcome (needs multi-year simulation)*

## Golden State Warriors

### 1st Round Picks (avg grade 6.80)

| Pick | Grade | Label |
|---|---|---|
| 2028 GS 1st | 8.9 | Great |
| 2027 GS 1st | 8.6 | Great |
| 2029 GS 1st | 8.6 | Great |
| 2031 GS 1st | 8.2 | Great |
| 2032 GS 1st | 7.9 | Great |
| 2030 GS 1st (protected, doesn't convey #21-30) | 5.7 | Above average |
| 2033 GS 1st | 5.5 | Above average |
| 2030 GS 2nd (conveys only if GS 1st is #21-30, conditional-resolved) | 1.0 | Fringe / throw-in |

### 2nd Round Picks (avg grade 1.00)

| Pick | Grade | Label |
|---|---|---|
| 2032 GS 2nd (protected, doesn't convey #51-60) | 1.0 | Fringe / throw-in |
| 2033 GS 2nd | 1.0 | Fringe / throw-in |

## Houston Rockets

### 1st Round Picks (avg grade 7.83)

| Pick | Grade | Label |
|---|---|---|
| 2029 DAL/HOU/PHX 1st (most favorable, swap-resolved) | 9.4 | Elite |
| 2027 BKN/HOU 1st (most favorable, swap-resolved) | 9.2 | Elite |
| 2027 PHX 1st | 8.9 | Great |
| 2028 HOU 1st | 8.1 | Great |
| 2031 HOU 1st | 7.9 | Great |
| 2030 HOU 1st | 7.8 | Great |
| 2029 DAL/HOU/PHX 1st (rank 2 of 3, swap-resolved) | 7.6 | Great |
| 2032 HOU 1st | 6.1 | Good |
| 2033 HOU 1st | 5.5 | Above average |

### 2nd Round Picks (avg grade 1.00)

| Pick | Grade | Label |
|---|---|---|
| 2027 NO/POR 2nd (least favorable, swap-resolved) | 1.0 | Fringe / throw-in |
| 2031 ATL/HOU 2nd (least favorable, swap-resolved) | 1.0 | Fringe / throw-in |

## Indiana Pacers

### 1st Round Picks (avg grade 7.65)

| Pick | Grade | Label |
|---|---|---|
| 2028 IND 1st | 8.9 | Great |
| 2027 IND 1st | 8.6 | Great |
| 2031 IND 1st | 8.2 | Great |
| 2032 IND 1st | 7.5 | Great |
| 2030 IND 1st | 7.2 | Good |
| 2033 IND 1st | 5.5 | Above average |

### 2nd Round Picks (avg grade 1.30)

| Pick | Grade | Label |
|---|---|---|
| 2027 UTA 2nd | 3.1 | Below average |
| 2032 IND 2nd | 1.0 | Fringe / throw-in |
| 2033 IND 2nd | 1.0 | Fringe / throw-in |
| 2029 IND/WAS 2nd (least favorable, swap-resolved) | 1.0 | Fringe / throw-in |
| 2030 CHI/IND 2nd (least favorable, swap-resolved) | 1.0 | Fringe / throw-in |
| 2031 IND/MEM/MIA 2nd (least favorable, swap-resolved) | 1.0 | Fringe / throw-in |
| 2028 CHI/(IND/PHX More Favorable) (Less Favorable) 2nd (nested swap-resolved) | 1.0 | Fringe / throw-in |

## Los Angeles Clippers

### 1st Round Picks (avg grade 7.35)

| Pick | Grade | Label |
|---|---|---|
| 2033 LAC 1st | 8.9 | Great |
| 2030 LAC 1st | 8.8 | Great |
| 2029 IND 1st | 8.3 | Great |
| 2031 LAC 1st | 7.9 | Great |
| 2033 TOR 1st | 7.0 | Good |
| 2032 LAC 1st | 6.6 | Good |
| 2029 TOR 1st | 5.8 | Above average |
| 2031 TOR 1st | 5.5 | Above average |

### 2nd Round Picks (avg grade 1.23)

| Pick | Grade | Label |
|---|---|---|
| 2027 (GS/PHX More Favorable)/(HOU/IND/MIA/OKC Most Favorable)/PHI (2nd Most Favorable) 2nd (nested swap-resolved) | 2.6 | Below average |
| 2028 DAL 2nd | 1.0 | Fringe / throw-in |
| 2030 TOR 2nd | 1.0 | Fringe / throw-in |
| 2031 LAC 2nd | 1.0 | Fringe / throw-in |
| 2032 LAC 2nd | 1.0 | Fringe / throw-in |
| 2033 LAC 2nd | 1.0 | Fringe / throw-in |
| 2033 TOR 2nd | 1.0 | Fringe / throw-in |

**Unresolved (3):**
- 2027: (DEN (If #6-30)/LAC/OKC (Least Favorable))/TOR (More Favorable) 1st -- *nested parens or a continuation fragment -- needs manual resolution*
- 2028: (CHA/LAC (Less Favorable))/MIA 2nd (If 2027 DAL 1st is #3-30)/NYK (Most Favorable) 2nd (If #56-60) -- *depends on a different pick's outcome (needs multi-year simulation)*
- 2029: LAC 1st (If #1-3) / LAC (If #4-30)/PHI (Less Favorable) 1st -- *nested parens or a continuation fragment -- needs manual resolution*

## Los Angeles Lakers

### 1st Round Picks (avg grade 4.42)

| Pick | Grade | Label |
|---|---|---|
| 2028 (CLE/UTA More Favorable)/LAL (Less Favorable) 1st (nested swap-resolved) | 5.7 | Above average |
| 2032 LAL 1st | 5.5 | Above average |
| 2030 LAL/UTA 1st (least favorable, swap-resolved) | 5.5 | Above average |
| 2027 LAL 1st (protected, doesn't convey #5-30) | 1.0 | Fringe / throw-in |

### 2nd Round Picks (avg grade 1.00)

| Pick | Grade | Label |
|---|---|---|
| 2031 WAS 2nd | 1.0 | Fringe / throw-in |
| 2032 WAS 2nd | 1.0 | Fringe / throw-in |
| 2033 LAL 2nd | 1.0 | Fringe / throw-in |

## Memphis Grizzlies

### 1st Round Picks (avg grade 6.16)

| Pick | Grade | Label |
|---|---|---|
| 2027 MEM 1st | 9.2 | Elite |
| 2032 MEM 1st | 8.9 | Great |
| 2027 CLE/MIN/UTA 1st (most favorable, swap-resolved) | 8.8 | Great |
| 2030 MEM/(PHX/WAS Less Favorable) (More Favorable) 1st (nested swap-resolved) | 8.6 | Great |
| 2033 MEM 1st | 8.5 | Great |
| 2028 MEM 1st | 8.3 | Great |
| 2031 PHX 1st | 8.2 | Great |
| 2030 ORL 1st | 8.1 | Great |
| 2031 MEM 1st | 6.9 | Good |
| 2027 LAL 1st (protected, doesn't convey #1-4) | 6.7 | Good |
| 2030 GS 1st (protected, doesn't convey #1-20) | 1.0 | Fringe / throw-in |
| 2027 LAL 2nd (conveys only if LAL 1st is #1-4, conditional-resolved) | 1.0 | Fringe / throw-in |
| 2029 ORL 2nd (conveys only if ORL 1st is #1-2, conditional-resolved) | 1.0 | Fringe / throw-in |
| 2030 GS 2nd (conveys only if GS 1st is #1-20, conditional-resolved) | 1.0 | Fringe / throw-in |

### 2nd Round Picks (avg grade 1.00)

| Pick | Grade | Label |
|---|---|---|
| 2029 HOU 2nd | 1.0 | Fringe / throw-in |
| 2029 LAL 2nd | 1.0 | Fringe / throw-in |
| 2029 POR 2nd | 1.0 | Fringe / throw-in |
| 2030 MEM 2nd (protected, doesn't convey #51-60) | 1.0 | Fringe / throw-in |
| 2032 GS 2nd (protected, doesn't convey #31-50) | 1.0 | Fringe / throw-in |
| 2033 MEM 2nd | 1.0 | Fringe / throw-in |
| 2033 OKC 2nd | 1.0 | Fringe / throw-in |
| 2033 WAS 2nd | 1.0 | Fringe / throw-in |
| 2030 DEN/HOU/MIA 2nd (most favorable, swap-resolved) | 1.0 | Fringe / throw-in |
| 2032 MEM/PHI/UTA 2nd (most favorable, swap-resolved) | 1.0 | Fringe / throw-in |
| 2031 (IND/MIA Less Favorable)/MEM (More Favorable) 2nd (nested swap-resolved) | 1.0 | Fringe / throw-in |

**Unresolved (1):**
- 2029: MEM/ORL (If #3-30) (More Favorable) 1st -- *nested parens or a continuation fragment -- needs manual resolution*

## Miami Heat

### 1st Round Picks (avg grade 6.78)

| Pick | Grade | Label |
|---|---|---|
| 2029 MIA 1st | 8.3 | Great |
| 2032 MIA 1st | 7.9 | Great |
| 2028 MIA 1st (conveys only if 2027 MIA 1st is #15-30, cross-year-conditional-resolved) | 6.7 | Good |
| 2027 MIA 1st (protected, doesn't convey #15-30) | 5.5 | Above average |
| 2030 MIA/MIL/POR 1st (least favorable, swap-resolved) | 5.5 | Above average |

### 2nd Round Picks (avg grade 1.00)

| Pick | Grade | Label |
|---|---|---|
| 2027 HOU/IND/MIA/OKC/SA 2nd (least favorable, swap-resolved) | 1.0 | Fringe / throw-in |

## Milwaukee Bucks

### 1st Round Picks (avg grade 7.50)

| Pick | Grade | Label |
|---|---|---|
| 2030 MIA/(MIL/POR Less Favorable) (More Favorable) 1st (nested swap-resolved) | 8.5 | Great |
| 2031 MIL 1st | 8.2 | Great |
| 2032 MIL 1st | 7.8 | Great |
| 2031 MIA 1st | 7.6 | Great |
| 2033 MIL 1st | 6.7 | Good |
| 2033 MIA 1st | 6.2 | Good |

### 2nd Round Picks (avg grade 1.82)

| Pick | Grade | Label |
|---|---|---|
| 2027 MIL 2nd | 3.0 | Below average |
| 2027 BKN/DAL 2nd (least favorable, swap-resolved) | 2.3 | Weak |
| 2033 MIA 2nd | 1.0 | Fringe / throw-in |
| 2033 MIL 2nd | 1.0 | Fringe / throw-in |

**Unresolved (1):**
- 2028: ((BKN/PHI (If #9-30)/PHX (Least Favorable)/WAS (More Favorable))/MIL/POR (Least Favorable) 1st -- *nested parens or a continuation fragment -- needs manual resolution*

## Minnesota Timberwolves

### 1st Round Picks (avg grade 5.50)

| Pick | Grade | Label |
|---|---|---|
| 2032 MIN 1st | 5.5 | Above average |
| 2028 CHA/MIN 1st (least favorable, swap-resolved) | 5.5 | Above average |
| 2030 CHA/(DAL/SA More Favorable)/MIN (Least Favorable) 1st (nested swap-resolved) | 5.5 | Above average |

### 2nd Round Picks (avg grade 1.00)

| Pick | Grade | Label |
|---|---|---|
| 2030 MEM 2nd (protected, doesn't convey #31-50) | 1.0 | Fringe / throw-in |

**Unresolved (1):**
- 2029: CHA/MIN (Less Favorable) 1st (If #2-5) -- *nested parens or a continuation fragment -- needs manual resolution*

## New Orleans Pelicans

### 1st Round Picks (avg grade 7.44)

| Pick | Grade | Label |
|---|---|---|
| 2027 MIL/NO 1st (most favorable, swap-resolved) | 9.5 | Elite |
| 2033 NO 1st | 8.9 | Great |
| 2028 NO 1st | 8.8 | Great |
| 2030 NO 1st | 8.8 | Great |
| 2029 NO 1st | 7.9 | Great |
| 2031 NO 1st | 7.9 | Great |
| 2032 NO 1st | 6.7 | Good |
| 2027 MIL/NO 1st (least favorable, swap-resolved) | 1.0 | Fringe / throw-in |

### 2nd Round Picks (avg grade 1.06)

| Pick | Grade | Label |
|---|---|---|
| 2027 HOU/IND/MIA/OKC 2nd (rank 2 of 4, swap-resolved) | 1.3 | Fringe / throw-in |
| 2031 TOR 2nd | 1.0 | Fringe / throw-in |
| 2032 NO 2nd | 1.0 | Fringe / throw-in |
| 2033 NO 2nd | 1.0 | Fringe / throw-in |
| 2030 NO/ORL 2nd (least favorable, swap-resolved) | 1.0 | Fringe / throw-in |

## New York Knicks

### 1st Round Picks (avg grade 6.55)

| Pick | Grade | Label |
|---|---|---|
| 2030 NYK 1st | 8.5 | Great |
| 2028 BKN/NYK 1st (least favorable, swap-resolved) | 6.7 | Good |
| 2032 NYK 1st | 5.5 | Above average |
| 2033 NYK 1st | 5.5 | Above average |

### 2nd Round Picks (avg grade 1.17)

| Pick | Grade | Label |
|---|---|---|
| 2027 WAS 2nd | 3.0 | Below average |
| 2027 NYK 2nd | 1.0 | Fringe / throw-in |
| 2028 BOS 2nd (protected, doesn't convey #31-45) | 1.0 | Fringe / throw-in |
| 2029 PHX 2nd | 1.0 | Fringe / throw-in |
| 2029 SAC 2nd | 1.0 | Fringe / throw-in |
| 2030 PHI 2nd | 1.0 | Fringe / throw-in |
| 2032 DAL 2nd | 1.0 | Fringe / throw-in |
| 2032 NYK 2nd | 1.0 | Fringe / throw-in |
| 2033 NYK 2nd | 1.0 | Fringe / throw-in |
| 2033 PHX 2nd | 1.0 | Fringe / throw-in |
| 2027 HOU/IND/MIA/OKC 2nd (rank 3 of 4, swap-resolved) | 1.0 | Fringe / throw-in |
| 2028 IND/PHX 2nd (least favorable, swap-resolved) | 1.0 | Fringe / throw-in |

## Oklahoma City Thunder

### 1st Round Picks (avg grade 4.90)

| Pick | Grade | Label |
|---|---|---|
| 2028 DAL/OKC 1st (most favorable, swap-resolved) | 9.1 | Elite |
| 2027 SA 1st (protected, doesn't convey #1-16) | 5.5 | Above average |
| 2029 OKC 1st | 5.5 | Above average |
| 2030 OKC 1st | 5.5 | Above average |
| 2031 OKC 1st | 5.5 | Above average |
| 2032 OKC 1st | 5.5 | Above average |
| 2033 OKC 1st | 5.5 | Above average |
| 2027 CHA 2nd (conveys only if SA 1st is #1-16, conditional-resolved) | 1.0 | Fringe / throw-in |
| 2027 SAC 2nd (conveys only if SA 1st is #1-16, conditional-resolved) | 1.0 | Fringe / throw-in |

### 2nd Round Picks (avg grade 1.12)

| Pick | Grade | Label |
|---|---|---|
| 2027 CHI 2nd | 3.0 | Below average |
| 2028 UTA 2nd | 1.0 | Fringe / throw-in |
| 2029 ATL 2nd | 1.0 | Fringe / throw-in |
| 2029 BOS 2nd | 1.0 | Fringe / throw-in |
| 2029 MIA 2nd | 1.0 | Fringe / throw-in |
| 2029 OKC 2nd | 1.0 | Fringe / throw-in |
| 2030 ATL 2nd | 1.0 | Fringe / throw-in |
| 2030 MIN 2nd | 1.0 | Fringe / throw-in |
| 2030 OKC 2nd | 1.0 | Fringe / throw-in |
| 2031 DET 2nd | 1.0 | Fringe / throw-in |
| 2031 OKC 2nd | 1.0 | Fringe / throw-in |
| 2032 ATL 2nd | 1.0 | Fringe / throw-in |
| 2032 LAL 2nd | 1.0 | Fringe / throw-in |
| 2032 OKC 2nd | 1.0 | Fringe / throw-in |
| 2030 DEN/HOU/MIA 2nd (rank 2 of 3, swap-resolved) | 1.0 | Fringe / throw-in |
| 2030 DEN/HOU/MIA 2nd (least favorable, swap-resolved) | 1.0 | Fringe / throw-in |
| 2031 NO/ORL 2nd (least favorable, swap-resolved) | 1.0 | Fringe / throw-in |

**Unresolved (6):**
- 2027: DEN 1st (If #6-30)/LAC/OKC (Most Favorable) 1st -- *nested parens or a continuation fragment -- needs manual resolution*
- 2027: DEN 1st (If #6-30)/LAC/OKC (2nd Most Favorable) 1st -- *nested parens or a continuation fragment -- needs manual resolution*
- 2028: DEN 1st (If #6-30, If 2027 DEN 1st is #1-5) -- *doesn't match any known pattern*
- 2029: DEN 1st (If #6-30, 2027 DEN 1st is #1-5 and 2028 DEN 1st is #1-5) / DEN 1st (If #6-30) (If 2027 DEN 1st is #6-30) -- *depends on a different pick's outcome (needs multi-year simulation)*
- 2030: DEN 1st (If #6-30 and 2029 DEN 1st is #1-5) (If 2027 DEN 1st is #6-30) / DEN 1st (If #6-30) (If 2027 DEN 1st is #1-5 and 2028 DEN 1st is #6-30) -- *depends on a different pick's outcome (needs multi-year simulation)*
- 2031: ATL/(HOU (If #31-55)) (More Favorable) 2nd -- *nested parens or a continuation fragment -- needs manual resolution*

## Orlando Magic

### 1st Round Picks (avg grade 6.12)

| Pick | Grade | Label |
|---|---|---|
| 2027 ORL 1st | 8.6 | Great |
| 2033 ORL 1st | 7.8 | Great |
| 2031 ORL 1st | 7.5 | Great |
| 2032 ORL 1st | 5.7 | Above average |
| 2029 ORL 2nd (conveys only if ORL 1st is #3-30, conditional-resolved) | 1.0 | Fringe / throw-in |

### 2nd Round Picks (avg grade 1.10)

| Pick | Grade | Label |
|---|---|---|
| 2028 LAL/WAS 2nd (most favorable, swap-resolved) | 1.6 | Weak |
| 2030 MIL 2nd | 1.0 | Fringe / throw-in |
| 2032 ORL 2nd | 1.0 | Fringe / throw-in |
| 2033 ORL 2nd | 1.0 | Fringe / throw-in |
| 2030 NO/ORL 2nd (most favorable, swap-resolved) | 1.0 | Fringe / throw-in |
| 2031 NO/ORL 2nd (most favorable, swap-resolved) | 1.0 | Fringe / throw-in |

**Unresolved (1):**
- 2029: ORL 1st (If #1-2) / MEM/ORL (If #3-30) (Less Favorable) 1st -- *nested parens or a continuation fragment -- needs manual resolution*

## Philadelphia 76ers

### 1st Round Picks (avg grade 5.48)

| Pick | Grade | Label |
|---|---|---|
| 2030 PHI 1st | 8.5 | Great |
| 2027 PHI 1st | 6.9 | Good |
| 2032 PHI 1st | 5.5 | Above average |
| 2033 PHI 1st | 5.5 | Above average |
| 2028 PHI 2nd (conveys only if PHI 1st is #9-30, conditional-resolved) | 1.0 | Fringe / throw-in |

### 2nd Round Picks (avg grade 1.30)

| Pick | Grade | Label |
|---|---|---|
| 2027 (GS/PHX More Favorable)/(HOU/IND/MIA/OKC Most Favorable)/PHI (Most Favorable) 2nd (nested swap-resolved) | 4.0 | Average |
| 2028 DET 2nd (protected, doesn't convey #31-55) | 1.0 | Fringe / throw-in |
| 2029 PHI 2nd | 1.0 | Fringe / throw-in |
| 2031 PHI 2nd | 1.0 | Fringe / throw-in |
| 2033 PHI 2nd | 1.0 | Fringe / throw-in |
| 2028 GS/MIL/OKC 2nd (rank 2 of 3, swap-resolved) | 1.0 | Fringe / throw-in |
| 2028 GS/MIL/OKC 2nd (least favorable, swap-resolved) | 1.0 | Fringe / throw-in |
| 2032 MEM/PHI 2nd (least favorable, swap-resolved) | 1.0 | Fringe / throw-in |
| 2027 (GS/PHX More Favorable)/(HOU/IND/MIA/OKC Most Favorable)/PHI (Least Favorable) 2nd (nested swap-resolved) | 1.0 | Fringe / throw-in |
| 2030 (PHX/POR More Favorable)/WAS (Less Favorable) 2nd (nested swap-resolved) | 1.0 | Fringe / throw-in |

**Unresolved (3):**
- 2028: (BOS (If #2-30)/SA (Less Favorable))/(LAC (If #1-16))/(PHI (If #1-8)) (2nd Most Favorable) 1st -- *nested parens or a continuation fragment -- needs manual resolution*
- 2028: (BOS (If #2-30)/SA (Less Favorable))/(LAC (If #17-30))/(PHI (If #1-8)) (Least Favorable) 1st (If 2028 PHI 1st is #1-8) -- *depends on a different pick's outcome (needs multi-year simulation)*
- 2029: LAC (If #4-30)/PHI (More Favorable) 1st -- *nested parens or a continuation fragment -- needs manual resolution*

## Phoenix Suns

### 1st Round Picks (avg grade 6.40)

| Pick | Grade | Label |
|---|---|---|
| 2032 PHX 1st | 7.9 | Great |
| 2027 CLE/MIN/UTA 1st (least favorable, swap-resolved) | 5.8 | Above average |
| 2030 MEM/PHX/WAS 1st (least favorable, swap-resolved) | 5.5 | Above average |

### 2nd Round Picks (avg grade 1.00)

| Pick | Grade | Label |
|---|---|---|
| 2027 BOS/ORL 2nd (least favorable, swap-resolved) | 1.0 | Fringe / throw-in |
| 2032 HOU/PHX 2nd (least favorable, swap-resolved) | 1.0 | Fringe / throw-in |

**Unresolved (2):**
- 2028: BKN/PHI (If #9-30)/PHX/WAS (Least Favorable) 1st -- *nested parens or a continuation fragment -- needs manual resolution*
- 2029: CLE/MIN (If #6-30)/UTA (Least Favorable) 1st -- *nested parens or a continuation fragment -- needs manual resolution*

## Portland Trail Blazers

### 1st Round Picks (avg grade 7.74)

| Pick | Grade | Label |
|---|---|---|
| 2028 MIL/POR 1st (most favorable, swap-resolved) | 9.2 | Elite |
| 2029 BOS/MIL/POR 1st (most favorable, swap-resolved) | 9.2 | Elite |
| 2030 MIL/POR 1st (most favorable, swap-resolved) | 8.5 | Great |
| 2027 POR 1st | 8.3 | Great |
| 2032 POR 1st | 8.3 | Great |
| 2028 ORL 1st | 8.2 | Great |
| 2031 POR 1st | 6.4 | Good |
| 2033 POR 1st | 6.1 | Good |
| 2029 BOS/MIL/POR 1st (least favorable, swap-resolved) | 5.5 | Above average |

### 2nd Round Picks (avg grade 1.06)

| Pick | Grade | Label |
|---|---|---|
| 2027 NO/POR 2nd (least favorable, swap-resolved) | 1.4 | Fringe / throw-in |
| 2028 SAC 2nd | 1.1 | Fringe / throw-in |
| 2027 MIN 2nd | 1.0 | Fringe / throw-in |
| 2028 POR 2nd | 1.0 | Fringe / throw-in |
| 2031 POR 2nd | 1.0 | Fringe / throw-in |
| 2032 POR 2nd | 1.0 | Fringe / throw-in |
| 2033 POR 2nd | 1.0 | Fringe / throw-in |
| 2029 IND/WAS 2nd (least favorable, swap-resolved) | 1.0 | Fringe / throw-in |

## Sacramento Kings

### 1st Round Picks (avg grade 6.60)

| Pick | Grade | Label |
|---|---|---|
| 2027 SAC 1st | 9.2 | Elite |
| 2028 SAC 1st | 9.1 | Elite |
| 2032 SAC 1st | 9.1 | Elite |
| 2029 SAC 1st | 8.9 | Great |
| 2030 SAC 1st | 8.5 | Great |
| 2033 SAC 1st | 8.3 | Great |
| 2031 MIN 1st | 7.0 | Good |
| 2031 SAC/SA 1st (least favorable, swap-resolved) | 5.5 | Above average |
| 2027 CHA 2nd (conveys only if SA 1st is #17-30, conditional-resolved) | 3.0 | Below average |
| 2027 SAC 2nd (conveys only if SA 1st is #17-30, conditional-resolved) | 3.0 | Below average |
| 2027 SA 1st (protected, doesn't convey #17-30) | 1.0 | Fringe / throw-in |

### 2nd Round Picks (none)

## San Antonio Spurs

### 1st Round Picks (avg grade 5.60)

| Pick | Grade | Label |
|---|---|---|
| 2027 ATL 1st | 8.6 | Great |
| 2031 SAC/SA 1st (most favorable, swap-resolved) | 7.5 | Great |
| 2029 SA 1st | 5.5 | Above average |
| 2032 SA 1st | 5.5 | Above average |
| 2033 SA 1st | 5.5 | Above average |
| 2028 BOS 2nd (conveys only if BOS 1st is #1-1, own protection (46, 60), conditional-resolved) | 1.0 | Fringe / throw-in |

### 2nd Round Picks (avg grade 1.00)

| Pick | Grade | Label |
|---|---|---|
| 2028 NO 2nd | 1.0 | Fringe / throw-in |
| 2028 SA 2nd | 1.0 | Fringe / throw-in |
| 2029 LAC 2nd | 1.0 | Fringe / throw-in |
| 2029 NO 2nd | 1.0 | Fringe / throw-in |
| 2029 SA 2nd | 1.0 | Fringe / throw-in |
| 2030 CLE 2nd | 1.0 | Fringe / throw-in |
| 2030 SAC 2nd | 1.0 | Fringe / throw-in |
| 2030 SA 2nd | 1.0 | Fringe / throw-in |
| 2031 SA 2nd | 1.0 | Fringe / throw-in |
| 2032 SA 2nd | 1.0 | Fringe / throw-in |
| 2033 SA 2nd | 1.0 | Fringe / throw-in |
| 2027 (HOU/IND/MIA/OKC Least Favorable)/SA (More Favorable) 2nd (nested swap-resolved) | 1.0 | Fringe / throw-in |

**Unresolved (2):**
- 2028: BOS (If #2-30)/SA (More Favorable) 1st -- *nested parens or a continuation fragment -- needs manual resolution*
- 2030: DAL/MIN (If #2-30)/SA (Most Favorable) 1st -- *nested parens or a continuation fragment -- needs manual resolution*

## Toronto Raptors

### 1st Round Picks (avg grade 5.90)

| Pick | Grade | Label |
|---|---|---|
| 2028 TOR 1st | 6.2 | Good |
| 2030 TOR 1st | 6.1 | Good |
| 2029 TOR 1st | 5.8 | Above average |
| 2032 TOR 1st | 5.5 | Above average |

### 2nd Round Picks (avg grade 1.30)

| Pick | Grade | Label |
|---|---|---|
| 2027 TOR 2nd | 1.9 | Weak |
| 2028 TOR 2nd | 1.0 | Fringe / throw-in |
| 2029 TOR 2nd | 1.0 | Fringe / throw-in |

**Unresolved (1):**
- 2027: DEN (If #6-30)/LAC/OKC/TOR (Least Favorable) 1st -- *nested parens or a continuation fragment -- needs manual resolution*

## Utah Jazz

### 1st Round Picks (avg grade 6.84)

| Pick | Grade | Label |
|---|---|---|
| 2028 CLE/LAL/UTA 1st (most favorable, swap-resolved) | 9.2 | Elite |
| 2031 UTA 1st | 8.5 | Great |
| 2030 LAL/UTA 1st (most favorable, swap-resolved) | 8.3 | Great |
| 2032 UTA 1st | 8.2 | Great |
| 2031 LAL 1st | 7.5 | Great |
| 2027 CLE/MIN/UTA 1st (rank 2 of 3, swap-resolved) | 7.2 | Good |
| 2033 UTA 1st | 6.2 | Good |
| 2033 LAL 1st | 5.5 | Above average |
| 2029 MIN 2nd (conveys only if MIN 1st is #1-5, conditional-resolved) | 1.0 | Fringe / throw-in |

### 2nd Round Picks (avg grade 1.35)

| Pick | Grade | Label |
|---|---|---|
| 2027 LAC 2nd | 3.0 | Below average |
| 2027 BOS/ORL 2nd (most favorable, swap-resolved) | 2.5 | Below average |
| 2027 DEN 2nd | 1.0 | Fringe / throw-in |
| 2028 CLE 2nd | 1.0 | Fringe / throw-in |
| 2029 UTA 2nd | 1.0 | Fringe / throw-in |
| 2032 CLE 2nd | 1.0 | Fringe / throw-in |
| 2033 UTA 2nd | 1.0 | Fringe / throw-in |
| 2030 LAC/UTA 2nd (least favorable, swap-resolved) | 1.0 | Fringe / throw-in |
| 2031 BOS/CLE 2nd (most favorable, swap-resolved) | 1.0 | Fringe / throw-in |
| 2031 (IND/MIA More Favorable)/UTA (Less Favorable) 2nd (nested swap-resolved) | 1.0 | Fringe / throw-in |

**Unresolved (3):**
- 2028: (CHA/LAC (Less Favorable))/DET (If #31-55)/MIA (If 2027 DAL 1st is #3-30)/NYK (Least Favorable) 2nd -- *depends on a different pick's outcome (needs multi-year simulation)*
- 2029: CLE /MIN (If #6-30)/UTA (Most Favorable) 1st -- *nested parens or a continuation fragment -- needs manual resolution*
- 2029: CLE/MIN (#If #6-30)/UTA (2nd Favorable) 1st -- *nested parens or a continuation fragment -- needs manual resolution*

## Washington Wizards

### 1st Round Picks (avg grade 8.40)

| Pick | Grade | Label |
|---|---|---|
| 2027 WAS 1st | 9.1 | Elite |
| 2029 WAS 1st | 9.1 | Elite |
| 2030 PHX/WAS 1st (most favorable, swap-resolved) | 9.1 | Elite |
| 2033 WAS 1st | 8.9 | Great |
| 2031 WAS 1st | 8.2 | Great |
| 2029 BOS/MIL/POR 1st (rank 2 of 3, swap-resolved) | 7.5 | Great |
| 2032 WAS 1st | 6.9 | Good |

### 2nd Round Picks (avg grade 1.52)

| Pick | Grade | Label |
|---|---|---|
| 2027 BKN/DAL 2nd (most favorable, swap-resolved) | 3.5 | Below average |
| 2027 GS/PHX 2nd (least favorable, swap-resolved) | 1.6 | Weak |
| 2033 DAL 2nd | 1.0 | Fringe / throw-in |
| 2030 PHX/POR 2nd (least favorable, swap-resolved) | 1.0 | Fringe / throw-in |
| 2031 IND/MIA/UTA 2nd (most favorable, swap-resolved) | 1.0 | Fringe / throw-in |
| 2032 (MEM/PHI More Favorable)/UTA (Less Favorable) 2nd (nested swap-resolved) | 1.0 | Fringe / throw-in |

**Unresolved (1):**
- 2028: (BKN/PHI (If #9-30)/PHX (Least Favorable))/(MIL/POR (Less Favorable)/WAS (Most Favorable), DEN 2nd (If #34-60), LAL/WAS (Less Favorable) 2nd -- *nested parens or a continuation fragment -- needs manual resolution*
