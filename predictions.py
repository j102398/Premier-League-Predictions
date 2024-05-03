import sqlite3
import os
#Firstly name the file
from flask import Flask, render_template
app = Flask(__name__)






#Connect to the fixture db
fixture_connection = sqlite3.connect('fixtures.db')
fixture_cursor = fixture_connection.cursor()

#Connect to the stats db
stats_connection = sqlite3.connect('stats.db')
stats_cursor = stats_connection.cursor()


#Define the gameweek, as it will only predict the relevant gameweeks fixtures. will also store the file with the gameweek
gameweek = 36
def name_file():
    db_folder = 'C:\\Users\\joe\\PycharmProjects\\predictions\\predictions_archive'
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

    global db_name
    db_name = os.path.join(db_folder, f"predictions_gw{gameweek}.db")

name_file()


#Connect to the predictions db
prediction_connection = sqlite3.connect(db_name)
prediction_cursor = prediction_connection.cursor()





def get_fixtures(gameweek):
    fixture_cursor.execute(f'SELECT home_team,away_team FROM fixtures WHERE gameweek = {gameweek}')
    fixture_list = fixture_cursor.fetchall()
    return fixture_list

def get_last_fixture_results(previous_home,previous_away):
    fixture_cursor.execute('SELECT home_xg,score,away_xg FROM fixtures WHERE home_team = ? AND away_team = ?',
                           (previous_home, previous_away))

    data = fixture_cursor.fetchall()

    #Sort the data into its variables
    previous_home_xg = data[0][0]
    score = data[0][1]
    previous_away_xg = data[0][2]
    return previous_home_xg,score,previous_away_xg


def get_team_stats(team):
    #Obtain points,points from last 5, goal_difference,progressive_carries,progressive_passes,xg
    stats_cursor.execute(f'SELECT points, last_5_points, goal_diff, progressive_carries, progressive_passes, xg,games FROM standard_for WHERE team_name = "{team}"')
    data = stats_cursor.fetchall()


    #Sort into individual stats
    points = data[0][0]
    last_5_points = data[0][1]
    goal_diff = data[0][2]
    progressive_carries = data[0][3]
    progressive_passes = data[0][4]
    xg = data[0][5]
    games = data[0][6]

    return points,last_5_points,goal_diff,progressive_carries,progressive_passes,xg,games

def clear_statistics_table():
    prediction_cursor.execute("DELETE FROM statistics")
    prediction_connection.commit()
def create_statistics_table():

        # Execute SQL to create the prediction table if it doesn't exist
        prediction_cursor.execute('''
            CREATE TABLE IF NOT EXISTS statistics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                gameweek INTEGER,
                home_team TEXT,
                away_team TEXT,
                score TEXT,
                home_previous_xg REAL,
                home_points INTEGER,
                home_last_5_points INTEGER,
                home_goal_diff INTEGER,
                home_progressive_carries INTEGER,
                home_progressive_passes INTEGER,
                home_xg REAL,
                away_previous_xg REAL,
                away_previous_home_xg REAL,
                away_points INTEGER,
                away_last_5_points INTEGER,
                away_goal_diff INTEGER,
                away_progressive_carries INTEGER,
                away_progressive_passes INTEGER,
                away_xg REAL,
                home_games_played INTEGER,
                away_games_played INTEGER
            )
        ''')


def insert_data(gameweek):
    # Create a new database for all the predicted outcomes

    # Get the list of fixtures
    fixture_list = get_fixtures(gameweek)

    # Create the predictions table if it doesn't exist
    create_statistics_table()

    # Create a for loop that splits the fixture into home team and away team
    for home_team, away_team in fixture_list:
        # Get the previous_home_xg, previous_score, previous_away_xg
        previous_home_xg, previous_score, previous_away_xg = get_last_fixture_results(away_team, home_team)

        # Get home stats
        home_points, home_last_5_points, home_goal_diff, home_progressive_carries, home_progressive_passes, home_xg,home_games = get_team_stats(
            home_team)

        # Get away stats
        away_points, away_last_5_points, away_goal_diff, away_progressive_carries, away_progressive_passes, away_xg,away_games = get_team_stats(
            away_team)

        # Construct the query with parameterized queries
        query = '''
            INSERT INTO statistics (gameweek, home_team, away_team, home_previous_xg, score, home_previous_xg,
                                     home_points, home_last_5_points, home_goal_diff, home_progressive_carries,
                                     home_progressive_passes, home_xg, away_previous_xg, away_previous_home_xg,
                                     away_points, away_last_5_points, away_goal_diff, away_progressive_carries,
                                     away_progressive_passes, away_xg,home_games_played,away_games_played)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?,?,?)
        '''



        # Execute the query with parameters
        prediction_cursor.execute(query, (gameweek, home_team, away_team, previous_home_xg, previous_score,
                                          previous_away_xg, home_points, home_last_5_points, home_goal_diff,
                                          home_progressive_carries, home_progressive_passes, home_xg,
                                          previous_away_xg, previous_home_xg, away_points, away_last_5_points,
                                          away_goal_diff, away_progressive_carries, away_progressive_passes,
                                          away_xg,home_games,away_games))

    # Commit the changes and close the database connection
    prediction_connection.commit()


def delete_comparisons_table():
    prediction_cursor.execute("DELETE FROM comparisons")
    prediction_connection.commit()





