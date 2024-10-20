#import relevant libraries
import sqlite3






#mathematical functions required for the predictions
def factorial(number):
    if number == 0:
        return 1
    else:
        total = 1
        for i in range(number, 0, -1):
            total *= i

        return total

def ppd(lambda_value, x):  #  Where X ~ Po(λ),P(X=x)
    ##Constants
    e = 2.718281828459045
    probability = (e ** (-lambda_value)) * ((lambda_value ** x) / factorial(x))
    return probability

def probable_goals(lambda_value):
    #testing the probability of 0-10 goals:
    probability_list = []
    for goals in range(0,11):
        probability_list.append(ppd(lambda_value,goals))

    #finding most probable goal count
    highest_probability = max(probability_list)
    probable_goals = probability_list.index(highest_probability)

    return probable_goals


class Predictions:
    def __init__(self,db_name,previous_db_file_path,gameweek):
        self.previous_connection = sqlite3.connect(previous_db_file_path)
        self.previous_cursor = self.previous_connection.cursor()
        #consider if the name contains .db in already
        if ".db" in db_name:
            self.connection = sqlite3.connect(db_name)

        else:

            self.connection = sqlite3.connect(f"{db_name}.db")
        self.cursor = self.connection.cursor()
        self.gameweek = str(gameweek) #when retrieving data, the gameweek will be in string format
        self.primary_table = f"gameweek_{self.gameweek}"
    def create_table(self):

        try:
            self.cursor.execute(f'''
                  CREATE TABLE IF NOT EXISTS gameweek_{self.gameweek} (
                    fixture TEXT PRIMARY KEY,
                    home_team TEXT,
                    away_team TEXT,
                    home_previous_xg REAL,
                    away_previous_xg REAL,
                    home_team_home_goals INTEGER,
                    away_team_away_goals INTEGER,
                    home_team_home_goals_conceded INTEGER,
                    away_team_away_goals_conceded INTEGER,
                    home_team_home_xg REAL,
                    away_team_away_xg REAL,
                    home_team_home_xg_conceded REAL,
                    away_team_away_xg_conceded REAL,
                    home_team_away_goals INTEGER,
                    home_team_away_xg REAL,
                    home_team_away_goals_conceded INTEGER,
                    home_team_away_xg_conceded REAL,
                    away_team_home_goals INTEGER,
                    away_team_home_xg REAL,
                    away_team_home_goals_conceded INTEGER,
                    away_team_home_xg_conceded REAL,
                    home_team_home_games INTEGER,
                    home_team_away_games INTEGER,
                    away_team_away_games INTEGER,
                    away_team_home_games INTEGER
                      
                  )
              ''')
            self.connection.commit()
        except Exception as error:
            print(f'An error occured : {error}')

    def insert_fixtures(self):
        try:

            #retrieving all the relevant fixtures we will predict
            self.previous_cursor.execute('SELECT fixture,home_team,away_team FROM fixtures WHERE gameweek = ?',(self.gameweek,))
            data = self.previous_cursor.fetchall()

            #inserting this into the prediction database
            for fixture,home_team,away_team in data:
                self.cursor.execute(F'INSERT INTO gameweek_{self.gameweek} (fixture,home_team,away_team) VALUES (?,?,?)',(fixture,home_team,away_team,))
            self.connection.commit()

        except Exception as error:
            print(f"An error occured : {error}")

    def insert_stats(self): #we will be collating the data manually from each individual game, as we want to be able to collect data for the purpose of backtesting
        #retrieving all the stats from when at home
        def home_stats(team): #this is a function for BOTH away and home teams, just collects stats from when a team was playing at home
            #we only can consider the stats from the games that had happened before the gameweek, as we will use this for backtesting
            self.previous_cursor.execute('SELECT home_xg,score,away_xg FROM fixtures WHERE home_team = ? AND gameweek < ?',(team,self.gameweek,))
            stats = self.previous_cursor.fetchall()


            #initialise counters
            games_counter = 0
            xg_counter = 0
            goals_counter = 0
            goals_conceded_counter = 0
            xg_conceded_counter = 0
            for home_xg,score,away_xg in stats:
                home_goals, home_goals_conceded = score.split('–')

                #increase the stats by their respective amounts
                games_counter += 1  # increment the amount of home games by one
                xg_counter += home_xg
                goals_counter += int(home_goals)
                goals_conceded_counter += int(home_goals_conceded)
                xg_conceded_counter += away_xg

            return games_counter,xg_counter,goals_counter,xg_conceded_counter,goals_conceded_counter

        #retrieving all the stats from when away
        def away_stats(team):#this is a function for BOTH away and home teams, just collects stats from when a team was playing at home
            #we only can consider the stats from the games that had happened before the gameweek, as we will use this for backtesting
            self.previous_cursor.execute(
                'SELECT home_xg,score,away_xg FROM fixtures WHERE away_team = ? AND gameweek < ?',
                (team, self.gameweek,))
            stats = self.previous_cursor.fetchall()

            # initialise counters
            games_counter = 0
            xg_counter = 0
            goals_counter = 0
            goals_conceded_counter = 0
            xg_conceded_counter = 0
            for home_xg,score,away_xg in stats:
                away_goals_conceded, away_goals = score.split('–')

                #increase the stats by their respective amounts
                games_counter += 1  # increment the amount of home games by one
                xg_counter += away_xg
                goals_counter += int(away_goals)
                goals_conceded_counter += int(away_goals_conceded)
                xg_conceded_counter += home_xg
            return games_counter,xg_counter,goals_counter,xg_conceded_counter,goals_conceded_counter


        #go through the list of fixtures and insert the stats accordingly
        self.cursor.execute(f'SELECT home_team,away_team FROM gameweek_{self.gameweek}')
        team_list = self.cursor.fetchall()

        for home_team,away_team in team_list:
            #home team stats
            home_team_home_games, home_team_home_xg, home_team_home_goals, home_team_home_xg_conceded, home_team_home_goals_conceded = home_stats(home_team)
            home_team_away_games, home_team_away_xg, home_team_away_goals, home_team_away_xg_conceded, home_team_away_goals_conceded = away_stats(home_team)

            #away team stats
            away_team_home_games, away_team_home_xg, away_team_home_goals, away_team_home_xg_conceded, away_team_home_goals_conceded = home_stats(away_team)
            away_team_away_games, away_team_away_xg, away_team_away_goals, away_team_away_xg_conceded, away_team_away_goals_conceded = away_stats(away_team)

            #find the previous xg from the previous fixtures
            try:

                self.previous_cursor.execute('SELECT home_xg,away_xg FROM fixtures WHERE home_team = ? and away_team = ?',(away_team,home_team,))
                away_previous_xg,home_previous_xg = self.previous_cursor.fetchone()

            except Exception as error:

                print(f"An error occured: {error}")


            #insert these stats
            self.cursor.execute(f'''
                UPDATE gameweek_{self.gameweek} 
                SET 
                    home_previous_xg = ?,
                    away_previous_xg = ?,
                    home_team_home_games = ?, 
                    home_team_home_xg = ?, 
                    home_team_home_goals = ?, 
                    home_team_home_xg_conceded = ?, 
                    home_team_home_goals_conceded = ?, 
                    away_team_home_games = ?, 
                    away_team_home_xg = ?, 
                    away_team_home_goals = ?, 
                    away_team_home_xg_conceded = ?, 
                    away_team_home_goals_conceded = ?, 
                    home_team_away_games = ?, 
                    home_team_away_xg = ?, 
                    home_team_away_goals = ?, 
                    home_team_away_xg_conceded = ?, 
                    home_team_away_goals_conceded = ?, 
                    away_team_away_games = ?, 
                    away_team_away_xg = ?, 
                    away_team_away_goals = ?, 
                    away_team_away_xg_conceded = ?, 
                    away_team_away_goals_conceded = ?
                WHERE home_team = ? AND away_team = ?
            ''', (
                home_previous_xg,away_previous_xg,
                home_team_home_games, home_team_home_xg, home_team_home_goals, home_team_home_xg_conceded,
                home_team_home_goals_conceded,
                away_team_home_games, away_team_home_xg, away_team_home_goals, away_team_home_xg_conceded,
                away_team_home_goals_conceded,
                home_team_away_games, home_team_away_xg, home_team_away_goals, home_team_away_xg_conceded,
                home_team_away_goals_conceded,
                away_team_away_games, away_team_away_xg, away_team_away_goals, away_team_away_xg_conceded,
                away_team_away_goals_conceded,
                home_team, away_team  # Add the home_team and away_team variables here
            ))
            self.connection.commit()

    def predictions(self): #will rework this properly after gamework 20
        #get list of fixtures and stats
        def simple_models(): #poisson model based off just
            #retrieve relevant data
            self.cursor.execute(f'SELECT fixture,home_team_home_goals,home_team_away_goals,away_team_away_goals,away_team_home_goals,away_team_away_games,home_team_away_games,home_team_home_games,away_team_home_games FROM gameweek_{self.gameweek}')
            data = self.cursor.fetchall()
            for fixture,home_team_home_goals,home_team_away_goals,away_team_away_goals,away_team_home_goals,away_team_away_games,home_team_away_games,home_team_home_games,away_team_home_games in data:
                #model 1:
                #Home goals ∿ Po(λ) : Where λ is avg  goals
                #away Goals ∿ Po(λ) : Where λ is avg  goals

                #Model 2:
                # Home goals ∿ Po(λ) : Where λ is avg  goals scored at home
                # away Goals ∿ Po(λ) : Where λ is avg  goals scored  away

                # model 3:
                # Home goals ∿ Po(λ) : Where λ is (avg  goals scored by home team + avg goals conceded by away team / 2)
                # away Goals ∿ Po(λ) : Where λ is (avg  goals scored by away team + avg goals conceded by home team / 2)

                home_lambda_1 = (home_team_home_goals + home_team_away_goals) / (home_team_away_games + home_team_home_games)
                away_lambda_1 = (away_team_away_goals + away_team_home_games) / (away_team_away_games + away_team_home_games)

                home_lambda_2 = (home_team_home_goals) / (home_team_home_games)
                away_lambda_2 = (away_team_away_goals) / (away_team_away_games)


                self.cursor.execute(f'SELECT home_team_home_goals_conceded,away_team_home_goals_conceded,home_team_away_goals_conceded,away_team_away_goals_conceded FROM gameweek_{self.gameweek} WHERE fixture = ?',(fixture,))
                home_team_home_goals_conceded,away_team_home_goals_conceded,home_team_away_goals_conceded,away_team_away_goals_conceded = self.cursor.fetchone()

                home_lambda_3 = ((home_lambda_1) + ((away_team_away_goals_conceded + away_team_home_goals_conceded) / (away_team_away_games +away_team_home_games)))
                away_lambda_3 = (away_lambda_1 + ((home_team_home_goals_conceded + home_team_away_goals_conceded) / (
                            home_team_home_games + home_team_away_games))) / 2


                print(f"Method 1 Prediction for {fixture} : {probable_goals(home_lambda_1)} - {probable_goals(away_lambda_1)} ")
                print(f"Method 2 Prediction for {fixture} : {probable_goals(home_lambda_2)} - {probable_goals(away_lambda_2)} ")
                print(f"Method 3 Prediction for {fixture} : {probable_goals(home_lambda_3)} - {probable_goals(away_lambda_3)}")
                print(f"")



        def complex_models(): #this model works of xg
            #Model 3:
            # Home goals ∿ Po(λ) : Where λ is (previous xg * (home goals scored / xg won) * (away team goals conceded / away team xg conceded)
            # Away goals ∿ Po(λ) : Where λ is (previous xg * (away goals scored / xg won) * (home team goals conceded / home team xg conceded)

            #Model 4 : the same but only for xg , goals scored at home
            pass

        simple_models()





test = Predictions("predictions","premier_league.db",8)
test.create_table()
test.insert_fixtures()
test.insert_stats()
test.predictions()
