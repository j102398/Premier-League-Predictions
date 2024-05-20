import sqlite3
import os

# Connect to the fixture db
fixture_connection = sqlite3.connect('fixtures.db')
fixture_cursor = fixture_connection.cursor()

# Connect to the stats db
stats_connection = sqlite3.connect('stats.db')
stats_cursor = stats_connection.cursor()

# Define the gameweek, as it will only predict the relevant gameweeks fixtures. will also store the file with the gameweek
gameweek = 39


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

# Connect to the predictions db
prediction_connection = sqlite3.connect(db_name)
prediction_cursor = prediction_connection.cursor()


def get_fixtures(gameweek):
    fixture_cursor.execute(f'SELECT home_team,away_team FROM fixtures WHERE gameweek = {gameweek}')
    fixture_list = fixture_cursor.fetchall()
    return fixture_list


def get_last_fixture_results(previous_home, previous_away):
    fixture_cursor.execute('SELECT home_xg,score,away_xg FROM fixtures WHERE home_team = ? AND away_team = ?',
                           (previous_home, previous_away))

    data = fixture_cursor.fetchall()

    # Sort the data into its variables
    previous_home_xg = data[0][0]
    score = data[0][1]
    previous_away_xg = data[0][2]
    return previous_home_xg, score, previous_away_xg


def get_team_stats(team):
    # Obtain points,points from last 5, goal_difference,progressive_carries,progressive_passes,xg
    stats_cursor.execute(
        f'SELECT points, last_5_points, goal_diff, progressive_carries, progressive_passes, xg,games,possession,goals_for,xg_against FROM standard_for WHERE team_name = "{team}"')
    data = stats_cursor.fetchall()

    # Sort into individual stats
    points = data[0][0]
    last_5_points = data[0][1]
    goal_diff = data[0][2]
    progressive_carries = data[0][3]
    progressive_passes = data[0][4]
    xg = data[0][5]
    games = data[0][6]
    possession = data[0][7]
    goals = data[0][8]
    xg_against = data[0][9]
    # Get
    return points, last_5_points, goal_diff, progressive_carries, progressive_passes, xg, games, possession,goals,xg_against


def clear_statistics_table():
    try:
        prediction_cursor.execute("DELETE FROM statistics")
        prediction_connection.commit()
    except:
        pass

def create_statistics_table():
    # Execute SQL to create the prediction table if it doesn't exist
    prediction_cursor.execute('''
            CREATE TABLE IF NOT EXISTS statistics (
                gameweek INTEGER,
                home_team TEXT,
                away_team TEXT,
                previous_score TEXT,
                home_previous_xg REAL,
                home_points INTEGER,
                home_last_5_points INTEGER,
                home_goal_diff INTEGER,
                home_progressive_carries INTEGER,
                home_progressive_passes INTEGER,
                home_xg REAL,
                away_previous_xg REAL,
                away_points INTEGER,
                away_last_5_points INTEGER,
                away_goal_diff INTEGER,
                away_progressive_carries INTEGER,
                away_progressive_passes INTEGER,
                away_xg REAL,
                home_games_played INTEGER,
                away_games_played INTEGER,
                home_possession REAL,
                away_possession REAL,
                home_goals INTEGER,
                away_goals INTEGER,
                home_xg_against REAL,
                away_xg_against REAL
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
        away_previous_xg, previous_score, home_previous_xg = get_last_fixture_results(away_team, home_team)

        # Get home stats
        home_points, home_last_5_points, home_goal_diff, home_progressive_carries, home_progressive_passes, home_xg, home_games, home_possession, home_progressive_passes_received,home_goals,home_xg_against= get_team_stats(
            home_team)

        # Get away stats
        away_points, away_last_5_points, away_goal_diff, away_progressive_carries, away_progressive_passes, away_xg, away_games, away_possession, away_progressive_passes_received,away_goals,away_xg_against = get_team_stats(
            away_team)

        # Construct the query with parameterized queries
        query = '''
            INSERT INTO statistics (
                gameweek, home_team, away_team, previous_score, home_previous_xg, home_points,
                home_last_5_points, home_goal_diff, home_progressive_carries, home_progressive_passes,
                home_xg, away_previous_xg, away_points, away_last_5_points, away_goal_diff,
                away_progressive_carries, away_progressive_passes, away_xg, home_games_played,
                away_games_played, home_possession,  away_possession,home_goals,away_goals,home_xg_against,away_xg_against
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?,?,?)
        '''

        # Execute the query with parameters
        prediction_cursor.execute(query, (
            gameweek, home_team, away_team, previous_score, home_previous_xg, home_points,
            home_last_5_points, home_goal_diff, home_progressive_carries, home_progressive_passes, home_xg,
            away_previous_xg, away_points, away_last_5_points, away_goal_diff, away_progressive_carries,
            away_progressive_passes, away_xg, home_games, away_games, home_possession,
             away_possession, home_goals,away_goals,home_xg_against,away_xg_against
        ))

    # Commit the changes and close the database connection
    prediction_connection.commit()




def run_program():
    try:
        # Clear existing statistics table
        clear_statistics_table()

        # Create statistics table and insert data
        create_statistics_table()
        insert_data(gameweek)


        print("Program execution completed successfully.")

    except Exception as e:
        print("An error occurred during program execution:", str(e))

# Execute the program
run_program()

