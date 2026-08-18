"""
Real 2026-27 roster depth charts for all 30 teams -- user-supplied,
authoritative for roster MEMBERSHIP (who plays where). Does NOT include
salary or performance data; see cap_sheet_data.py for salary (partial,
being filled in) and team_wins.py for how performance projections plug in
once real per-player DARKO/EPM data is available.

WHY THIS FILE EXISTS: multiple scraped sources (nbacaptracker.com,
Spotrac) were found to have real errors in which players they attribute to
which team -- not just missing/incomplete data, but confirmed wrong
attributions (e.g. Charlotte's cap_sheet_data.py entries originally
included LaMelo Ball, Miles Bridges, and Josh Green, none of whom are
actually on Charlotte's real roster per this depth chart -- Ball and Green
are on Minnesota, Bridges is on Phoenix). This file is the ground truth for
"who is actually on this team right now" that other modules' player lists
should be checked against before being trusted.

Format: {team_name: {position: [player_name, ...]}}. Position strings match
the depth chart's own grouping (PG/SG/SF/PF/C) -- these are DEPTH CHART
listing order (starter first), not a guarantee of exact playing time
splits. Player name strings keep the source's inline annotations (e.g.
"(R)" for rookie, "**" for two-way/camp body/non-guaranteed-type flags,
"(Ex-10)"/"(Ex-9)" for Exhibit 9/10 contracts, "(RFA)"/"(UFA)" for restricted
/unrestricted free agent, "(+)" for a notable recent addition) rather than
stripping them, since that annotation is informative and this is a direct
transcription, not a cleaned dataset -- callers that need bare names should
strip parenthetical/trailing-marker suffixes themselves.

NOTE: Washington Wizards' center row was cut off mid-transcription in the
source message (ends at "Tristan Vukcevi..."). Reconstructed as "Tristan
Vukcevic" based on the visible prefix and his presence in Washington's cap
sheet data already gathered independently -- flagged here rather than
silently completed, in case that reconstruction is wrong.
"""

from typing import Dict, List

