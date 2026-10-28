# Projected Standings -- Underlying the Pick Value Projections

Average simulated wins per team per season (2000 trials each), for the SAME ratings that drive every pick distribution/grade in /Users/tobeyhirsch/Desktop/NBA Draft Pick Model/nba-draft-pick-grader/league_pick_grades.md: 2026-27 trade-deadline ratings for 2027 (55-game records locked in, remaining 27 games simulated), DARKO+longevity-evolved ratings (darko_ratings.py) for 2028-2032, and the flat 2027 deadline ratings again (from 0-0) for 2033 (outside darko_ratings.py's window -- see its module docstring for why the window stops where it does). These are regular-season win projections only -- no play-in/lottery/draft-order logic runs here, that all happens downstream in draft_pipeline_321.py using these same ratings.

## 2026-27 season (feeds the 2027 draft)

### East

| Rank | Team | Avg W | Avg L | GB |
|---|---|---|---|---|
| 1 | New York Knicks | 52.9 | 29.1 | 0.0 |
| 2 | Boston Celtics | 51.9 | 30.1 | 1.0 |
| 3 | Philadelphia 76ers | 51.9 | 30.1 | 1.0 |
| 4 | Detroit Pistons | 48.8 | 33.2 | 4.1 |
| 5 | Cleveland Cavaliers | 48.0 | 34.0 | 4.9 |
| 6 | Toronto Raptors | 47.0 | 35.0 | 6.0 |
| 7 | Miami Heat | 45.9 | 36.1 | 7.0 |
| 8 | Indiana Pacers | 44.0 | 38.0 | 8.9 |
| 9 | Atlanta Hawks | 42.9 | 39.1 | 10.0 |
| 10 | Orlando Magic | 42.9 | 39.1 | 10.0 |
| 11 | Charlotte Hornets | 39.1 | 42.9 | 13.9 |
| 12 | Washington Wizards | 35.1 | 46.9 | 17.9 |
| 13 | Chicago Bulls | 27.9 | 54.1 | 25.1 |
| 14 | Milwaukee Bucks | 25.0 | 57.0 | 28.0 |
| 15 | Brooklyn Nets | 23.0 | 59.0 | 30.0 |

### West

| Rank | Team | Avg W | Avg L | GB |
|---|---|---|---|---|
| 1 | San Antonio Spurs | 61.9 | 20.1 | 0.0 |
| 2 | Oklahoma City Thunder | 61.9 | 20.1 | 0.1 |
| 3 | Denver Nuggets | 47.9 | 34.1 | 14.1 |
| 4 | Minnesota Timberwolves | 47.9 | 34.1 | 14.1 |
| 5 | Houston Rockets | 46.9 | 35.1 | 15.1 |
| 6 | Los Angeles Lakers | 45.9 | 36.1 | 16.1 |
| 7 | Portland Trail Blazers | 41.0 | 41.0 | 20.9 |
| 8 | Phoenix Suns | 40.0 | 42.0 | 21.9 |
| 9 | Golden State Warriors | 38.9 | 43.1 | 23.0 |
| 10 | Utah Jazz | 36.0 | 46.0 | 25.9 |
| 11 | Dallas Mavericks | 33.9 | 48.1 | 28.0 |
| 12 | New Orleans Pelicans | 28.9 | 53.1 | 33.1 |
| 13 | Los Angeles Clippers | 27.9 | 54.1 | 34.0 |
| 14 | Memphis Grizzlies | 26.9 | 55.1 | 35.0 |
| 15 | Sacramento Kings | 20.9 | 61.1 | 41.1 |

## 2027-28 season (feeds the 2028 draft)

### East

| Rank | Team | Avg W | Avg L | GB |
|---|---|---|---|---|
| 1 | Toronto Raptors | 47.3 | 34.7 | 0.0 |
| 2 | Boston Celtics | 45.4 | 36.6 | 1.9 |
| 3 | Detroit Pistons | 45.0 | 37.0 | 2.3 |
| 4 | Cleveland Cavaliers | 44.2 | 37.8 | 3.1 |
| 5 | New York Knicks | 43.7 | 38.3 | 3.6 |
| 6 | Orlando Magic | 42.6 | 39.4 | 4.7 |
| 7 | Philadelphia 76ers | 42.3 | 39.7 | 5.0 |
| 8 | Atlanta Hawks | 41.6 | 40.4 | 5.7 |
| 9 | Miami Heat | 41.5 | 40.5 | 5.8 |
| 10 | Indiana Pacers | 39.1 | 42.9 | 8.3 |
| 11 | Chicago Bulls | 38.2 | 43.8 | 9.1 |
| 12 | Milwaukee Bucks | 38.0 | 44.0 | 9.3 |
| 13 | Charlotte Hornets | 37.1 | 44.9 | 10.2 |
| 14 | Brooklyn Nets | 33.8 | 48.2 | 13.5 |
| 15 | Washington Wizards | 32.2 | 49.8 | 15.2 |

### West

| Rank | Team | Avg W | Avg L | GB |
|---|---|---|---|---|
| 1 | Oklahoma City Thunder | 53.5 | 28.5 | 0.0 |
| 2 | San Antonio Spurs | 49.2 | 32.8 | 4.3 |
| 3 | Minnesota Timberwolves | 47.2 | 34.8 | 6.3 |
| 4 | Los Angeles Lakers | 46.7 | 35.3 | 6.8 |
| 5 | Denver Nuggets | 46.4 | 35.6 | 7.1 |
| 6 | Houston Rockets | 42.5 | 39.5 | 11.0 |
| 7 | Portland Trail Blazers | 41.0 | 41.0 | 12.5 |
| 8 | Phoenix Suns | 38.4 | 43.6 | 15.0 |
| 9 | New Orleans Pelicans | 38.2 | 43.8 | 15.3 |
| 10 | Golden State Warriors | 37.8 | 44.2 | 15.7 |
| 11 | Dallas Mavericks | 37.1 | 44.9 | 16.4 |
| 12 | Utah Jazz | 35.7 | 46.3 | 17.8 |
| 13 | Los Angeles Clippers | 35.6 | 46.4 | 17.9 |
| 14 | Memphis Grizzlies | 34.8 | 47.2 | 18.7 |
| 15 | Sacramento Kings | 34.0 | 48.0 | 19.5 |

## 2028-29 season (feeds the 2029 draft)

### East

| Rank | Team | Avg W | Avg L | GB |
|---|---|---|---|---|
| 1 | Toronto Raptors | 47.0 | 35.0 | 0.0 |
| 2 | Cleveland Cavaliers | 45.4 | 36.6 | 1.5 |
| 3 | Detroit Pistons | 45.4 | 36.6 | 1.6 |
| 4 | Boston Celtics | 43.3 | 38.7 | 3.7 |
| 5 | Philadelphia 76ers | 42.7 | 39.3 | 4.2 |
| 6 | Orlando Magic | 42.4 | 39.6 | 4.5 |
| 7 | Atlanta Hawks | 41.5 | 40.5 | 5.5 |
| 8 | New York Knicks | 41.1 | 40.9 | 5.8 |
| 9 | Indiana Pacers | 40.1 | 41.9 | 6.9 |
| 10 | Miami Heat | 40.0 | 42.0 | 7.0 |
| 11 | Chicago Bulls | 39.4 | 42.6 | 7.5 |
| 12 | Milwaukee Bucks | 38.5 | 43.5 | 8.5 |
| 13 | Charlotte Hornets | 38.1 | 43.9 | 8.9 |
| 14 | Brooklyn Nets | 34.1 | 47.9 | 12.8 |
| 15 | Washington Wizards | 33.7 | 48.3 | 13.2 |

### West

| Rank | Team | Avg W | Avg L | GB |
|---|---|---|---|---|
| 1 | Oklahoma City Thunder | 52.6 | 29.4 | 0.0 |
| 2 | San Antonio Spurs | 48.7 | 33.3 | 3.9 |
| 3 | Minnesota Timberwolves | 46.7 | 35.3 | 5.9 |
| 4 | Los Angeles Lakers | 44.9 | 37.1 | 7.7 |
| 5 | Denver Nuggets | 43.5 | 38.5 | 9.1 |
| 6 | Houston Rockets | 42.3 | 39.7 | 10.2 |
| 7 | Portland Trail Blazers | 39.1 | 42.9 | 13.5 |
| 8 | Phoenix Suns | 39.1 | 42.9 | 13.5 |
| 9 | Dallas Mavericks | 38.3 | 43.7 | 14.3 |
| 10 | Golden State Warriors | 38.2 | 43.8 | 14.4 |
| 11 | New Orleans Pelicans | 37.7 | 44.3 | 14.9 |
| 12 | Los Angeles Clippers | 37.1 | 44.9 | 15.5 |
| 13 | Utah Jazz | 36.9 | 45.1 | 15.7 |
| 14 | Sacramento Kings | 36.3 | 45.7 | 16.3 |
| 15 | Memphis Grizzlies | 35.9 | 46.1 | 16.7 |

## 2029-30 season (feeds the 2030 draft)

### East

| Rank | Team | Avg W | Avg L | GB |
|---|---|---|---|---|
| 1 | Detroit Pistons | 46.1 | 35.9 | 0.0 |
| 2 | Toronto Raptors | 45.4 | 36.6 | 0.7 |
| 3 | Cleveland Cavaliers | 44.8 | 37.2 | 1.3 |
| 4 | Orlando Magic | 42.1 | 39.9 | 4.0 |
| 5 | Boston Celtics | 41.7 | 40.3 | 4.4 |
| 6 | Atlanta Hawks | 41.7 | 40.3 | 4.5 |
| 7 | Miami Heat | 40.1 | 41.9 | 6.0 |
| 8 | Philadelphia 76ers | 39.8 | 42.2 | 6.3 |
| 9 | New York Knicks | 39.8 | 42.2 | 6.3 |
| 10 | Indiana Pacers | 39.6 | 42.4 | 6.5 |
| 11 | Charlotte Hornets | 39.4 | 42.6 | 6.7 |
| 12 | Milwaukee Bucks | 39.3 | 42.7 | 6.8 |
| 13 | Chicago Bulls | 39.3 | 42.7 | 6.9 |
| 14 | Brooklyn Nets | 37.4 | 44.6 | 8.7 |
| 15 | Washington Wizards | 37.1 | 44.9 | 9.0 |

### West

| Rank | Team | Avg W | Avg L | GB |
|---|---|---|---|---|
| 1 | Oklahoma City Thunder | 52.1 | 29.9 | 0.0 |
| 2 | San Antonio Spurs | 47.3 | 34.7 | 4.8 |
| 3 | Houston Rockets | 42.5 | 39.5 | 9.6 |
| 4 | Los Angeles Lakers | 42.3 | 39.7 | 9.8 |
| 5 | Denver Nuggets | 41.9 | 40.1 | 10.2 |
| 6 | Minnesota Timberwolves | 41.5 | 40.5 | 10.6 |
| 7 | Phoenix Suns | 39.8 | 42.2 | 12.3 |
| 8 | Portland Trail Blazers | 39.5 | 42.5 | 12.7 |
| 9 | Golden State Warriors | 39.2 | 42.8 | 12.9 |
| 10 | Dallas Mavericks | 39.1 | 42.9 | 13.0 |
| 11 | New Orleans Pelicans | 38.6 | 43.4 | 13.5 |
| 12 | Los Angeles Clippers | 38.4 | 43.6 | 13.7 |
| 13 | Utah Jazz | 38.1 | 43.9 | 14.0 |
| 14 | Sacramento Kings | 38.1 | 43.9 | 14.1 |
| 15 | Memphis Grizzlies | 38.0 | 44.0 | 14.1 |

## 2030-31 season (feeds the 2031 draft)

### East

| Rank | Team | Avg W | Avg L | GB |
|---|---|---|---|---|
| 1 | Toronto Raptors | 45.3 | 36.7 | 0.0 |
| 2 | Detroit Pistons | 43.6 | 38.4 | 1.7 |
| 3 | Cleveland Cavaliers | 43.4 | 38.6 | 1.8 |
| 4 | Boston Celtics | 41.1 | 40.9 | 4.2 |
| 5 | Orlando Magic | 40.8 | 41.2 | 4.5 |
| 6 | New York Knicks | 40.8 | 41.2 | 4.5 |
| 7 | Philadelphia 76ers | 40.6 | 41.4 | 4.7 |
| 8 | Miami Heat | 40.5 | 41.5 | 4.8 |
| 9 | Atlanta Hawks | 40.3 | 41.7 | 5.0 |
| 10 | Indiana Pacers | 40.2 | 41.8 | 5.1 |
| 11 | Charlotte Hornets | 39.9 | 42.1 | 5.4 |
| 12 | Milwaukee Bucks | 39.9 | 42.1 | 5.4 |
| 13 | Chicago Bulls | 39.8 | 42.2 | 5.4 |
| 14 | Brooklyn Nets | 38.2 | 43.8 | 7.1 |
| 15 | Washington Wizards | 38.2 | 43.8 | 7.1 |

### West

| Rank | Team | Avg W | Avg L | GB |
|---|---|---|---|---|
| 1 | Oklahoma City Thunder | 48.5 | 33.5 | 0.0 |
| 2 | San Antonio Spurs | 46.8 | 35.2 | 1.7 |
| 3 | Denver Nuggets | 42.3 | 39.7 | 6.2 |
| 4 | Los Angeles Lakers | 42.1 | 39.9 | 6.5 |
| 5 | Minnesota Timberwolves | 41.8 | 40.2 | 6.7 |
| 6 | Houston Rockets | 41.1 | 40.9 | 7.4 |
| 7 | Portland Trail Blazers | 40.3 | 41.7 | 8.2 |
| 8 | Dallas Mavericks | 39.9 | 42.1 | 8.6 |
| 9 | Golden State Warriors | 39.8 | 42.2 | 8.7 |
| 10 | Phoenix Suns | 39.7 | 42.3 | 8.8 |
| 11 | Los Angeles Clippers | 39.5 | 42.5 | 9.0 |
| 12 | New Orleans Pelicans | 39.1 | 42.9 | 9.4 |
| 13 | Memphis Grizzlies | 39.0 | 43.0 | 9.6 |
| 14 | Sacramento Kings | 38.8 | 43.2 | 9.7 |
| 15 | Utah Jazz | 38.8 | 43.2 | 9.7 |

## 2031-32 season (feeds the 2032 draft)

### East

| Rank | Team | Avg W | Avg L | GB |
|---|---|---|---|---|
| 1 | Toronto Raptors | 45.8 | 36.2 | 0.0 |
| 2 | Detroit Pistons | 45.5 | 36.5 | 0.3 |
| 3 | Cleveland Cavaliers | 43.6 | 38.4 | 2.2 |
| 4 | Philadelphia 76ers | 42.0 | 40.0 | 3.8 |
| 5 | New York Knicks | 41.6 | 40.4 | 4.3 |
| 6 | Miami Heat | 40.9 | 41.1 | 5.0 |
| 7 | Boston Celtics | 40.7 | 41.3 | 5.2 |
| 8 | Atlanta Hawks | 40.2 | 41.8 | 5.6 |
| 9 | Orlando Magic | 40.1 | 41.9 | 5.8 |
| 10 | Indiana Pacers | 39.9 | 42.1 | 6.0 |
| 11 | Milwaukee Bucks | 39.3 | 42.7 | 6.5 |
| 12 | Chicago Bulls | 39.1 | 42.9 | 6.7 |
| 13 | Charlotte Hornets | 38.8 | 43.2 | 7.0 |
| 14 | Washington Wizards | 35.6 | 46.4 | 10.2 |
| 15 | Brooklyn Nets | 34.6 | 47.4 | 11.3 |

### West

| Rank | Team | Avg W | Avg L | GB |
|---|---|---|---|---|
| 1 | Oklahoma City Thunder | 51.3 | 30.7 | 0.0 |
| 2 | San Antonio Spurs | 47.9 | 34.1 | 3.4 |
| 3 | Denver Nuggets | 46.8 | 35.2 | 4.5 |
| 4 | Los Angeles Lakers | 45.2 | 36.8 | 6.1 |
| 5 | Minnesota Timberwolves | 45.0 | 37.0 | 6.4 |
| 6 | Houston Rockets | 43.1 | 38.9 | 8.2 |
| 7 | Portland Trail Blazers | 40.5 | 41.5 | 10.8 |
| 8 | Dallas Mavericks | 39.0 | 43.0 | 12.3 |
| 9 | Golden State Warriors | 38.7 | 43.3 | 12.6 |
| 10 | Phoenix Suns | 38.6 | 43.4 | 12.7 |
| 11 | Los Angeles Clippers | 38.0 | 44.0 | 13.4 |
| 12 | Memphis Grizzlies | 37.5 | 44.5 | 13.8 |
| 13 | New Orleans Pelicans | 37.3 | 44.7 | 14.0 |
| 14 | Utah Jazz | 37.0 | 45.0 | 14.3 |
| 15 | Sacramento Kings | 36.4 | 45.6 | 14.9 |

## 2032-33 season (feeds the 2033 draft)

### East

| Rank | Team | Avg W | Avg L | GB |
|---|---|---|---|---|
| 1 | Boston Celtics | 51.5 | 30.5 | 0.0 |
| 2 | Philadelphia 76ers | 51.2 | 30.8 | 0.2 |
| 3 | New York Knicks | 51.2 | 30.8 | 0.3 |
| 4 | Toronto Raptors | 48.5 | 33.5 | 3.0 |
| 5 | Cleveland Cavaliers | 48.4 | 33.6 | 3.1 |
| 6 | Detroit Pistons | 48.3 | 33.7 | 3.2 |
| 7 | Indiana Pacers | 45.7 | 36.3 | 5.7 |
| 8 | Miami Heat | 45.5 | 36.5 | 6.0 |
| 9 | Orlando Magic | 42.3 | 39.7 | 9.2 |
| 10 | Atlanta Hawks | 42.2 | 39.8 | 9.3 |
| 11 | Charlotte Hornets | 39.5 | 42.5 | 12.0 |
| 12 | Washington Wizards | 36.4 | 45.6 | 15.1 |
| 13 | Chicago Bulls | 27.1 | 54.9 | 24.3 |
| 14 | Milwaukee Bucks | 24.1 | 57.9 | 27.4 |
| 15 | Brooklyn Nets | 21.2 | 60.8 | 30.2 |

### West

| Rank | Team | Avg W | Avg L | GB |
|---|---|---|---|---|
| 1 | San Antonio Spurs | 63.5 | 18.5 | 0.0 |
| 2 | Oklahoma City Thunder | 60.5 | 21.5 | 2.9 |
| 3 | Minnesota Timberwolves | 48.5 | 33.5 | 15.0 |
| 4 | Denver Nuggets | 48.3 | 33.7 | 15.2 |
| 5 | Houston Rockets | 48.3 | 33.7 | 15.2 |
| 6 | Los Angeles Lakers | 45.2 | 36.8 | 18.2 |
| 7 | Golden State Warriors | 39.4 | 42.6 | 24.1 |
| 8 | Phoenix Suns | 39.4 | 42.6 | 24.1 |
| 9 | Portland Trail Blazers | 39.4 | 42.6 | 24.1 |
| 10 | Utah Jazz | 36.2 | 45.8 | 27.2 |
| 11 | Dallas Mavericks | 33.2 | 48.8 | 30.3 |
| 12 | New Orleans Pelicans | 29.9 | 52.1 | 33.5 |
| 13 | Memphis Grizzlies | 27.3 | 54.7 | 36.1 |
| 14 | Los Angeles Clippers | 27.0 | 55.0 | 36.5 |
| 15 | Sacramento Kings | 21.0 | 61.0 | 42.5 |
