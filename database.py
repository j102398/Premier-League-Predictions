from datetime import datetime as datetime_module
import requests
from bs4 import BeautifulSoup
import sqlite3
import os
import shutil

pageToScrape = requests.get('https://fbref.com/en/comps/9/Premier-League-Stats')
soup = BeautifulSoup(pageToScrape.text, "html.parser")

# List of tuples with data-stat and SQL data type
identifiers_and_types_standard = [
    ("players_used", "TEXT"),
    ("avg_age", "REAL"),
    ("possession", "REAL"),
    ("games", "INTEGER"),
    ("games_starts", "INTEGER"),
    ("minutes", "INTEGER"),
    ("minutes_90s", "REAL"),
    ("goals", "INTEGER"),
    ("assists", "INTEGER"),
    ("goals_assists", "INTEGER"),
    ("goals_pens", "INTEGER"),
    ("pens_made", "INTEGER"),
    ("cards_yellow", "INTEGER"),
    ("cards_red", "INTEGER"),
    ("xg", "REAL"),
    ("npxg", "REAL"),
    ("xg_assist", "REAL"),
    ("progressive_carries", "TEXT"),
    ("progressive_passes", "TEXT"),
    ("progressive_passes_received", "TEXT"),
    ("goals_per90", "REAL"),
    ("assists_per90", "REAL"),
    ("goals_assists_per90", "REAL"),
    ("goals_pens_per90", "REAL"),
    ("points", "REAL"),
    ("wins", "INTEGER"),
    ("ties", "INTEGER"),
    ("losses", "TEXT"),
    ("last_5", "INTEGER"),
    ("goal_diff", "REAL"),

]

identifiers_and_types_goalkeeping = [
    ('gk_goals_against', 'INTEGER'),
    ('gk_goals_against_per90', 'REAL'),
    ('gk_shots_on_target_against', 'INTEGER'),
    ('gk_saves', 'INTEGER'),
    ('gk_saves_pct', 'REAL'),
    ('gk_clean_sheets', 'INTEGER'),
    ('gk_clean_sheets_pct', 'REAL'),
    ('gk_pens_att', 'INTEGER'),
    ('gk_pens_allowed', 'INTEGER'),
    ('gk_pens_saved', 'INTEGER'),
    ('gk_pens_missed', 'INTEGER'),
    ('gk_pens_save_pct', 'REAL')
]

identifiers_and_types_advanced_goalkeeping = [
    ('gk_free_kick_goals_against', 'INTEGER'),
    ('gk_corner_kick_goals_against', 'INTEGER'),
    ('gk_own_goals_against', 'INTEGER'),
    ('gk_psxg', 'REAL'),
    ('gk_psnpxg_per_shot_on_target_against', 'REAL'),
    ('gk_psxg_net', 'REAL'),
    ('gk_psxg_net_per90', 'REAL'),
    ('gk_passes_completed_launched', 'INTEGER'),
    ('gk_passes_launched', 'INTEGER'),
    ('gk_passes_pct_launched', 'REAL'),
    ('gk_passes', 'INTEGER'),
    ('gk_passes_throws', 'INTEGER'),
    ('gk_pct_passes_launched', 'REAL'),
    ('gk_passes_length_avg', 'REAL'),
    ('gk_goal_kicks', 'INTEGER'),
    ('gk_pct_goal_kicks_launched', 'REAL'),
    ('gk_goal_kick_length_avg', 'REAL'),
    ('gk_crosses', 'INTEGER'),
    ('gk_crosses_stopped', 'INTEGER'),
    ('gk_crosses_stopped_pct', 'REAL'),
    ('gk_def_actions_outside_pen_area', 'INTEGER'),
    ('gk_def_actions_outside_pen_area_per90', 'REAL'),
    ('gk_avg_distance_def_actions', 'REAL')
]

identifiers_and_types_shooting = [
    ('goals', 'INTEGER'),
    ('shots', 'INTEGER'),
    ('shots_on_target', 'INTEGER'),
    ('shots_on_target_pct', 'REAL'),
    ('shots_per90', 'REAL'),
    ('shots_on_target_p90', 'REAL'),
    ('goals_per_shot', 'REAL'),
    ('goals_per_shot_on_target', 'REAL'),
    ('average_shot_distance', 'REAL'),
    ('shots_free_kicks', 'INTEGER'),
    ('pens_made', 'INTEGER'),
    ('pens_att', 'INTEGER'),
    ('xg', 'REAL'),
    ('npxg', 'REAL'),
    ('npxg_per_shot', 'REAL'),
    ('xg_net', 'REAL'),
    ('npxg_net', 'REAL')
]

