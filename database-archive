import datetime
import requests
from bs4 import BeautifulSoup
import sqlite3
from datetime import datetime
import os

def scrape_and_store_team_stats():
    pageToScrape = requests.get('https://fbref.com/en/comps/9/Premier-League-Stats')
    soup = BeautifulSoup(pageToScrape.text, "html.parser")

    # Player info
    players_used_elements = soup.find_all(attrs={"data-stat": "players_used"})
    team_elements = soup.find_all(attrs={"data-stat": "team"})
    nationality_elements = soup.find_all(attrs={"data-stat": "nationality"})
    position_elements = soup.find_all(attrs={"data-stat": "position"})
    age_elements = soup.find_all(attrs={"data-stat": "avg_age"})
    possession_elements = soup.find_all(attrs={"data-stat": "possession"})

    # Starts and minutes
    games_elements = soup.find_all(attrs={"data-stat": "games"})
    start_element = soup.find_all(attrs={"data-stat": "games_starts"})
    minutes_elements = soup.find_all(attrs={"data-stat": "minutes"})
    ninety_mins = soup.find_all(attrs={"data-stat": "minutes_90s"})

    # G+A
    goals_elements = soup.find_all(attrs={"data-stat": "goals"})
    assist_elements = soup.find_all(attrs={"data-stat": "assists"})
    goals_assists_elements = soup.find_all(attrs={"data-stat": "goals_assists"})
    non_pen_goals_elements = soup.find_all(attrs={"data-stat": "goals_pens"})
    penalties_made_elements = soup.find_all(attrs={"data-stat": "pens_made"})

    # Cards
    yellow_cards_elements = soup.find_all(attrs={"data-stat": "cards_yellow"})
    red_cards_elements = soup.find_all(attrs={"data-stat": "cards_red"})

    # Expected stats
    xg_elements = soup.find_all(attrs={"data-stat": "xg"})
    npxg_elements = soup.find_all(attrs={"data-stat": "npxg"})
    xassists_elements = soup.find_all(attrs={"data-stat": "xg_assist"})

    # Progression
    progressive_carries_elements = soup.find_all(attrs={"data-stat": "progressive_carries"})
    progressive_passes_elements_elements = soup.find_all(attrs={"data-stat": "progressive_passes"})
    progressive_passes_recieved_elements = soup.find_all(attrs={"data-stat": "progressive_passes_recieved"})

    # Stats per 90
    goalsp90_elements = soup.find_all(attrs={"data-stat": "goals_per90"})
    assistsp90_elements = soup.find_all(attrs={"data-stat": "assists_per90"})
    goalsassistsp90_elements = soup.find_all(attrs={"data-stat": "goals_assists_per90"})
    non_pen_goalsp90_elements = soup.find_all(attrs={"data-stat": "goals_pens_per90"})

    current_datetime = datetime.now()
    date_and_time = current_datetime.strftime("%d/%m/%Y %H:%M:%S")#
    #Get the Date for the name of the database file name

    date = current_datetime.strftime('%d.%m.%Y')
    time = current_datetime.strftime('%H.%M')


    # Specify the folder path
    db_folder = "C:\\Users\\joe\\PycharmProjects\\automatic_database\\Database-Archive"

    # Check if the folder exists
    if not os.path.exists(db_folder):
        try:
            # Create the folder
            os.makedirs(db_folder)
            print("Folder '" + db_folder + "' created successfully.")
        except Exception as e:
            print("An error occurred while creating the folder: " + str(e))
    else:
        print("Folder '" + db_folder + "' already exists.")

    db_name = db_folder + "\\PremierLeagueStats_" + date + "_at_" + time + ".db"



    connection = sqlite3.connect(db_name)
    cursor = connection.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS teamStats (
            id INTEGER PRIMARY KEY,
            team_name TEXT,
            xg_value REAL,
            goals_scored INTEGER
        )
    ''')

    cursor.execute("PRAGMA table_info(teamStats)")
    columns = cursor.fetchall()
    column_names = [col[1] for col in columns]

    ColumnsToBeAdded = ['xg_conceded', 'goals_conceded', 'average_age', 'yellow_cards', 'red_cards', 'pens_made',
                        'progressive_carries', 'team_abbreviation', 'colour_code']
    TypeOfData = [' REAL', ' INTEGER', ' REAL', ' INTEGER', 'INTEGER', 'INTEGER', 'INTEGER', 'TEXT', 'TEXT']

    for column, dataType in zip(ColumnsToBeAdded, TypeOfData):
        if column not in column_names:
            query = "ALTER TABLE teamStats ADD COLUMN " + column + " " + dataType
            cursor.execute(query)
            connection.commit()

    if 'date_and_time' not in column_names:
        cursor.execute('''
            ALTER TABLE teamStats 
            ADD COLUMN date_and_time TEXT 
        ''')
        connection.commit()

    cursor.execute('DELETE FROM teamStats')


    def create_team_columns_insert_time():
        row = 0
        for team in team_elements:
            team_text = team.get_text(strip=True)
            if team_text == "Squad":
                continue
            else:
                cursor.execute('INSERT INTO teamStats (team_name,date_and_time) VALUES (?,?)',
                               (team_text, date_and_time))
            row += 1
            if row == 20:
                break

    def statsPerTeam():
        for team, xg, goals, players, age, yellow, red, pens_made, progressive_carries in zip(
                team_elements, xg_elements, goals_elements, players_used_elements,
                age_elements, yellow_cards_elements, red_cards_elements,
                penalties_made_elements, progressive_carries_elements
        ):
            team_value = team.get_text(strip=True)

            if "vs" not in team_value and team_value != "Squad":
                xg_value = float(xg.get_text(strip=True))
                goals_value = int(goals.get_text(strip=True))
                age_value = float(age.get_text(strip=True))
                yellow_value = int(yellow.get_text(strip=True))
                red_value = int(red.get_text(strip=True))
                pens_made_value = int(pens_made.get_text(strip=True))
                progressive_carries_value = int(progressive_carries.get_text(strip=True))
                cursor.execute('''
                    UPDATE teamStats
                    SET xg_value = ?,
                        goals_scored = ?,
                        average_age = ?,
                        yellow_cards = ?,
                        red_cards = ?,
                        pens_made = ?,
                        progressive_carries = ?
                    WHERE team_name = ?
                ''', (
                    xg_value, goals_value, age_value, yellow_value, red_value,
                    pens_made_value, progressive_carries_value, team_value
                ))
                connection.commit()

    def statsAgainstTeam():
        row = 0
        for team, xg_conceded, goals_conceded, player in zip(team_elements, xg_elements, goals_elements,
                                                             players_used_elements):
            player_count = player.get_text(strip=True)
            if player_count:
                team_text = team.get_text(strip=True)
                if team_text != "Squad" and "vs" in team_text:
                    xg_text = xg_conceded.get_text(strip=True)
                    goals_text = goals_conceded.get_text(strip=True)
                    team_name = team_text.split('vs ')[1]
                    xg_value = float(xg_text)
                    goals_count = int(goals_text)
                    print(team_name)
                    cursor.execute('''
                        UPDATE teamStats 
                        SET xg_conceded = ?, goals_conceded = ?
                        WHERE team_name = ?
                    ''', (xg_value, goals_count, team_name))

                    connection.commit()
                    row += 1

                if row == 20:
                    break

    def TeamConstantInfo():
        team_abbreviations = {
            'Arsenal': 'ARS',
            'Aston Villa': 'AVL',
            'Bournemouth': 'BOU',
            'Brentford': 'BRE',
            'Brighton': 'BHA',
            'Burnley': 'BUR',
            'Chelsea': 'CHE',
            'Crystal Palace': 'CRY',
            'Everton': 'EVE',
            'Fulham': 'FUL',
            'Liverpool': 'LIV',
            'Luton Town': 'LUT',
            'Manchester City': 'MCI',
            'Manchester Utd': 'MUN',
            'Newcastle Utd': 'NEW',
            "Nott'ham Forest": 'NOT',
            'Sheffield Utd': 'SHU',
            'Tottenham': 'TOT',
            'West Ham': 'WHU',
            'Wolves': 'WOL'
        }

        team_colours_hex = {
            'Arsenal': '#EF0107',
            'Aston Villa': '#95BFE5',
            'Bournemouth': '#DA291C',
            'Brentford': '#FFDB00',
            'Brighton': '#0057B8',
            'Burnley': '#6C1D45',
            'Chelsea': '#034694',
            'Crystal Palace': '#1B458F',
            'Everton': '#003399',
            'Fulham': '#000000',
            'Liverpool': '#C8102E',
            'Luton Town': '#FFA500',
            'Manchester City': '#6CADDF',
            'Manchester Utd': '#DA291C',
            'Newcastle Utd': '#241F20',
            "Nott'ham Forest": '#FFCC00',
            'Sheffield Utd': '#EE2737',
            'Tottenham': '#132257',
            'West Ham': '#7A263A',
            'Wolves': '#FDB913'
        }

        for team, abbreviation in team_abbreviations.items():
            hex_code = team_colours_hex.get(team, '')
            cursor.execute(
                'UPDATE teamStats SET team_abbreviation = ?, colour_code = ? WHERE team_name = ?',
                (abbreviation, hex_code, team)
            )
            connection.commit()

    create_team_columns_insert_time()
    statsPerTeam()
    statsAgainstTeam()
    TeamConstantInfo()

   
    cursor.close()
    connection.close()

# Call the function to execute the code

scrape_and_store_team_stats()







#PLEASE REFER TO THE READ.ME ON THE GITHUB , THIS IS FOR TASK SCHEDULER SET UP
def task_schedule_details():


    import sys
    import platform
    import importlib.util

    print("Python EXE     : " + sys.executable)
    print("Architecture   : " + platform.architecture()[0])

    # Specify the module name
    module_name = "arcpy"

    # Try to find the module
    try:
        spec = importlib.util.find_spec(module_name)
        path_to_arcpy = spec.origin if spec else "Not found"
    except ImportError:
        path_to_arcpy = "Not found"

    print("Path to arcpy  : " + path_to_arcpy)

    input("\n\nPress ENTER to quit")


#task_schedule_details()
