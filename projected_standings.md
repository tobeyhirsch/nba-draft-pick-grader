# Projected Standings -- Underlying the Pick Value Projections

Average simulated wins per team per season (2000 trials each), for the SAME ratings that drive every pick distribution/grade in /Users/tobeyhirsch/Desktop/NBA Draft Pick Model/nba-draft-pick-grader/league_pick_grades.md: real 2026-27 market ratings for 2027, DARKO+longevity-evolved ratings (darko_ratings.py) for 2028-2032, and the flat 2027 market ratings again for 2033 (outside darko_ratings.py's window -- see its module docstring for why the window stops where it does). These are regular-season win projections only -- no play-in/lottery/draft-order logic runs here, that all happens downstream in draft_pipeline_321.py using these same ratings.

## 2026-27 season (feeds the 2027 draft)

### East

| Rank | Team | Avg W | Avg L | GB |
|---|---|---|---|---|
| 1 | New York Knicks | 52.1 | 29.9 | 0.0 |
| 2 | Boston Celtics | 50.5 | 31.5 | 1.6 |
| 3 | Philadelphia 76ers | 50.0 | 32.0 | 2.1 |
| 4 | Detroit Pistons | 49.1 | 32.9 | 3.0 |
| 5 | Cleveland Cavaliers | 47.6 | 34.4 | 4.5 |
| 6 | Miami Heat | 45.4 | 36.6 | 6.7 |
| 7 | Toronto Raptors | 45.1 | 36.9 | 7.1 |
| 8 | Indiana Pacers | 43.8 | 38.2 | 8.3 |
| 9 | Orlando Magic | 43.4 | 38.6 | 8.7 |
| 10 | Atlanta Hawks | 43.2 | 38.8 | 8.9 |
| 11 | Charlotte Hornets | 38.8 | 43.2 | 13.3 |
| 12 | Washington Wizards | 35.3 | 46.7 | 16.8 |
| 13 | Chicago Bulls | 28.3 | 53.7 | 23.9 |
| 14 | Milwaukee Bucks | 25.3 | 56.7 | 26.8 |
| 15 | Brooklyn Nets | 24.0 | 58.0 | 28.1 |

### West

| Rank | Team | Avg W | Avg L | GB |
|---|---|---|---|---|
| 1 | Oklahoma City Thunder | 61.1 | 20.9 | 0.0 |
| 2 | San Antonio Spurs | 60.1 | 21.9 | 1.0 |
| 3 | Denver Nuggets | 48.7 | 33.3 | 12.4 |
| 4 | Minnesota Timberwolves | 47.6 | 34.4 | 13.5 |
| 5 | Houston Rockets | 47.0 | 35.0 | 14.1 |
| 6 | Los Angeles Lakers | 44.9 | 37.1 | 16.1 |
| 7 | Portland Trail Blazers | 41.9 | 40.1 | 19.2 |
| 8 | Golden State Warriors | 40.1 | 41.9 | 21.0 |
| 9 | Phoenix Suns | 38.9 | 43.1 | 22.1 |
| 10 | Utah Jazz | 36.3 | 45.7 | 24.7 |
| 11 | Dallas Mavericks | 33.7 | 48.3 | 27.4 |
| 12 | Los Angeles Clippers | 30.1 | 51.9 | 31.0 |
| 13 | Memphis Grizzlies | 28.5 | 53.5 | 32.6 |
| 14 | New Orleans Pelicans | 27.9 | 54.1 | 33.2 |
| 15 | Sacramento Kings | 21.2 | 60.8 | 39.9 |

## 2027-28 season (feeds the 2028 draft)

### East

| Rank | Team | Avg W | Avg L | GB |
|---|---|---|---|---|
| 1 | Toronto Raptors | 46.9 | 35.1 | 0.0 |
| 2 | Boston Celtics | 45.1 | 36.9 | 1.8 |
| 3 | Detroit Pistons | 44.8 | 37.2 | 2.1 |
| 4 | Cleveland Cavaliers | 44.0 | 38.0 | 2.8 |
| 5 | New York Knicks | 43.5 | 38.5 | 3.4 |
| 6 | Orlando Magic | 42.5 | 39.5 | 4.4 |
| 7 | Philadelphia 76ers | 42.2 | 39.8 | 4.7 |
| 8 | Atlanta Hawks | 41.6 | 40.4 | 5.3 |
| 9 | Miami Heat | 41.5 | 40.5 | 5.4 |
| 10 | Indiana Pacers | 39.2 | 42.8 | 7.7 |
| 11 | Chicago Bulls | 38.4 | 43.6 | 8.4 |
| 12 | Milwaukee Bucks | 38.2 | 43.8 | 8.7 |
| 13 | Charlotte Hornets | 37.4 | 44.6 | 9.4 |
| 14 | Brooklyn Nets | 34.3 | 47.7 | 12.5 |
| 15 | Washington Wizards | 32.8 | 49.2 | 14.1 |

### West

| Rank | Team | Avg W | Avg L | GB |
|---|---|---|---|---|
| 1 | Oklahoma City Thunder | 52.6 | 29.4 | 0.0 |
| 2 | San Antonio Spurs | 48.6 | 33.4 | 4.0 |
| 3 | Minnesota Timberwolves | 46.7 | 35.3 | 5.9 |
| 4 | Los Angeles Lakers | 46.3 | 35.7 | 6.4 |
| 5 | Denver Nuggets | 46.0 | 36.0 | 6.7 |
| 6 | Houston Rockets | 42.4 | 39.6 | 10.3 |
| 7 | Portland Trail Blazers | 41.0 | 41.0 | 11.7 |
| 8 | Phoenix Suns | 38.6 | 43.4 | 14.0 |
| 9 | New Orleans Pelicans | 38.4 | 43.6 | 14.3 |
| 10 | Golden State Warriors | 38.1 | 43.9 | 14.6 |
| 11 | Dallas Mavericks | 37.4 | 44.6 | 15.3 |
| 12 | Utah Jazz | 36.1 | 45.9 | 16.6 |
| 13 | Los Angeles Clippers | 36.0 | 46.0 | 16.6 |
| 14 | Memphis Grizzlies | 35.2 | 46.8 | 17.4 |
| 15 | Sacramento Kings | 34.5 | 47.5 | 18.2 |

## 2028-29 season (feeds the 2029 draft)

### East

| Rank | Team | Avg W | Avg L | GB |
|---|---|---|---|---|
| 1 | Toronto Raptors | 46.5 | 35.5 | 0.0 |
| 2 | Cleveland Cavaliers | 45.1 | 36.9 | 1.4 |
| 3 | Detroit Pistons | 45.1 | 36.9 | 1.4 |
| 4 | Boston Celtics | 43.1 | 38.9 | 3.4 |
| 5 | Philadelphia 76ers | 42.6 | 39.4 | 3.9 |
| 6 | Orlando Magic | 42.3 | 39.7 | 4.2 |
| 7 | Atlanta Hawks | 41.4 | 40.6 | 5.1 |
| 8 | New York Knicks | 41.1 | 40.9 | 5.4 |
| 9 | Indiana Pacers | 40.2 | 41.8 | 6.3 |
| 10 | Miami Heat | 40.0 | 42.0 | 6.5 |
| 11 | Chicago Bulls | 39.6 | 42.4 | 6.9 |
| 12 | Milwaukee Bucks | 38.7 | 43.3 | 7.8 |
| 13 | Charlotte Hornets | 38.3 | 43.7 | 8.2 |
| 14 | Brooklyn Nets | 34.6 | 47.4 | 11.9 |
| 15 | Washington Wizards | 34.2 | 47.8 | 12.3 |

### West

| Rank | Team | Avg W | Avg L | GB |
|---|---|---|---|---|
| 1 | Oklahoma City Thunder | 51.8 | 30.2 | 0.0 |
| 2 | San Antonio Spurs | 48.2 | 33.8 | 3.6 |
| 3 | Minnesota Timberwolves | 46.3 | 35.7 | 5.5 |
| 4 | Los Angeles Lakers | 44.7 | 37.3 | 7.1 |
| 5 | Denver Nuggets | 43.3 | 38.7 | 8.5 |
| 6 | Houston Rockets | 42.2 | 39.8 | 9.6 |
| 7 | Phoenix Suns | 39.2 | 42.8 | 12.6 |
| 8 | Portland Trail Blazers | 39.2 | 42.8 | 12.6 |
| 9 | Dallas Mavericks | 38.5 | 43.5 | 13.3 |
| 10 | Golden State Warriors | 38.4 | 43.6 | 13.4 |
| 11 | New Orleans Pelicans | 38.0 | 44.0 | 13.8 |
| 12 | Los Angeles Clippers | 37.4 | 44.6 | 14.4 |
| 13 | Utah Jazz | 37.2 | 44.8 | 14.6 |
| 14 | Sacramento Kings | 36.6 | 45.4 | 15.2 |
| 15 | Memphis Grizzlies | 36.2 | 45.8 | 15.6 |

## 2029-30 season (feeds the 2030 draft)

### East

| Rank | Team | Avg W | Avg L | GB |
|---|---|---|---|---|
| 1 | Detroit Pistons | 45.7 | 36.3 | 0.0 |
| 2 | Toronto Raptors | 45.1 | 36.9 | 0.7 |
| 3 | Cleveland Cavaliers | 44.6 | 37.4 | 1.2 |
| 4 | Orlando Magic | 42.0 | 40.0 | 3.7 |
| 5 | Boston Celtics | 41.6 | 40.4 | 4.1 |
| 6 | Atlanta Hawks | 41.6 | 40.4 | 4.1 |
| 7 | Miami Heat | 40.1 | 41.9 | 5.6 |
| 8 | Philadelphia 76ers | 39.9 | 42.1 | 5.8 |
| 9 | New York Knicks | 39.9 | 42.1 | 5.8 |
| 10 | Indiana Pacers | 39.7 | 42.3 | 6.0 |
| 11 | Charlotte Hornets | 39.5 | 42.5 | 6.2 |
| 12 | Chicago Bulls | 39.4 | 42.6 | 6.3 |
| 13 | Milwaukee Bucks | 39.4 | 42.6 | 6.4 |
| 14 | Brooklyn Nets | 37.7 | 44.3 | 8.0 |
| 15 | Washington Wizards | 37.4 | 44.6 | 8.3 |

### West

| Rank | Team | Avg W | Avg L | GB |
|---|---|---|---|---|
| 1 | Oklahoma City Thunder | 51.3 | 30.7 | 0.0 |
| 2 | San Antonio Spurs | 46.8 | 35.2 | 4.5 |
| 3 | Houston Rockets | 42.4 | 39.6 | 8.9 |
| 4 | Los Angeles Lakers | 42.2 | 39.8 | 9.1 |
| 5 | Denver Nuggets | 41.9 | 40.1 | 9.5 |
| 6 | Minnesota Timberwolves | 41.4 | 40.6 | 9.9 |
| 7 | Phoenix Suns | 39.9 | 42.1 | 11.4 |
| 8 | Portland Trail Blazers | 39.5 | 42.5 | 11.8 |
| 9 | Golden State Warriors | 39.3 | 42.7 | 12.0 |
| 10 | Dallas Mavericks | 39.3 | 42.7 | 12.1 |
| 11 | New Orleans Pelicans | 38.8 | 43.2 | 12.6 |
| 12 | Los Angeles Clippers | 38.6 | 43.4 | 12.8 |
| 13 | Utah Jazz | 38.3 | 43.7 | 13.0 |
| 14 | Memphis Grizzlies | 38.3 | 43.7 | 13.1 |
| 15 | Sacramento Kings | 38.3 | 43.7 | 13.1 |

## 2030-31 season (feeds the 2031 draft)

### East

| Rank | Team | Avg W | Avg L | GB |
|---|---|---|---|---|
| 1 | Toronto Raptors | 45.0 | 37.0 | 0.0 |
| 2 | Detroit Pistons | 43.4 | 38.6 | 1.6 |
| 3 | Cleveland Cavaliers | 43.3 | 38.7 | 1.7 |
| 4 | Boston Celtics | 41.1 | 40.9 | 3.9 |
| 5 | Orlando Magic | 40.8 | 41.2 | 4.2 |
| 6 | New York Knicks | 40.8 | 41.2 | 4.2 |
| 7 | Philadelphia 76ers | 40.6 | 41.4 | 4.3 |
| 8 | Miami Heat | 40.5 | 41.5 | 4.4 |
| 9 | Atlanta Hawks | 40.4 | 41.6 | 4.6 |
| 10 | Indiana Pacers | 40.3 | 41.7 | 4.7 |
| 11 | Charlotte Hornets | 40.0 | 42.0 | 5.0 |
| 12 | Milwaukee Bucks | 39.9 | 42.1 | 5.0 |
| 13 | Chicago Bulls | 39.9 | 42.1 | 5.1 |
| 14 | Brooklyn Nets | 38.4 | 43.6 | 6.6 |
| 15 | Washington Wizards | 38.4 | 43.6 | 6.6 |

### West

| Rank | Team | Avg W | Avg L | GB |
|---|---|---|---|---|
| 1 | Oklahoma City Thunder | 48.0 | 34.0 | 0.0 |
| 2 | San Antonio Spurs | 46.3 | 35.7 | 1.6 |
| 3 | Denver Nuggets | 42.2 | 39.8 | 5.8 |
| 4 | Los Angeles Lakers | 42.0 | 40.0 | 6.0 |
| 5 | Minnesota Timberwolves | 41.8 | 40.2 | 6.2 |
| 6 | Houston Rockets | 41.1 | 40.9 | 6.9 |
| 7 | Portland Trail Blazers | 40.3 | 41.7 | 7.7 |
| 8 | Dallas Mavericks | 40.0 | 42.0 | 8.0 |
| 9 | Golden State Warriors | 39.9 | 42.1 | 8.1 |
| 10 | Phoenix Suns | 39.8 | 42.2 | 8.2 |
| 11 | Los Angeles Clippers | 39.6 | 42.4 | 8.4 |
| 12 | New Orleans Pelicans | 39.3 | 42.7 | 8.7 |
| 13 | Memphis Grizzlies | 39.1 | 42.9 | 8.9 |
| 14 | Sacramento Kings | 39.0 | 43.0 | 9.0 |
| 15 | Utah Jazz | 39.0 | 43.0 | 9.0 |

## 2031-32 season (feeds the 2032 draft)

### East

| Rank | Team | Avg W | Avg L | GB |
|---|---|---|---|---|
| 1 | Toronto Raptors | 45.5 | 36.5 | 0.0 |
| 2 | Detroit Pistons | 45.2 | 36.8 | 0.3 |
| 3 | Cleveland Cavaliers | 43.4 | 38.6 | 2.1 |
| 4 | Philadelphia 76ers | 41.9 | 40.1 | 3.6 |
| 5 | New York Knicks | 41.5 | 40.5 | 4.0 |
| 6 | Miami Heat | 40.9 | 41.1 | 4.6 |
| 7 | Boston Celtics | 40.7 | 41.3 | 4.8 |
| 8 | Atlanta Hawks | 40.3 | 41.7 | 5.2 |
| 9 | Orlando Magic | 40.1 | 41.9 | 5.4 |
| 10 | Indiana Pacers | 40.0 | 42.0 | 5.5 |
| 11 | Milwaukee Bucks | 39.5 | 42.5 | 6.0 |
| 12 | Chicago Bulls | 39.3 | 42.7 | 6.2 |
| 13 | Charlotte Hornets | 39.0 | 43.0 | 6.5 |
| 14 | Washington Wizards | 36.0 | 46.0 | 9.5 |
| 15 | Brooklyn Nets | 35.0 | 47.0 | 10.5 |

### West

| Rank | Team | Avg W | Avg L | GB |
|---|---|---|---|---|
| 1 | Oklahoma City Thunder | 50.6 | 31.4 | 0.0 |
| 2 | San Antonio Spurs | 47.4 | 34.6 | 3.2 |
| 3 | Denver Nuggets | 46.4 | 35.6 | 4.1 |
| 4 | Los Angeles Lakers | 44.9 | 37.1 | 5.6 |
| 5 | Minnesota Timberwolves | 44.7 | 37.3 | 5.9 |
| 6 | Houston Rockets | 42.9 | 39.1 | 7.6 |
| 7 | Portland Trail Blazers | 40.5 | 41.5 | 10.0 |
| 8 | Dallas Mavericks | 39.2 | 42.8 | 11.4 |
| 9 | Golden State Warriors | 38.9 | 43.1 | 11.7 |
| 10 | Phoenix Suns | 38.7 | 43.3 | 11.8 |
| 11 | Los Angeles Clippers | 38.2 | 43.8 | 12.4 |
| 12 | Memphis Grizzlies | 37.7 | 44.3 | 12.8 |
| 13 | New Orleans Pelicans | 37.6 | 44.4 | 13.0 |
| 14 | Utah Jazz | 37.3 | 44.7 | 13.3 |
| 15 | Sacramento Kings | 36.7 | 45.3 | 13.9 |

## 2032-33 season (feeds the 2033 draft)

### East

| Rank | Team | Avg W | Avg L | GB |
|---|---|---|---|---|
| 1 | New York Knicks | 52.1 | 29.9 | 0.0 |
| 2 | Boston Celtics | 50.5 | 31.5 | 1.6 |
| 3 | Philadelphia 76ers | 50.0 | 32.0 | 2.1 |
| 4 | Detroit Pistons | 49.1 | 32.9 | 3.0 |
| 5 | Cleveland Cavaliers | 47.6 | 34.4 | 4.5 |
| 6 | Miami Heat | 45.4 | 36.6 | 6.7 |
| 7 | Toronto Raptors | 45.1 | 36.9 | 7.1 |
| 8 | Indiana Pacers | 43.8 | 38.2 | 8.3 |
| 9 | Orlando Magic | 43.4 | 38.6 | 8.7 |
| 10 | Atlanta Hawks | 43.2 | 38.8 | 8.9 |
| 11 | Charlotte Hornets | 38.8 | 43.2 | 13.3 |
| 12 | Washington Wizards | 35.3 | 46.7 | 16.8 |
| 13 | Chicago Bulls | 28.3 | 53.7 | 23.9 |
| 14 | Milwaukee Bucks | 25.3 | 56.7 | 26.8 |
| 15 | Brooklyn Nets | 24.0 | 58.0 | 28.1 |

### West

| Rank | Team | Avg W | Avg L | GB |
|---|---|---|---|---|
| 1 | Oklahoma City Thunder | 61.1 | 20.9 | 0.0 |
| 2 | San Antonio Spurs | 60.1 | 21.9 | 1.0 |
| 3 | Denver Nuggets | 48.7 | 33.3 | 12.4 |
| 4 | Minnesota Timberwolves | 47.6 | 34.4 | 13.5 |
| 5 | Houston Rockets | 47.0 | 35.0 | 14.1 |
| 6 | Los Angeles Lakers | 44.9 | 37.1 | 16.1 |
| 7 | Portland Trail Blazers | 41.9 | 40.1 | 19.2 |
| 8 | Golden State Warriors | 40.1 | 41.9 | 21.0 |
| 9 | Phoenix Suns | 38.9 | 43.1 | 22.1 |
| 10 | Utah Jazz | 36.3 | 45.7 | 24.7 |
| 11 | Dallas Mavericks | 33.7 | 48.3 | 27.4 |
| 12 | Los Angeles Clippers | 30.1 | 51.9 | 31.0 |
| 13 | Memphis Grizzlies | 28.5 | 53.5 | 32.6 |
| 14 | New Orleans Pelicans | 27.9 | 54.1 | 33.2 |
| 15 | Sacramento Kings | 21.2 | 60.8 | 39.9 |