def create_comparisons_table():
    query = sql_create_table = '''
CREATE TABLE IF NOT EXISTS comparisons (
    fixture TEXT,
    more_previous_xg REAL,
    score INTEGER,
    more_points INTEGER,
    more_last_5_points INTEGER,
    more_goal_diff INTEGER,
    more_progressive_carries INTEGER,
    more_progressive_passes INTEGER,
    more_xg REAL
);
'''
    prediction_cursor.execute(query)

def create_scoring_criteria_table():
    # Construct the SQL query to create the scoring criteria table
    query = '''
        CREATE TABLE IF NOT EXISTS scoring_criteria (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            previous_xg_multiplier REAL,
            score_difference_multiplier REAL,
            more_points_multiplier REAL,
            more_last_5_points_multiplier REAL,
            more_goal_diff_multiplier REAL,
            more_progressive_carries_multiplier REAL,
            more_progressive_passes_multiplier REAL,
            more_xg_multiplier REAL
        )
    '''

    # Execute the query
    prediction_cursor.execute(query)

    # Commit the changes to the database
    prediction_connection.commit()

def delete_scoring_criteria_table():
    prediction_cursor.execute("DELETE FROM scoring_criteria")
    prediction_connection.commit()




def insert_comparisons():
    # Get the data for home teams
    prediction_cursor.execute(
        'SELECT home_team, home_points, home_last_5_points, home_goal_diff, home_progressive_carries, home_progressive_passes, home_xg, away_previous_xg, score FROM statistics')
    home_teams_data = prediction_cursor.fetchall()

    # Get data for away teams
    prediction_cursor.execute(
        'SELECT away_team, away_points, away_last_5_points, away_goal_diff, away_progressive_carries, away_progressive_passes, away_xg, home_previous_xg, score FROM statistics')
    away_teams_data = prediction_cursor.fetchall()

    # Insert the comparisons into the comparisons table
    for x in range(0, len(home_teams_data)):
        # Get variables
        home_team = home_teams_data[x][0]
        away_team = away_teams_data[x][0]
        home_points = home_teams_data[x][1]
        away_points = away_teams_data[x][1]
        home_last_5_points = home_teams_data[x][2]
        away_last_5_points = away_teams_data[x][2]
        home_goal_diff = home_teams_data[x][3]
        away_goal_diff = away_teams_data[x][3]
        home_progressive_carries = home_teams_data[x][4]
        away_progressive_carries = away_teams_data[x][4]
        home_progressive_passes = home_teams_data[x][5]
        away_progressive_passes = away_teams_data[x][5]
        home_xg = home_teams_data[x][6]
        away_xg = away_teams_data[x][6]
        away_previous_xg = home_teams_data[x][7]
        home_previous_xg = away_teams_data[x][7]
        score = home_teams_data[x][8]
        previous_home_goals = int(score[0])
        previous_away_goals = int(score[2])



        # Make comparisons
        # Make comparisons
        more_previous_xg = round(away_previous_xg - home_previous_xg, 2)
        more_points = round(home_points - away_points)
        more_goal_diff = round(home_goal_diff - away_goal_diff)
        more_progressive_carries = round(home_progressive_carries - away_progressive_carries)
        more_progressive_passes = round(home_progressive_passes - away_progressive_passes)
        more_xg = round(home_xg - away_xg, 2)
        more_last_5_points = home_last_5_points - away_last_5_points
        more_score = previous_away_goals - previous_home_goals

        # Construct the query
        query = '''
            INSERT INTO comparisons (fixture, more_previous_xg, more_points, more_goal_diff, more_progressive_carries, more_progressive_passes, more_xg, more_last_5_points, score)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        '''

        # Execute the query with parameters
        prediction_cursor.execute(query, (
            home_team + " vs " + away_team, more_previous_xg, more_points, more_goal_diff, more_progressive_carries,
            more_progressive_passes, more_xg, more_last_5_points, more_score))

    prediction_connection.commit()



#Create the tables



def delete_from_prediction_table():
    prediction_cursor.execute('DELETE FROM predictions')
def create_prediction_table():
    prediction_cursor.execute('''CREATE TABLE IF NOT EXISTS predictions (
    fixture TEXT PRIMARY KEY,
    previous_xg_points REAL,
    score_points REAL,
    points_points REAL,
    last_5_points_points REAL,
    goal_diff_points REAL,
    progressive_carries_points REAL,
    progressive_passes_points REAL,
    xg_points REAL,
    total_points REAL
)''')
    prediction_connection.commit()






def run_program():
    # Clear existing statistics table

    create_statistics_table()
    clear_statistics_table()
    create_statistics_table()
    # Insert data into statistics table for a specific gameweek
    insert_data(gameweek)

    # Create comparisons table
    create_comparisons_table()
    delete_comparisons_table()
    create_comparisons_table()
    # Insert comparisons data
    insert_comparisons()

    # Delete existing scoring criteria table
    create_scoring_criteria_table()
    delete_scoring_criteria_table()
    create_scoring_criteria_table()
    # Create scoring criteria table
    create_scoring_criteria_table()
    delete_scoring_criteria_table()
    create_scoring_criteria_table()

    # Create prediction table

    create_prediction_table()
    delete_from_prediction_table()
    create_prediction_table()



# Execute the program
run_program()


