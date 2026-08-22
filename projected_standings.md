# Projected Standings -- Underlying the Pick Value Projections

Average simulated wins per team per season (2000 trials each), for the SAME ratings that drive every pick distribution/grade in league_pick_grades.md: real 2026-27 market ratings for 2027, DARKO+longevity-evolved ratings (darko_ratings.py) for 2028-2032, and the flat 2027 market ratings again for 2033 (outside darko_ratings.py's window -- see its module docstring for why the window stops where it does). These are regular-season win projections only -- no play-in/lottery/draft-order logic runs here, that all happens downstream in draft_pipeline_321.py using these same ratings.

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
| 1 | New York Knicks | 50.3 | 31.7 | 0.0 |
| 2 | Boston Celtics | 47.4 | 34.6 | 2.9 |
| 3 | Detroit Pistons | 47.0 | 35.0 | 3.3 |
| 4 | Toronto Raptors | 45.8 | 36.2 | 4.6 |
| 5 | Philadelphia 76ers | 44.8 | 37.2 | 5.5 |
| 6 | Orlando Magic | 44.7 | 37.3 | 5.6 |
| 7 | Cleveland Cavaliers | 44.5 | 37.5 | 5.9 |
| 8 | Atlanta Hawks | 42.1 | 39.9 | 8.2 |
| 9 | Miami Heat | 40.8 | 41.2 | 9.5 |
| 10 | Indiana Pacers | 38.9 | 43.1 | 11.5 |
| 11 | Charlotte Hornets | 37.8 | 44.2 | 12.5 |
| 12 | Milwaukee Bucks | 36.3 | 45.7 | 14.0 |
| 13 | Chicago Bulls | 35.2 | 46.8 | 15.1 |
| 14 | Brooklyn Nets | 30.3 | 51.7 | 20.0 |
| 15 | Washington Wizards | 29.0 | 53.0 | 21.3 |

### West

| Rank | Team | Avg W | Avg L | GB |
|---|---|---|---|---|
| 1 | San Antonio Spurs | 54.6 | 27.4 | 0.0 |
| 2 | Los Angeles Lakers | 52.2 | 29.8 | 2.4 |
| 3 | Minnesota Timberwolves | 50.2 | 31.8 | 4.3 |
| 4 | Denver Nuggets | 48.7 | 33.3 | 5.9 |
| 5 | Oklahoma City Thunder | 47.7 | 34.3 | 6.9 |
| 6 | Houston Rockets | 44.5 | 37.5 | 10.0 |
| 7 | Portland Trail Blazers | 40.4 | 41.6 | 14.1 |
| 8 | Phoenix Suns | 36.9 | 45.1 | 17.7 |
| 9 | Golden State Warriors | 36.9 | 45.1 | 17.7 |
| 10 | Dallas Mavericks | 36.2 | 45.8 | 18.4 |
| 11 | New Orleans Pelicans | 35.1 | 46.9 | 19.5 |
| 12 | Los Angeles Clippers | 34.4 | 47.6 | 20.2 |
| 13 | Sacramento Kings | 33.0 | 49.0 | 21.5 |
| 14 | Utah Jazz | 32.2 | 49.8 | 22.4 |
| 15 | Memphis Grizzlies | 32.0 | 50.0 | 22.6 |

## 2028-29 season (feeds the 2029 draft)

### East

| Rank | Team | Avg W | Avg L | GB |
|---|---|---|---|---|
| 1 | Detroit Pistons | 47.7 | 34.3 | 0.0 |
| 2 | Cleveland Cavaliers | 47.0 | 35.0 | 0.7 |
| 3 | Toronto Raptors | 46.9 | 35.1 | 0.8 |
| 4 | New York Knicks | 45.9 | 36.1 | 1.7 |
| 5 | Boston Celtics | 45.4 | 36.6 | 2.3 |
| 6 | Philadelphia 76ers | 44.8 | 37.2 | 2.9 |
| 7 | Orlando Magic | 44.6 | 37.4 | 3.1 |
| 8 | Atlanta Hawks | 41.5 | 40.5 | 6.2 |
| 9 | Indiana Pacers | 39.5 | 42.5 | 8.2 |
| 10 | Miami Heat | 39.3 | 42.7 | 8.4 |
| 11 | Charlotte Hornets | 38.1 | 43.9 | 9.6 |
| 12 | Chicago Bulls | 37.1 | 44.9 | 10.6 |
| 13 | Milwaukee Bucks | 37.1 | 44.9 | 10.6 |
| 14 | Washington Wizards | 30.6 | 51.4 | 17.1 |
| 15 | Brooklyn Nets | 29.8 | 52.2 | 17.9 |

### West

| Rank | Team | Avg W | Avg L | GB |
|---|---|---|---|---|
| 1 | San Antonio Spurs | 54.0 | 28.0 | 0.0 |
| 2 | Minnesota Timberwolves | 50.0 | 32.0 | 4.0 |
| 3 | Oklahoma City Thunder | 49.3 | 32.7 | 4.6 |
| 4 | Los Angeles Lakers | 48.9 | 33.1 | 5.0 |
| 5 | Denver Nuggets | 44.6 | 37.4 | 9.3 |
| 6 | Houston Rockets | 43.7 | 38.3 | 10.3 |
| 7 | Portland Trail Blazers | 38.3 | 43.7 | 15.6 |
| 8 | Phoenix Suns | 38.1 | 43.9 | 15.8 |
| 9 | Dallas Mavericks | 37.3 | 44.7 | 16.7 |
| 10 | Golden State Warriors | 37.0 | 45.0 | 16.9 |
| 11 | Los Angeles Clippers | 36.1 | 45.9 | 17.9 |
| 12 | New Orleans Pelicans | 35.6 | 46.4 | 18.4 |
| 13 | Sacramento Kings | 35.1 | 46.9 | 18.9 |
| 14 | Utah Jazz | 33.9 | 48.1 | 20.0 |
| 15 | Memphis Grizzlies | 32.9 | 49.1 | 21.1 |

## 2029-30 season (feeds the 2030 draft)

### East

| Rank | Team | Avg W | Avg L | GB |
|---|---|---|---|---|
| 1 | Detroit Pistons | 48.6 | 33.4 | 0.0 |
| 2 | Cleveland Cavaliers | 46.4 | 35.6 | 2.1 |
| 3 | Toronto Raptors | 45.5 | 36.5 | 3.1 |
| 4 | Orlando Magic | 43.8 | 38.2 | 4.7 |
| 5 | Boston Celtics | 43.2 | 38.8 | 5.4 |
| 6 | New York Knicks | 43.1 | 38.9 | 5.5 |
| 7 | Atlanta Hawks | 41.7 | 40.3 | 6.9 |
| 8 | Philadelphia 76ers | 40.4 | 41.6 | 8.2 |
| 9 | Miami Heat | 39.6 | 42.4 | 9.0 |
| 10 | Charlotte Hornets | 39.4 | 42.6 | 9.2 |
| 11 | Indiana Pacers | 39.0 | 43.0 | 9.5 |
| 12 | Milwaukee Bucks | 38.2 | 43.8 | 10.4 |
| 13 | Chicago Bulls | 37.6 | 44.4 | 11.0 |
| 14 | Brooklyn Nets | 35.0 | 47.0 | 13.6 |
| 15 | Washington Wizards | 34.7 | 47.3 | 13.9 |

### West

| Rank | Team | Avg W | Avg L | GB |
|---|---|---|---|---|
| 1 | San Antonio Spurs | 52.1 | 29.9 | 0.0 |
| 2 | Oklahoma City Thunder | 50.9 | 31.1 | 1.2 |
| 3 | Los Angeles Lakers | 44.2 | 37.8 | 7.9 |
| 4 | Houston Rockets | 44.0 | 38.0 | 8.1 |
| 5 | Denver Nuggets | 42.6 | 39.4 | 9.6 |
| 6 | Minnesota Timberwolves | 42.4 | 39.6 | 9.8 |
| 7 | Phoenix Suns | 39.1 | 42.9 | 13.0 |
| 8 | Portland Trail Blazers | 38.9 | 43.1 | 13.2 |
| 9 | Dallas Mavericks | 38.1 | 43.9 | 14.0 |
| 10 | Golden State Warriors | 38.0 | 44.0 | 14.1 |
| 11 | Los Angeles Clippers | 37.7 | 44.3 | 14.4 |
| 12 | New Orleans Pelicans | 37.2 | 44.8 | 14.9 |
| 13 | Sacramento Kings | 37.2 | 44.8 | 14.9 |
| 14 | Memphis Grizzlies | 35.8 | 46.2 | 16.3 |
| 15 | Utah Jazz | 35.6 | 46.4 | 16.5 |

## 2030-31 season (feeds the 2031 draft)

### East

| Rank | Team | Avg W | Avg L | GB |
|---|---|---|---|---|
| 1 | Toronto Raptors | 45.9 | 36.1 | 0.0 |
| 2 | Cleveland Cavaliers | 45.1 | 36.9 | 0.7 |
| 3 | Detroit Pistons | 44.8 | 37.2 | 1.1 |
| 4 | New York Knicks | 43.3 | 38.7 | 2.5 |
| 5 | Boston Celtics | 42.0 | 40.0 | 3.9 |
| 6 | Orlando Magic | 41.6 | 40.4 | 4.3 |
| 7 | Philadelphia 76ers | 41.1 | 40.9 | 4.8 |
| 8 | Miami Heat | 40.2 | 41.8 | 5.6 |
| 9 | Atlanta Hawks | 40.0 | 42.0 | 5.9 |
| 10 | Charlotte Hornets | 39.7 | 42.3 | 6.1 |
| 11 | Indiana Pacers | 39.7 | 42.3 | 6.2 |
| 12 | Milwaukee Bucks | 39.1 | 42.9 | 6.8 |
| 13 | Chicago Bulls | 38.6 | 43.4 | 7.3 |
| 14 | Washington Wizards | 36.2 | 45.8 | 9.7 |
| 15 | Brooklyn Nets | 36.0 | 46.0 | 9.8 |

### West

| Rank | Team | Avg W | Avg L | GB |
|---|---|---|---|---|
| 1 | San Antonio Spurs | 51.2 | 30.8 | 0.0 |
| 2 | Oklahoma City Thunder | 48.0 | 34.0 | 3.2 |
| 3 | Los Angeles Lakers | 43.5 | 38.5 | 7.7 |
| 4 | Denver Nuggets | 43.4 | 38.6 | 7.7 |
| 5 | Minnesota Timberwolves | 42.9 | 39.1 | 8.3 |
| 6 | Houston Rockets | 41.9 | 40.1 | 9.2 |
| 7 | Portland Trail Blazers | 39.8 | 42.2 | 11.4 |
| 8 | Phoenix Suns | 39.0 | 43.0 | 12.1 |
| 9 | Dallas Mavericks | 39.0 | 43.0 | 12.2 |
| 10 | Golden State Warriors | 39.0 | 43.0 | 12.2 |
| 11 | Los Angeles Clippers | 38.9 | 43.1 | 12.2 |
| 12 | New Orleans Pelicans | 38.1 | 43.9 | 13.1 |
| 13 | Sacramento Kings | 38.1 | 43.9 | 13.1 |
| 14 | Memphis Grizzlies | 37.3 | 44.7 | 13.9 |
| 15 | Utah Jazz | 36.8 | 45.2 | 14.4 |

## 2031-32 season (feeds the 2032 draft)

### East

| Rank | Team | Avg W | Avg L | GB |
|---|---|---|---|---|
| 1 | New York Knicks | 49.1 | 32.9 | 0.0 |
| 2 | Toronto Raptors | 47.4 | 34.6 | 1.8 |
| 3 | Detroit Pistons | 47.3 | 34.7 | 1.8 |
| 4 | Cleveland Cavaliers | 45.0 | 37.0 | 4.1 |
| 5 | Philadelphia 76ers | 42.7 | 39.3 | 6.4 |
| 6 | Boston Celtics | 42.5 | 39.5 | 6.6 |
| 7 | Orlando Magic | 41.5 | 40.5 | 7.7 |
| 8 | Miami Heat | 40.5 | 41.5 | 8.6 |
| 9 | Atlanta Hawks | 39.0 | 43.0 | 10.1 |
| 10 | Charlotte Hornets | 38.2 | 43.8 | 10.9 |
| 11 | Indiana Pacers | 38.2 | 43.8 | 10.9 |
| 12 | Milwaukee Bucks | 37.5 | 44.5 | 11.7 |
| 13 | Chicago Bulls | 36.2 | 45.8 | 12.9 |
| 14 | Washington Wizards | 32.3 | 49.7 | 16.9 |
| 15 | Brooklyn Nets | 29.7 | 52.3 | 19.4 |

### West

| Rank | Team | Avg W | Avg L | GB |
|---|---|---|---|---|
| 1 | San Antonio Spurs | 54.2 | 27.8 | 0.0 |
| 2 | Oklahoma City Thunder | 51.5 | 30.5 | 2.7 |
| 3 | Denver Nuggets | 50.9 | 31.1 | 3.3 |
| 4 | Los Angeles Lakers | 49.6 | 32.4 | 4.5 |
| 5 | Minnesota Timberwolves | 48.2 | 33.8 | 6.0 |
| 6 | Houston Rockets | 44.5 | 37.5 | 9.7 |
| 7 | Portland Trail Blazers | 39.9 | 42.1 | 14.3 |
| 8 | Phoenix Suns | 37.5 | 44.5 | 16.6 |
| 9 | Golden State Warriors | 37.0 | 45.0 | 17.2 |
| 10 | Dallas Mavericks | 36.3 | 45.7 | 17.9 |
| 11 | Los Angeles Clippers | 36.1 | 45.9 | 18.1 |
| 12 | New Orleans Pelicans | 35.1 | 46.9 | 19.1 |
| 13 | Memphis Grizzlies | 34.4 | 47.6 | 19.8 |
| 14 | Utah Jazz | 34.0 | 48.0 | 20.2 |
| 15 | Sacramento Kings | 33.6 | 48.4 | 20.5 |

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