identifiers_and_types_passing = [
    ('minutes_90s', 'REAL'),
    ('passes_completed', 'INTEGER'),
    ('passes', 'INTEGER'),
    ('passes_pct', 'REAL'),
    ('passes_total_distance', 'REAL'),
    ('passes_progressive_distance', 'REAL'),
    ('passes_completed_short', 'INTEGER'),
    ('passes_short', 'INTEGER'),
    ('passes_pct_short', 'REAL'),
    ('passes_completed_medium', 'INTEGER'),
    ('passes_pct_medium', 'REAL'),
    ('passes_completed_long', 'INTEGER'),
    ('passes_long', 'INTEGER'),
    ('passes_pct_long', 'REAL'),
    ('assists', 'INTEGER'),
    ('xg_assist', 'REAL'),
    ('pass_xa', 'REAL'),
    ('xg_assist_net', 'REAL'),
    ('assisted_shots', 'INTEGER'),
    ('passes_into_final_third', 'INTEGER'),
    ('passes_into_penalty_area', 'INTEGER'),
    ('crosses_into_penalty_area', 'INTEGER'),
    ('progressive_passes', 'INTEGER')
]

identifiers_and_types_goal_and_shot_creation = [
    ('sca', 'INTEGER'),
    ('sca_per90', 'REAL'),
    ('sca_passes_live', 'INTEGER'),
    ('sca_passes_dead', 'INTEGER'),
    ('sca_take_ons', 'INTEGER'),
    ('sca_shots', 'INTEGER'),
    ('sca_fouled', 'INTEGER'),
    ('sca_defense', 'INTEGER'),
    ('gca', 'INTEGER'),
    ('gca_per90', 'REAL'),
    ('gca_passes_live', 'INTEGER'),
    ('gca_passes_dead', 'INTEGER'),
    ('gca_take_ons', 'INTEGER'),
    ('gca_shots', 'INTEGER'),
    ('gca_fouled', 'INTEGER'),
    ('gca_defense', 'INTEGER')
]

identifiers_and_types_defensive_actions = [
    ('tackles', 'INTEGER'),
    ('tackles_won', 'INTEGER'),
    ('tackles_def_3rd', 'INTEGER'),
    ('tackles_mid_3rd', 'INTEGER'),
    ('tackles_att_3rd', 'INTEGER'),
    ('challenge_tackles', 'INTEGER'),
    ('challenges', 'INTEGER'),
    ('challenges_tackles_pct', 'REAL'),
    ('challenges_lost', 'INTEGER'),
    ('blocks', 'INTEGER'),
    ('blocked_shots', 'INTEGER'),
    ('blocked_passes', 'INTEGER'),
    ('interceptions', 'INTEGER'),
    ('tackles_interceptions', 'INTEGER'),
    ('clearances', 'INTEGER'),
    ('errors', 'INTEGER')
]

identifiers_and_types_possession = [
    ('touches', 'INTEGER'),
    ('touches_def_pen_area', 'INTEGER'),
    ('touches_def_3rd', 'INTEGER'),
    ('touches_mid_3rd', 'INTEGER'),
    ('touches_att_3rd', 'INTEGER'),
    ('touches_att_pen_area', 'INTEGER'),
    ('touches_live_ball', 'INTEGER'),
    ('take_ons', 'INTEGER'),
    ('take_ons_won', 'INTEGER'),
    ('take_ons_won_pct', 'REAL'),
    ('take_ons_tackled', 'INTEGER'),
    ('take_ons_tackled_pct', 'REAL'),
    ('carries', 'INTEGER'),
    ('carries_distance', 'REAL'),
    ('carries_progressive_distance', 'REAL'),
    ('progressive_carries', 'INTEGER'),
    ('carries_into_final_third', 'INTEGER'),
    ('carries_into_penalty_area', 'INTEGER'),
    ('miscontrols', 'INTEGER'),
    ('dispossessed', 'INTEGER'),
    ('passes_received', 'INTEGER'),
    ('progressive_passes_received', 'INTEGER')
]