TEAM_DEPTH_CHARTS: Dict[str, Dict[str, List[str]]] = {
    "Atlanta Hawks": {
        "PG": ["Nickeil Alexander-Walker", "Kingston Flemings (R)", "Ryan Nembhard", "Devin Carter", "RayJ Dennis**", "Keshon Gilbert (R)**"],
        "SG": ["CJ McCollum", "Corey Kispert", "Buddy Hield"],
        "SF": ["Dyson Daniels", "Luguentz Dort", "Aaron Wiggins", "Jalen Wilson**"],
        "PF": ["Jalen Johnson", "Mouhamed Gueye", "Asa Newell"],
        "C": ["Onyeka Okongwu", "Jock Landale", "Zuby Ejiofor (R)", "Henri Veesaar (R)"],
    },
    "Boston Celtics": {
        "PG": ["Derrick White", "Payton Pritchard", "Mike Conley", "Milos Uzan (R) (Ex-10)"],
        "SG": ["Sam Hauser", "Baylor Scheierman", "Ron Harper Jr.", "Tucker DeVries (R) (Ex-10)"],
        "SF": ["Paul George", "Jordan Walsh", "Dillon Mitchell (R)"],
        "PF": ["Jayson Tatum", "Hugo Gonzalez", "Chris Cenac Jr. (R)"],
        "C": ["Mitchell Robinson", "Neemias Queta", "Luka Garza", "Amari Williams**"],
    },
    "Brooklyn Nets": {
        "PG": ["Mikel Brown Jr. (R)", "Keon Ellis", "Nolan Traore", "Ben Saraf"],
        "SG": ["Egor Demin", "Terance Mann", "Drake Powell"],
        "SF": ["Michael Porter Jr.", "Josh Minott", "Chaney Johnson**"],
        "PF": ["Julius Randle", "Noah Clowney", "Joshua Jefferson (R)", "Tyler Bilodeau (R)**"],
        "C": ["Day'Ron Sharpe", "Moritz Wagner", "Danny Wolf"],
    },
    "Charlotte Hornets": {
        "PG": ["Coby White", "Tre Mann", "Christian Anderson (R)", "Kylan Boswell (R)**"],
        "SG": ["Kon Knueppel", "Grayson Allen", "Sion James", "Pat Connaughton"],
        "SF": ["Brandon Miller", "Royce O'Neale", "Dorian Finney-Smith", "Liam McNeeley", "Michael Ajayi (R)**"],
        "PF": ["Naz Reid", "Grant Williams", "Tidjane Salaun"],
        "C": ["Moussa Diabate", "Ryan Kalkbrenner", "Hannes Steinbach (R)", "PJ Hall**"],
    },
    "Chicago Bulls": {
        "PG": ["Josh Giddey", "Tre Jones"],
        "SG": ["Norman Powell", "Isaac Okoro", "Rob Dillingham", "Jaylin Sellers (R)**"],
        "SF": ["Matas Buzelis", "Patrick Williams", "Dailyn Swain (R)", "Leonard Miller"],
        "PF": ["Caleb Wilson (R)", "Noa Essengue", "Tobe Awaka (R)**"],
        "C": ["Nic Claxton", "Jalen Smith"],
    },
    "Cleveland Cavaliers": {
        "PG": ["James Harden (UFA)", "Dennis Schroder", "Craig Porter Jr."],
        "SG": ["Donovan Mitchell", "Sam Merrill", "Meleek Thomas (R)", "Tyrese Proctor"],
        "SF": ["Max Strus", "Jaylon Tyson", "Tristan Enaruna**", "Riley Minix**"],
        "PF": ["Evan Mobley", "Mario Hezonja", "Nae'Qwan Tomlin"],
        "C": ["Jarrett Allen", "Thomas Bryant", "Ernest Udeh Jr. (R)**"],
    },
    "Dallas Mavericks": {
        "PG": ["Kyrie Irving", "Marcus Sasser", "Sergio de Larrea (R)"],
        "SG": ["Max Christie", "Klay Thompson", "Jett Howard**", "John Poulakidas**"],
        "SF": ["Cooper Flagg", "Naji Marshall", "Zaccharie Risacher", "Caleb Martin", "Tarik Biberovic (R)"],
        "PF": ["PJ Washington", "Santi Aldama", "Morez Johnson Jr. (R)", "Tobi Lawal (R)**"],
        "C": ["Daniel Gafford", "Dereck Lively II", "Moussa Cisse"],
    },
    "Denver Nuggets": {
        "PG": ["Jamal Murray", "Tyus Jones", "KJ Simpson**"],
        "SG": ["Christian Braun", "Peyton Watson (RFA)"],
        "SF": ["Cameron Johnson", "Spencer Jones", "Alpha Diallo (R)", "Bryce Hopkins (R)"],
        "PF": ["Aaron Gordon", "Zeke Nnaji", "Julian Strawther", "DaRon Holmes II", "Trevon Brazile (R)"],
        "C": ["Nikola Jokic", "Marvin Bagley III"],
    },
    "Detroit Pistons": {
        "PG": ["Cade Cunningham", "Daniss Jenkins", "Ebuka Okorie (R)"],
        "SG": ["Duncan Robinson", "Isaiah Joe", "Kevin Huerter", "Gary Harris", "Chaz Lanier"],
        "SF": ["Ausar Thompson", "Javonte Green", "Taurean Prince", "Elijah Harkless**"],
        "PF": ["John Collins", "Ron Holland", "Tolu Smith", "Isaac Jones**"],
        "C": ["Jalen Duren (RFA)", "Paul Reed", "Ugonna Onyenso (R)**"],
    },
    "Golden State Warriors": {
        "PG": ["Stephen Curry", "De'Anthony Melton", "LJ Cryer (R)**"],
        "SG": ["Brandin Podziemski", "Will Richard"],
        "SF": ["Gui Santos", "Lajae Jones (R)", "Jimmy Butler (+)", "Moses Moody (+)"],
        "PF": ["Draymond Green", "Yaxel Lendeborg (R)", "Malevy Leons**"],
        "C": ["Kristaps Porzingis", "Al Horford", "Charles Bassey"],
    },
    "Houston Rockets": {
        "PG": ["Fred VanVleet", "Reed Sheppard", "Bruce Thornton (R)", "JD Davison", "Tristen Newton**"],
        "SG": ["Amen Thompson", "Marcus Smart"],
        "SF": ["Kevin Durant", "Bogdan Bogdanovic", "Jae'Sean Tate", "Isaiah Crawford", "Quadir Copeland (R)**", "Julian Phillips (Ex-10)"],
        "PF": ["Jabari Smith Jr.", "Tari Eason"],
        "C": ["Alperen Sengun", "Steven Adams", "Clint Capela", "Oscar Tshiebwe (Ex-10)"],
    },
    "Indiana Pacers": {
        "PG": ["Tyrese Haliburton", "TJ McConnell", "Braden Smith (R)**", "Ethan Thompson**"],
        "SG": ["Andrew Nembhard", "Ben Sheppard", "Johnny Furphy", "Quenton Jackson"],
        "SF": ["Aaron Nesmith", "Kelly Oubre Jr.", "Jarace Walker", "Kobe Brown**"],
        "PF": ["Pascal Siakam", "Obi Toppin", "Jalen Slawson**"],
        "C": ["Ivica Zubac", "Jay Huff", "Larry Nance Jr."],
    },
    "Los Angeles Clippers": {
        "PG": ["Darius Garland", "Kris Dunn", "Sean Pedulla**"],
        "SG": ["Keaton Wagler (R)", "Gradey Dick", "Cam Christie"],
        "SF": ["Brandon Ingram", "Bennedict Mathurin (RFA)", "Kobe Sanders", "Nick Martinelli (R)**"],
        "PF": ["Rui Hachimura", "Derrick Jones Jr.", "Jordan Miller", "Baba Miller (R)", "Johni Broome"],
        "C": ["Brook Lopez", "Yanic Konan Niederhauser", "Isaiah Jackson", "Jamarion Sharp (R)**"],
    },
    "Los Angeles Lakers": {
        "PG": ["Luka Doncic", "Collin Sexton", "Bronny James"],
        "SG": ["Austin Reaves", "Quentin Grimes", "Cameron Carr (R)", "Jaden Hardy", "Chris Manon**"],
        "SF": ["Jake LaRavia", "Ziaire Williams", "Matisse Thybulle", "Dalton Knecht", "AK Okereke (R)**"],
        "PF": ["Sandro Mamukelashvili", "Jarred Vanderbilt", "Adou Thiero", "Arthur Kaluma (R)**"],
        "C": ["Walker Kessler", "Kevon Looney"],
    },
    "Memphis Grizzlies": {
        "PG": ["Ty Jerome", "Scotty Pippen Jr.", "Walter Clayton Jr.", "Javon Small**", "D'Angelo Russell"],
        "SG": ["Cedric Coward", "Cam Spencer", "Richie Saunders (R)", "AJ Johnson"],
        "SF": ["Jaylen Wells", "Karim Lopez (R)", "Kris Murray", "Olivier-Maxence Prosper", "Jahmai Mashack**"],
        "PF": ["Cameron Boozer (R)", "GG Jackson", "Taylor Hendricks", "Jerami Grant"],
        "C": ["Zach Edey", "Isaiah Stewart", "Quinten Post", "Taj Gibson", "Carson Cooper (R)**"],
    },
    "Miami Heat": {
        "PG": ["Davion Mitchell", "Dru Smith", "Ryan Conwell (R)", "Tre Donaldson (R)**"],
        "SG": ["Tim Hardaway Jr.", "Pelle Larsson", "Myron Gardner"],
        "SF": ["Andrew Wiggins", "Simone Fontecchio"],
        "PF": ["Giannis Antetokounmpo", "Nikola Jovic"],
        "C": ["Bam Adebayo", "Bobby Portis", "Vladislav Goldin**"],
    },
    "Milwaukee Bucks": {
        "PG": ["Kevin Porter Jr.", "Ryan Rollins", "Brayden Burries (R)", "Kam Jones**"],
        "SG": ["Tyler Herro", "Gary Trent Jr.", "Kasparas Jakucionis", "Cormac Ryan**"],
        "SF": ["Jaime Jaquez Jr.", "AJ Green", "Caris LeVert"],
        "PF": ["Kyle Kuzma", "Nate Ament (R)", "Ousmane Dieng", "Pete Nance", "Bogoljub Markovic (R)"],
        "C": ["Myles Turner", "Kel'el Ware", "Jericho Sims", "Rafael Castro (R)"],
    },
    "Minnesota Timberwolves": {
        "PG": ["Ayo Dosunmu", "Bones Hyland", "Zyon Pullin**"],
        "SG": ["LaMelo Ball", "Josh Green", "Jaylen Clark", "Donte DiVincenzo (+)"],
        "SF": ["Anthony Edwards", "Terrence Shannon Jr.", "Isaiah Evans (R)"],
        "PF": ["Jaden McDaniels", "Trey Lyles", "Trey Kaufman-Renn (R)", "Enrique Freeman**"],
        "C": ["Rudy Gobert", "Joan Beringer", "Rocco Zikarsky**"],
    },
    "New Orleans Pelicans": {
        "PG": ["Dejounte Murray", "Jeremiah Fears", "Jordan Poole", "Kobe Bufkin (Ex-9)"],
        "SG": ["Herb Jones", "Jordan Hawkins", "Micah Peavy", "Jaron Pierre Jr. (R)**"],
        "SF": ["Trey Murphy III", "Saddiq Bey", "Bryce McGowens"],
        "PF": ["Zion Williamson", "Karlo Matkovic"],
        "C": ["Derik Queen", "Yves Missi", "DeAndre Jordan", "Hunter Dickinson**", "Christian Koloko (Ex-9)"],
    },
    "New York Knicks": {
        "PG": ["Jalen Brunson", "Jose Alvarado", "Jordan Clarkson", "Tyler Kolek"],
        "SG": ["Mikal Bridges", "Miles McBride", "Tyler Nickel (R)"],
        "SF": ["Josh Hart", "Landry Shamet"],
        "PF": ["OG Anunoby", "Mohamed Diawara"],
        "C": ["Karl-Anthony Towns", "Andre Drummond"],
    },
    "Oklahoma City Thunder": {
        "PG": ["Shai Gilgeous-Alexander", "Ajay Mitchell", "Nikola Topic"],
        "SG": ["Cason Wallace", "Jared McCain", "Bennett Stirtz (R)", "Otega Oweh (R)**", "Josh Dix (R)**"],
        "SF": ["Jalen Williams", "Alex Caruso", "Kenrich Williams", "Brooks Barnhizer**"],
        "PF": ["Isaiah Hartenstein", "Jaylin Williams"],
        "C": ["Chet Holmgren", "Aday Mara (R)", "Thomas Sorber (R)"],
    },
    "Orlando Magic": {
        "PG": ["Jalen Suggs", "Jevon Carter", "Jase Richardson"],
        "SG": ["Desmond Bane", "Anthony Black", "Alex Morales**"],
        "SF": ["Franz Wagner", "Jonathan Isaac", "Jamal Cain"],
        "PF": ["Paolo Banchero", "Tristan da Silva", "Noah Penda", "Izaiyah Nelson (R)"],
        "C": ["Wendell Carter Jr.", "Goga Bitadze", "Nikola Vucevic", "Colin Castleton**"],
    },
    "Philadelphia 76ers": {
        "PG": ["Tyrese Maxey", "Labaron Philon Jr. (R)", "Caleb Love**"],
        "SG": ["VJ Edgecombe", "Anfernee Simons", "Rayan Rupert**", "Duke Miles (R) (Ex-10)"],
        "SF": ["Jaylen Brown", "Kentavious Caldwell-Pope", "Justin Edwards"],
        "PF": ["LeBron James", "Dean Wade", "Dominick Barlow", "Jabari Walker"],
        "C": ["Joel Embiid", "Ariel Hukporti", "Adem Bona"],
    },
    "Phoenix Suns": {
        "PG": ["Jordan Goodwin", "Collin Gillespie", "Jamaree Bouyea", "Pat Spencer**"],
        "SG": ["Devin Booker", "Luke Kennard", "Jalen Green", "Koby Brea**"],
        "SF": ["Dillon Brooks", "Ryan Dunn", "Haywood Highsmith"],
        "PF": ["Miles Bridges", "Oso Ighodaro", "Koa Peat (R)", "Rasheer Fleming", "CJ Huntley**"],
        "C": ["Mark Williams", "Khaman Maluach"],
    },
    "Portland Trail Blazers": {
        "PG": ["Damian Lillard", "Jrue Holiday", "Vit Krejci"],
        "SG": ["Ja Morant", "Scoot Henderson", "Sidy Cissoko", "John Tonje**", "Chris Youngblood**"],
        "SF": ["Toumani Camara", "Shaedon Sharpe", "Jayson Kent**"],
        "PF": ["Deni Avdija", "Robert Williams", "Micah Potter"],
        "C": ["Donovan Clingan", "Yang Hansen (R)", "Branden Carlson"],
    },
    "Sacramento Kings": {
        "PG": ["Darius Acuff Jr. (R)", "Emanuel Sharp (R)", "Adam Flagler**"],
        "SG": ["Zach LaVine", "Malik Monk", "Daeqwon Plowden"],
        "SF": ["De'Andre Hunter", "Nique Clifford", "Alex Karaban (R)"],
        "PF": ["Keegan Murray", "Precious Achiuwa", "Dylan Cardwell", "Jonathan Mogbo**"],
        "C": ["Domantas Sabonis", "Maxime Raynaud"],
    },
    "San Antonio Spurs": {
        "PG": ["De'Aaron Fox", "Dylan Harper", "Jordan McLaughlin", "Ja'Kobi Gillespie (R)**"],
        "SG": ["Stephon Castle", "Keldon Johnson", "David Jones Garcia**"],
        "SF": ["Devin Vassell", "Harrison Barnes", "Carter Bryant"],
        "PF": ["Julian Champagnie", "Tobias Harris", "Tarris Reed Jr. (R)", "Maliq Brown (R)**", "Emanuel Miller**"],
        "C": ["Victor Wembanyama", "Luke Kornet", "Jayden Quaintance (R)"],
    },
    "Toronto Raptors": {
        "PG": ["Immanuel Quickley", "Jamal Shead", "Jaden Bradley (R)**", "Chucky Hepburn**"],
        "SG": ["RJ Barrett", "Ja'Kobe Walter", "Alijah Martin"],
        "SF": ["Kawhi Leonard", "Jamison Battle"],
        "PF": ["Scottie Barnes", "Kyle Anderson", "Allen Graves (R)"],
        "C": ["Jakob Poeltl", "Collin Murray-Boyles", "Trayce Jackson-Davis", "Nathan Bittle (R) (Ex-10)"],
    },
    "Utah Jazz": {
        "PG": ["Keyonte George", "Isaiah Collier", "Tamar Bates (R)**"],
        "SG": ["Darryn Peterson (R)", "Josh Okogie", "Cody Williams", "Sviatoslav Mykhailiuk", "Trey Alexander**"],
        "SF": ["Lauri Markkanen", "Ace Bailey", "John Konchar", "Blake Hinson**", "Harrison Ingram (Ex-10)"],
        "PF": ["Jaren Jackson Jr.", "Brice Sensabaugh"],
        "C": ["Jusuf Nurkic", "Jaxson Hayes", "Kyle Filipowski", "Mohamed Bamba"],
    },
    "Washington Wizards": {
        "PG": ["Trae Young", "Bub Carrington"],
        "SG": ["Kyshawn George", "Tre Johnson", "Jamir Watkins** (+)"],
        "SF": ["AJ Dybantsa (R)", "Khris Middleton", "Will Riley", "Cam Whitmore"],
        "PF": ["Anthony Davis", "Bilal Coulibaly", "Justin Champagnie", "Julian Reese (R)**"],
        "C": ["Alex Sarr", "Deandre Ayton", "Tristan Vukcevic"],  # NOTE: source text cut off after "Tristan Vukcevi..." -- reconstructed, see module docstring
    },
}


