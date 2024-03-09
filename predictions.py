import sqlite3
import os
#Firstly name the file







#Connect to the fixture db
fixture_connection = sqlite3.connect('fixtures.db')
fixture_cursor = fixture_connection.cursor()

#Connect to the stats db
stats_connection = sqlite3.connect('stats.db')
stats_cursor = stats_connection.cursor()


#Define the gameweek, as it will only predict the relevant gameweeks fixtures. will also store the file with the gameweek
gameweek = 28

def name_file():
    db_folder = "C:\\path\\to\\your\\desired\\folder"
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
    stats_cursor.execute(f'SELECT points, last_5_points, goal_diff, progressive_carries, progressive_passes, xg FROM standard_for WHERE team_name = "{team}"')
    data = stats_cursor.fetchall()

    #Sort into individual stats
    points = data[0][0]
    last_5_points = data[0][1]
    goal_diff = data[0][2]
    progressive_carries = data[0][3]
    progressive_passes = data[0][4]
    xg = data[0][5]
    return points,last_5_points,goal_diff,progressive_carries,progressive_passes,xg

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
                away_xg REAL
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
        home_points, home_last_5_points, home_goal_diff, home_progressive_carries, home_progressive_passes, home_xg = get_team_stats(
            home_team)

        # Get away stats
        away_points, away_last_5_points, away_goal_diff, away_progressive_carries, away_progressive_passes, away_xg = get_team_stats(
            away_team)

        # Construct the query with parameterized queries
        query = '''
            INSERT INTO statistics (gameweek, home_team, away_team, home_previous_xg, score, home_previous_xg,
                                     home_points, home_last_5_points, home_goal_diff, home_progressive_carries,
                                     home_progressive_passes, home_xg, away_previous_xg, away_previous_home_xg,
                                     away_points, away_last_5_points, away_goal_diff, away_progressive_carries,
                                     away_progressive_passes, away_xg)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        '''



        # Execute the query with parameters
        prediction_cursor.execute(query, (gameweek, home_team, away_team, previous_home_xg, previous_score,
                                          previous_away_xg, home_points, home_last_5_points, home_goal_diff,
                                          home_progressive_carries, home_progressive_passes, home_xg,
                                          previous_away_xg, previous_home_xg, away_points, away_last_5_points,
                                          away_goal_diff, away_progressive_carries, away_progressive_passes,
                                          away_xg))

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



#Get the user to determine how much weight should be placed on different stats
def determine_points_criteria():
    #We are going to use a scoring criteria to predict the outcome of games.

    previous_xg_multiplier = 3


    score_difference_multiplier = 2


    more_points_multiplier = 1


    more_last_5_points_multiplier = 3

    more_goal_diff_multiplier = 2

    more_progressive_carries_multiplier = 0.01

    more_progressive_passes_multiplier = 0.01

    more_xg_multiplier = 2

    return previous_xg_multiplier,score_difference_multiplier,more_points_multiplier,more_last_5_points_multiplier,more_goal_diff_multiplier,more_progressive_carries_multiplier,more_progressive_passes_multiplier,more_xg_multiplier

def store_scoring_criteria():
    scoring_criteria = determine_points_criteria()
    query = f'''
          INSERT INTO scoring_criteria (
              previous_xg_multiplier,
              score_difference_multiplier,
              more_points_multiplier,
              more_last_5_points_multiplier,
              more_goal_diff_multiplier,
              more_progressive_carries_multiplier,
              more_progressive_passes_multiplier,
              more_xg_multiplier
          )
          VALUES (
              {scoring_criteria[0]},
              {scoring_criteria[1]},
              {scoring_criteria[2]},
              {scoring_criteria[3]},
              {scoring_criteria[4]},
              {scoring_criteria[5]},
              {scoring_criteria[6]},
              {scoring_criteria[7]}
          )
      '''

    # Execute the query
    prediction_cursor.execute(query)

    # Commit the changes to the database
    prediction_connection.commit()
    assign_points(scoring_criteria[0], scoring_criteria[1],
                  scoring_criteria[2], scoring_criteria[3], scoring_criteria[4],
                  scoring_criteria[5], scoring_criteria[6], scoring_criteria[7])


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




def assign_points(previous_xg_multiplier, score_difference_multiplier,
                  more_points_multiplier, more_last_5_points_multiplier, more_goal_diff_multiplier,
                  more_progressive_carries_multiplier, more_progressive_passes_multiplier, more_xg_multiplier):
    # Get all the data from the comparisons table
    prediction_cursor.execute('SELECT fixture, more_previous_xg, score, more_points, more_last_5_points, '
                              'more_goal_diff, more_progressive_carries, more_progressive_passes, more_xg '
                              'FROM comparisons')
    data = prediction_cursor.fetchall()

    for x in range(len(data)):
        fixture = data[x][0]
        more_previous_xg = float(data[x][1])  # Convert to float
        score = int(data[x][2])  # Convert to integer
        more_points = int(data[x][3])  # Convert to integer
        more_last_5_points = int(data[x][4])  # Convert to integer
        more_goal_diff = int(data[x][5])  # Convert to integer
        more_progressive_carries = int(data[x][6])  # Convert to integer
        more_progressive_passes = int(data[x][7])  # Convert to integer
        more_xg = float(data[x][8])  # Convert to float

        # Calculate points for each criterion
        previous_xg_points = more_previous_xg * previous_xg_multiplier
        score_points = score * score_difference_multiplier
        points_points = more_points * more_points_multiplier
        last_5_points_points = more_last_5_points * more_last_5_points_multiplier
        goal_diff_points = more_goal_diff * more_goal_diff_multiplier
        progressive_carries_points = more_progressive_carries * more_progressive_carries_multiplier
        progressive_passes_points = more_progressive_passes * more_progressive_passes_multiplier
        xg_points = more_xg * more_xg_multiplier

        total_points = (previous_xg_points + score_points + points_points +
                        last_5_points_points + goal_diff_points +
                        progressive_carries_points + progressive_passes_points + xg_points)

        # Here, you would typically have some logic to store or use these points, such as updating a database
        # For example, you can insert these points into the predictions table
        prediction_cursor.execute('''INSERT INTO predictions (fixture, previous_xg_points, score_points, 
                                    points_points, last_5_points_points, goal_diff_points, 
                                    progressive_carries_points, progressive_passes_points, xg_points,total_points) 
                                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?,?)''',
                                  (fixture, previous_xg_points, score_points, points_points,
                                   last_5_points_points, goal_diff_points, progressive_carries_points,
                                   progressive_passes_points, xg_points,total_points))



    # Commit the transaction after all insertions
    prediction_cursor.connection.commit()




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

    # Store scoring criteria (assuming it needs to be stored again, as per your original code)
    store_scoring_criteria()


# Execute the program
run_program()