identifiers_and_types_playing_time = [
    ('game_starts', 'INTEGER'),
    ('minutes_per_start', 'REAL'),
    ('games_complete', 'INTEGER'),
    ('games_subs', 'INTEGER'),
    ('unused_subs', 'INTEGER'),
    ('points_per_game', 'REAL'),
    ('on_goals_for', 'INTEGER'),
    ('on_goals_against', 'INTEGER'),
    ('plus_minus', 'INTEGER'),
    ('plus_minus_per90', 'REAL'),
    ('on_xg_for', 'REAL'),
    ('on_xg_against', 'REAL'),
    ('xg_plus_minus', 'REAL'),
    ('xg_plus_minus_per90', 'REAL')
]


identifiers_and_types_miscellaneous_stats = [
    ('cards_yellow', 'INTEGER'),
    ('cards_red', 'INTEGER'),
    ('cards_yellow_red', 'INTEGER'),
    ('fouls', 'INTEGER'),
    ('fouled', 'INTEGER'),
    ('offsides', 'INTEGER'),
    ('crosses', 'INTEGER'),
    ('interceptions', 'INTEGER'),
    ('tackles_won', 'INTEGER'),
    ('pens_won', 'INTEGER'),
    ('pens_conceded', 'INTEGER'),
    ('own_goals', 'INTEGER'),
    ('ball_recoveries', 'INTEGER'),
    ('aerials_won', 'INTEGER'),
    ('aerials_lost', 'INTEGER'),
    ('aerials_won_pct', 'REAL')
]

tables_and_identifiers = [
    ('standard_for', identifiers_and_types_standard),
    ('standard_against', identifiers_and_types_standard),
    ('goalkeeping_for', identifiers_and_types_goalkeeping),
    ('goalkeeping_against', identifiers_and_types_goalkeeping),
    ('advanced_goalkeeping_for', identifiers_and_types_advanced_goalkeeping),
    ('advanced_goalkeeping_against', identifiers_and_types_advanced_goalkeeping),
    ('shooting_for', identifiers_and_types_shooting),
    ('shooting_against', identifiers_and_types_shooting),
    ('passing_for', identifiers_and_types_passing),
    ('passing_against', identifiers_and_types_passing),
    ('goal_and_shot_creation_for', identifiers_and_types_goal_and_shot_creation),
    ('goal_and_shot_creation_against', identifiers_and_types_goal_and_shot_creation),
    ('defensive_for', identifiers_and_types_defensive_actions),
    ('defensive_against', identifiers_and_types_defensive_actions),
    ('possession_for', identifiers_and_types_possession),
    ('possession_against', identifiers_and_types_possession),
    ('playing_time_for', identifiers_and_types_playing_time),
    ('playing_time_against', identifiers_and_types_playing_time),
    ('miscellaneous_stats_for', identifiers_and_types_miscellaneous_stats),
    ('miscellaneous_stats_against', identifiers_and_types_miscellaneous_stats)
]

# Create a connection to the database
connection = sqlite3.connect('stats.db')
cursor = connection.cursor()

# List of tables to be created
tablesToBeCreated = [
    'standard', 'goalkeeping', 'advanced_goalkeeping', 'shooting', 'passing',
    'pass_types', 'goal_and_shot_creation', 'defensive', 'possession',
    'playing_time', 'miscellaneous_stats'
]

# List of tables including 'team_info'
total_tables = ['team_info']

# Iterate through each table and create 'for' and 'against' versions
for table in tablesToBeCreated:
    table_for = table + "_for"
    table_against = table + "_against"
    total_tables.append(table_for)
    total_tables.append(table_against)

    # Create tables if they do not exist
    cursor.execute(f"CREATE TABLE IF NOT EXISTS {table_for} (team_name TEXT PRIMARY KEY)")
    cursor.execute(f"CREATE TABLE IF NOT EXISTS {table_against} (team_name TEXT PRIMARY KEY)")

# Create 'team_info' table
cursor.execute('''
    CREATE TABLE IF NOT EXISTS team_info (
        team_name TEXT PRIMARY KEY
    )
''')


for table in total_tables:
    cursor.execute(f"DELETE FROM {table}")