def bare_name(annotated_name: str) -> str:
    """Strips trailing annotations like '(R)', '**', '(Ex-10)', '(RFA)', '(+)' to get a plain player name."""
    import re
    return re.sub(r"\s*(\(\w[\w\s-]*\)|\*\*|\(\+\))+\s*$", "", annotated_name).strip()


def team_for_player(player_bare_name: str) -> "list[str]":
    """Returns the list of teams whose depth chart includes a player with this bare name (should normally be 0 or 1; >1 would indicate a data problem)."""
    matches = []
    for team, positions in TEAM_DEPTH_CHARTS.items():
        for names in positions.values():
            if any(bare_name(n) == player_bare_name for n in names):
                matches.append(team)
                break
    return matches


if __name__ == "__main__":
    print(f"Loaded depth charts for {len(TEAM_DEPTH_CHARTS)} teams")
    total_players = sum(len(names) for positions in TEAM_DEPTH_CHARTS.values() for names in positions.values())
    print(f"Total listed players (incl. rookies/two-ways/exhibit contracts): {total_players}")

    # Sanity check: no player name should appear on more than one team's chart.
    from collections import defaultdict
    seen: dict = defaultdict(list)
    for team, positions in TEAM_DEPTH_CHARTS.items():
        for names in positions.values():
            for n in names:
                seen[bare_name(n)].append(team)
    dupes = {name: teams for name, teams in seen.items() if len(teams) > 1}
    print(f"\nPlayers appearing on more than one team's chart (should be empty): {dupes}")

    # Spot check the corrections made to cap_sheet_data.py
    for name in ["LaMelo Ball", "Miles Bridges", "Josh Green", "Jaylen Brown", "Jaden Hardy", "D'Angelo Russell"]:
        print(f"{name}: {team_for_player(name)}")