def create_team_column():
    row = 0
    team_elements = soup.find_all(attrs={"data-stat": "team"})
    for team in team_elements:
        team_text = team.get_text(strip=True)
        if team_text == "Squad":
            continue
        else:
            vs_team = "vs " + team_text
            for table in total_tables:
                if "against" in table:
                    cursor.execute(f"INSERT OR IGNORE INTO {table} (team_name) VALUES (?)", (vs_team,))
                else:
                    cursor.execute(f"INSERT OR IGNORE INTO {table} (team_name) VALUES (?)", (team_text,))

            cursor.execute('INSERT OR IGNORE INTO team_info (team_name) VALUES (?)', (team_text,))
        row += 1
        if row == 20:
            break

def create_rest_of_columns(identifiers_and_types, table):
    if not isinstance(identifiers_and_types[0], tuple):
        identifiers_and_types = [("", identifiers_and_types)]  # Make it a list of tuples

    for stat, data_type in identifiers_and_types:
        cursor.execute(f"PRAGMA table_info({table})")
        existing_columns = [col[1] for col in cursor.fetchall()]
        if stat not in existing_columns:
            query = f"ALTER TABLE {table} ADD COLUMN {stat} {data_type}"
            cursor.execute(query)
            connection.commit()
        else:
            print(f'Column {stat} already exists in the {table} table.')


# Usage:
# - Call this function for each table after creating the necessary tables.
# - For example, after calling create_team_column(), you can call:
# create_rest_of_columns(cursor, 'standard_for', identifiers_and_types_standard)
# create_rest_of_columns(cursor, 'standard_against', identifiers_and_types_standard)
# create_rest_of_columns(cursor, 'shooting_for', identifiers_and_types_shooting)
# create_rest_of_columns(cursor, 'shooting_against', identifiers_and_types_shooting)
# ... and so on





def statsFor(table_name, identifiers_and_types):
    for stats, data_type in identifiers_and_types:
        stat_elements = soup.find_all(attrs={"data-stat": stats})
        team_elements = soup.find_all(attrs={"data-stat": "team"})

        for stat_element, team_element in zip(stat_elements, team_elements):
            stat_value = stat_element.get_text(strip=True)
            team_value = team_element.get_text(strip=True)

            if team_value != "Squad" and "vs" not in team_value:
                query = f"UPDATE {table_name} SET {stats} = ? WHERE team_name = ?"
                cursor.execute(query, (stat_value, team_value))
                connection.commit()



def statsAgainst(table_name, identifiers_and_types):
    for stats, data_type in identifiers_and_types:
        stat_elements = soup.find_all(attrs={"data-stat": stats})
        team_elements = soup.find_all(attrs={"data-stat": "team"})

        for stat_element, team_element in zip(stat_elements, team_elements):
            stat_value = stat_element.get_text(strip=True)
            team_value = team_element.get_text(strip=True)

            if team_value != "Squad" and "vs" in team_value:
                query = f"UPDATE {table_name} SET {stats} = ? WHERE team_name = ?"
                cursor.execute(query, (stat_value, team_value))
    connection.commit()

create_team_column()

# Loop through each table and call the necessary functions
for table_name, identifiers_and_types in tables_and_identifiers:
    create_rest_of_columns(identifiers_and_types, table_name)

# Call create_team_column() to populate the 'team_info' table
create_team_column()

# Loop through each 'for' table and call statsFor()
for table_name, identifiers_and_types in tables_and_identifiers:
    if 'for' in table_name:
        statsFor(table_name, identifiers_and_types)

# Loop through each 'against' table and call statsAgainst()
for table_name, identifiers_and_types in tables_and_identifiers:
    if 'against' in table_name:
        statsAgainst(table_name, identifiers_and_types)


def team_constant_info():
    # Create columns if they don't exist
    columns_to_be_added = ['abbreviation', 'colour_code', 'latitude', 'longitude']

    for column_name in columns_to_be_added:
        cursor.execute(f"PRAGMA table_info(team_info)")
        existing_columns = [column[1] for column in cursor.fetchall()]

        # If the column doesn't exist, add it
        if column_name not in existing_columns:
            if column_name != "latitude" and column_name != "longitude":
                data_type = "TEXT"
            else:
                data_type = "REAL"
            cursor.execute(f"ALTER TABLE team_info ADD COLUMN {column_name} {data_type}")

    # List of Premier League team information with separated coordinates
    teams_info = [
        ("Arsenal", "ARS", "#EF0107", 51.5550, -0.1084),
        ("Manchester Utd", "MUN", "#DA020E", 53.4631, -2.2913),
        ("Liverpool", "LIV", "#C8102E", 53.4308, -2.9608),
        ('Aston Villa','AVL','#95BFA3',52.5091,-1.8845),
        ("Chelsea", "CHE", "#034694", 51.4816, -0.1919),
        ("Manchester City", "MCI", "#6CADDF", 53.4830, -2.2004),
        ("Tottenham", "TOT", "#132257", 51.6043, -0.0660),
        ("West Ham", "WHU", "#7A263A", 51.5387, -0.0166),
        ("Brighton", "BHA", "#0057B8", 50.8610, -0.0834),
        ("Newcastle Utd", "NEW", "#241F20", 54.9755, -1.6215),
        ("Wolves", "WOL", "#FDB913", 52.5900, -2.1306),
        ("Bournemouth", "BOU", "#D31145", 50.7353, -1.8383),
        ("Fulham", "FUL", "#000000", 51.4750, -0.2219),
        ("Crystal Palace", "CRY", "#1B458F", 51.3983, -0.0857),
        ("Nott'ham Forest", "NOT", "#DA020E", 52.9394, -1.1332),
        ("Brentford", "BRE", "#F7EB09", 51.4881, -0.3028),
        ("Everton", "EVE", "#003399", 53.4388, -2.9664),
        ("Luton Town", "LUT", "#FFD100", 51.8841, -0.4314),
        ("Burnley", "BUR", "#6C1D45", 53.7890, -2.2300),
        ("Sheffield Utd", "SHU", "#EE2737", 53.3704, -1.4701)
    ]

    # Print the information for all teams with separated coordinates
    for team_info in teams_info:
        team_name, abbreviation, colour_code, latitude, longitude = team_info
        cursor.execute('''
                UPDATE team_info
                SET abbreviation = ?, colour_code = ?, latitude = ?, longitude = ?
                WHERE team_name = ?
            ''', (abbreviation, colour_code, latitude, longitude, team_name))

    connection.commit()


def date_and_time():
    cursor.execute("CREATE TABLE IF NOT EXISTS date_and_time (date TEXT PRIMARY KEY,time TEXT)")
    current_date = datetime_module.now().strftime("%Y-%m-%d")
    current_time = datetime_module.now().strftime("%H:%M")
    cursor.execute("UPDATE date_and_time SET date = ?,time =?",(current_date,current_time))
    connection.commit()


#Copy the db to other locations if needed
def copy_file():
    current_directory = os.getcwd()
    source_file_path = os.path.join(current_directory,"stats.db")
    path_to_copy1= r"#path/to/your/file"
    path_to_copy2 = r"path/to/your/second/file"
    try:
        # Check if the source file exists
        if os.path.exists(source_file_path):
            destination_file_path1 = os.path.join(path_to_copy1, "stats.db")
            shutil.copy2(source_file_path, destination_file_path1)
            destination_file_path2 = os.path.join(path_to_copy2,"stats.db")
            shutil.copy2(source_file_path,destination_file_path2)
            print(f"File copied successfully from {source_file_path} to {destination_file_path1}")
            print(f"File copied successfully from {source_file_path} to {destination_file_path2}")
        else:
            print("Source file not found.")
    except PermissionError:
        print("Permission error. Make sure you have the necessary permissions.")
    except Exception as e:
        print(f"An error occurred: {e}")

def convert_last_5_to_points():
    cursor.execute("PRAGMA table_info(standard_for)")
    columns = [column[1] for column in cursor.fetchall()]

    if 'last_5_points' not in columns:
        cursor.execute("ALTER TABLE standard_for ADD COLUMN last_5_points INTEGER")

    cursor.execute('SELECT team_name, last_5 FROM standard_for')
    teams_data = cursor.fetchall()

    for team, matches in teams_data:
        last_5_points = 0
        for match in matches:
            if match == "W":
                last_5_points += 3
            elif match == "D":
                last_5_points += 1
            else:
                continue

        # Update the last_5_points column for the current team
        cursor.execute('UPDATE standard_for SET last_5_points = ? WHERE team_name = ?', (last_5_points, team))

    # Commit the changes to the database
    connection.commit()

team_constant_info()
date_and_time()
#copy_file()
convert_last_5_to_points()
cursor.close()
connection.close()
