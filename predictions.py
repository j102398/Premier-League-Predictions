#Import relevant libraries
import sqlite3
import requests
from bs4 import BeautifulSoup

previous_db_file_path = "C:\\Users\\joe\\PycharmProjects\\fixture_db\\fixtures.db" #conect to the database with the fixtures

#Miscellaneous
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

class Database:
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
                    gameweek INTEGER,
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
                    home_team_home_conceded_xg REAL,
                    away_team_away_conceded_xg REAL,
                    home_team_away_goals INTEGER,
                    home_team_away_xg REAL,
                    home_team_away_goals_conceded INTEGER,
                    home_team_away_xg_conceded REAL,
                    away_team_home_goals INTEGER,
                    away_team_home_xg REAL,
                    away_team_home_goals_conceded INTEGER,
                    away_team_home_xg_conceded REAL
                )
            ''')
            self.connection.commit()
        except Exception as error:
            print(f'An error occured : {error}')


    def get_fixtures(self): #get the fixture, home team and away team from the specified gameweek

        try:
            self.previous_cursor.execute('SELECT fixture,home_team,away_team FROM fixtures WHERE gameweek = ?',(self.gameweek,))
            data = self.previous_cursor.fetchall()

            #Loop through the data, inserting the fixtures into our new database
            for fixture,home_team,away_team in data:
                self.cursor.execute(f'INSERT INTO {self.primary_table} (fixture,home_team,away_team,gameweek) VALUES (?,?,?,?)',(fixture,home_team,away_team,self.gameweek))
                self.connection.commit()

        except: #if the fixtures have already been inserted
            pass

    def insert_data_simple(self): #insert the data that doesn't require manual manipulation
        #we are retrieving previous xg from last game
        self.cursor.execute(f'SELECT home_team,away_team FROM {self.primary_table}') #retrieve a list of home teams and away teams this gameweek
        teams = self.cursor.fetchall()
        for previous_away_team,previous_home_team in teams: #current home team is the previous away team etc.
            home_team = previous_away_team
            away_team = previous_home_team
            self.previous_cursor.execute('SELECT home_xg,away_xg FROM fixtures WHERE home_team = ? AND away_team = ? AND gameweek < ?',(previous_home_team,previous_away_team,self.gameweek)) #include the gameweek clause for the purpose of back testing. only want to consider the available data at the time
            away_previous_xg,home_previous_xg = self.previous_cursor.fetchone() #the previous xg of the CURRENT away team


            #insert this data into the new database
            self.cursor.execute(f'UPDATE {self.primary_table} SET home_previous_xg =?,away_previous_xg = ? WHERE home_team = ? AND away_team = ?',(float(home_previous_xg),float(away_previous_xg),home_team,away_team))
            self.connection.commit()







    def insert_data_complex(self): #accounting for home and away bias
        def sort_goals(score):
            home_goals_str, away_goals_str = score.split("–")
            return int(home_goals_str), int(away_goals_str)



        #get the list of teams
        self.cursor.execute(f'SELECT home_team,away_team FROM {self.primary_table}')  # retrieve a list of home teams and away teams this gameweek
        teams = self.cursor.fetchall()

        home_team_home_dictionary = {} #create a dictionary to track the stats for each home team when at home
        home_team_away_dictionary = {} #create a dictionary to track the stats for the home team when playing away
        away_team_home_dictionary = {} # create a dictionary to track the stats for the away team when playing at home
        away_team_away_dictionary = {} #create a dictionary to track the stats for each away team
        for home_team, away_team in teams:

            # Collect the stats  of the home team
            self.previous_cursor.execute('SELECT home_xg,score,away_xg FROM fixtures WHERE home_team = ? AND gameweek < ?', (home_team,self.gameweek,))
            home_home_stats_list = self.previous_cursor.fetchall()

            self.previous_cursor.execute('SELECT home_xg,score,away_xg FROM fixtures WHERE away_team = ? AND gameweek < ?', (home_team,self.gameweek,))
            home_away_stats_list = self.previous_cursor.fetchall()

            #Collect the stats of the away team

            self.previous_cursor.execute('SELECT away_xg,score,home_xg FROM fixtures WHERE home_team = ? AND gameweek < ?', (away_team,self.gameweek,))
            away_home_stats_list = self.previous_cursor.fetchall()

            self.previous_cursor.execute('SELECT away_xg,score,home_xg FROM fixtures WHERE away_team = ? AND gameweek < ?', (away_team,self.gameweek,))
            away_away_stats_list = self.previous_cursor.fetchall()


            #include the
            #add the home and away teams to their respective sets
            if home_team not in home_team_home_dictionary:
                home_team_home_dictionary[home_team] = {'home_team_home_xg': 0, 'home_team_home_goals': 0, 'home_team_home_xg_conceded': 0, 'home_team_home_goals_conceded': 0}


            if home_team not in home_team_away_dictionary:
                home_team_away_dictionary[home_team] = {'home_team_away_xg': 0, 'home_team_away_goals': 0, 'home_team_away_xg_conceded': 0, 'home_team_away_goals_conceded': 0}

            if away_team not in away_team_away_dictionary:
                away_team_away_dictionary[away_team] = {'away_team_away_xg': 0, 'away_team_away_goals': 0, 'away_team_away_xg_conceded': 0, 'away_team_away_goals_conceded': 0}

            if away_team not in away_team_home_dictionary:
                away_team_home_dictionary[away_team] = {'away_team_home_xg':0,'away_team_home_goals':0,'away_team_home_xg_conceded':0,"away_team_home_goals_conceded":0}

            for home_home_row,home_away_row in zip(home_home_stats_list,home_away_stats_list):

                #sort out the stats when the home team is playing at home
                home_team_home_xg, home_score, home_team_home_conceded_xg = home_home_row
                home_team_home_goals, home_team_home_goals_conceded = sort_goals(home_score)

                #sort out the stats when the home team is playing away
                home_team_away_xg_conceded,away_score,home_team_away_xg = home_away_row
                home_team_away_goals_conceded, home_team_away_goals = sort_goals(away_score)

                #add this information to a dictionary, and we will insert this into the db later on

                try: #we need to include a try and accept statement because sometimes data is missing, and we need to omitt this data
                    home_team_home_dictionary[home_team]['home_team_home_xg'] += float(home_team_home_xg)
                    home_team_home_dictionary[home_team]['home_team_home_goals'] += int(home_team_home_goals)
                    home_team_home_dictionary[home_team]['home_team_home_xg_conceded'] += float(home_team_home_conceded_xg)
                    home_team_home_dictionary[home_team]['home_team_home_goals_conceded'] += int(home_team_home_goals_conceded)

                    #add the stats when the home team are playing away
                    home_team_away_dictionary[home_team]['home_team_away_xg'] += float(home_team_away_xg)
                    home_team_away_dictionary[home_team]['home_team_away_goals'] += float(home_team_away_goals)
                    home_team_away_dictionary[home_team]['home_team_away_xg_conceded'] += float(home_team_away_xg_conceded)
                    home_team_away_dictionary[home_team]['home_team_away_goals_conceded'] += float(home_team_away_goals_conceded)



                except sqlite3.Error as error:
                    print(f"An error ocurred : {error}")

            for away_home_row,away_away_row in zip(away_home_stats_list,away_away_stats_list): #getting the stats for the away team

                #sort out the stats for when the away teams were playing at home

                away_team_home_xg,away_home_score,away_team_home_xg_conceded = away_home_row
                away_team_home_goals,away_team_home_goals_conceded = sort_goals(away_home_score)

                #sort out the stats for when the away teams were playing away
                away_team_away_xg,away_away_score,away_team_away_xg_conceded  = away_away_row
                away_team_away_goals_conceded,away_teams_away_goals = sort_goals(away_away_score)

                try: #we need to include a try and accept statement because sometimes data is missing, and we need to omitt this data

                    #sort the stats for when the away team is playing at home

                    away_team_home_dictionary[away_team]['away_team_home_xg'] += float(away_team_home_xg)
                    away_team_home_dictionary[away_team]['away_team_home_goals'] += int(away_team_home_goals)
                    away_team_home_dictionary[away_team]['away_team_home_xg_conceded'] += float(away_team_home_xg_conceded)
                    away_team_home_dictionary[away_team]['away_team_home_goals_conceded'] += int(away_team_home_goals_conceded)




                    #sort the stats for when the away team is playing away
                    away_team_away_dictionary[away_team]['away_team_away_xg'] += float(away_team_away_xg)
                    away_team_away_dictionary[away_team]['away_team_away_goals'] += int(away_teams_away_goals)
                    away_team_away_dictionary[away_team]['away_team_away_xg_conceded'] += float(away_team_away_xg_conceded)
                    away_team_away_dictionary[away_team]['away_team_away_goals_conceded'] += int(away_team_away_goals_conceded)


                except sqlite3.Error as error:
                    print(f"An error ocurred : {error}")

            #now we have the data for each team, we can insert it into the database
            #inserting for the home team when at home:
            for home_team,stats in home_team_home_dictionary.items():
                try:
                    self.cursor.execute(
                        f"UPDATE {self.primary_table} SET home_team_home_goals = ?, home_team_home_goals_conceded = ?, home_team_home_xg = ?, home_team_home_conceded_xg = ? WHERE home_team = ?",
                        (stats['home_team_home_goals'], stats['home_team_home_goals_conceded'],
                         stats['home_team_home_xg'], stats['home_team_home_xg_conceded'], home_team))
                    self.connection.commit()
                except sqlite3.Error as error:
                    print(f'An error occured when updating home data when at home : {error}')

            #inserting the data for the away team when away
            for away_team, stats in away_team_away_dictionary.items():
                try:
                    self.cursor.execute(
                        f"UPDATE {self.primary_table} SET away_team_away_goals = ?, away_team_away_goals_conceded = ?, away_team_away_xg = ?, away_team_away_conceded_xg = ? WHERE away_team = ?",
                        (stats['away_team_away_goals'], stats['away_team_away_goals_conceded'],
                         stats['away_team_away_xg'], stats['away_team_away_xg_conceded'], away_team))
                    self.connection.commit()
                except sqlite3.Error as error:
                    print(f'An error occurred updating away team data when away: {error}')

            for home_team,stats in home_team_away_dictionary.items(): #inserting the data for the home team when away
                try:
                    self.cursor.execute(
                        f"UPDATE {self.primary_table} SET home_team_away_goals = ?, home_team_away_goals_conceded = ?, home_team_away_xg = ?, home_team_away_xg_conceded = ? WHERE home_team = ?",
                        (stats['home_team_away_goals'], stats['home_team_away_goals_conceded'],
                         stats['home_team_away_xg'], stats['home_team_away_xg_conceded'], home_team))
                    self.connection.commit()

                except sqlite3.Error as error:
                    print(f"An error occured updating home team data when away: {error}")

            for away_team,stats in away_team_home_dictionary.items(): #inserting the data for the away team when at home
                try:
                    self.cursor.execute(
                        f"UPDATE {self.primary_table} SET away_team_home_goals = ?, away_team_home_goals_conceded = ?, away_team_home_xg = ?, away_team_home_xg_conceded = ? WHERE away_team = ?",
                        (stats['away_team_home_goals'], stats['away_team_home_xg_conceded'],
                         stats['away_team_home_xg'], stats['away_team_home_xg_conceded'], away_team,))
                    self.connection.commit()

                except sqlite3.Error as error:
                    print(f"An error occured updating away team data when at home: {error}")




    def predictions(self): #prediction method 1
        self.cursor.execute(f'SELECT fixture,home_previous_xg,away_previous_xg,home_team_home_goals,away_team_away_goals,home_team_home_goals_conceded,away_team_away_goals_conceded,home_team_home_xg,away_team_away_xg,home_team_home_conceded_xg,away_team_away_conceded_xg FROM {self.primary_table}') #again,only considering the data we have before the game. included this for the purpose of backtesting
        data = self.cursor.fetchall()
        for fixture,home_previous_xg,away_previous_xg,home_team_home_goals,away_team_away_goals,home_team_goals_conceded,away_team_away_goals_conceded,home_team_home_xg,away_team_away_xg,home_team_home_conceded_xg,away_team_away_conceded_xg in data:
            #calculate the lambda value for the home team
            scoring_efficiency_home = home_team_home_goals / home_team_home_xg
            opposition_conceding_efficiency_away = away_team_away_goals_conceded / away_team_away_conceded_xg
            home_lambda_value = scoring_efficiency_home * home_previous_xg * opposition_conceding_efficiency_away

            #calculate the lambda value for the away team
            scoring_efficiency_away = away_team_away_goals /away_team_away_xg
            opposition_conceding_efficiency_home = home_team_goals_conceded / home_team_home_conceded_xg
            away_lambda_value = scoring_efficiency_away * away_previous_xg * opposition_conceding_efficiency_home


            #work out most probable scorelines
            home_probability_list = []
            away_probability_list = []
            for possible_output in range(15):
                home_probability_list.append(ppd(home_lambda_value,possible_output))
                away_probability_list.append(ppd(away_lambda_value,possible_output))

            home_probable_goals = home_probability_list.index(max(home_probability_list)) #finds the most probable outcome
            away_probable_goals = away_probability_list.index(max(away_probability_list))
            #print(f'Method 2{fixture} : {home_probable_goals} - {away_probable_goals}')

        self.cursor.execute(
            f'SELECT fixture,home_previous_xg,away_previous_xg,home_team_home_goals,away_team_away_goals,home_team_home_goals_conceded,away_team_away_goals_conceded,home_team_home_xg,away_team_away_xg,home_team_home_conceded_xg,away_team_away_conceded_xg FROM {self.primary_table}')  # again,only considering the data we have before the game. included this for the purpose of backtesting
        data = self.cursor.fetchall()
        for fixture, home_previous_xg, away_previous_xg, home_team_home_goals, away_team_away_goals, home_team_goals_conceded, away_team_away_goals_conceded, home_team_home_xg, away_team_away_xg, home_team_home_conceded_xg, away_team_away_conceded_xg in data:
            # calculate the lambda value for the home team
            scoring_efficiency_home = home_team_home_goals / home_team_home_xg
            opposition_conceding_efficiency_away = away_team_away_goals_conceded / away_team_away_conceded_xg
            home_lambda_value = scoring_efficiency_home * home_previous_xg * opposition_conceding_efficiency_away

            # calculate the lambda value for the away team
            scoring_efficiency_away = away_team_away_goals / away_team_away_xg
            opposition_conceding_efficiency_home = home_team_goals_conceded / home_team_home_conceded_xg
            away_lambda_value = scoring_efficiency_away * away_previous_xg * opposition_conceding_efficiency_home

            # work out most probable scorelines
            home_probability_list = []
            away_probability_list = []
            for possible_output in range(15):
                home_probability_list.append(ppd(home_lambda_value, possible_output))
                away_probability_list.append(ppd(away_lambda_value, possible_output))

            home_probable_goals = home_probability_list.index(
                max(home_probability_list))  # finds the most probable outcome
            away_probable_goals = away_probability_list.index(max(away_probability_list))
            #print(f'Method 2 : {fixture} : {home_probable_goals} - {away_probable_goals}')

        self.cursor.execute(
            f'SELECT fixture,home_previous_xg,away_previous_xg,home_team_home_goals,away_team_away_goals,home_team_home_goals_conceded,away_team_away_goals_conceded,home_team_home_xg,away_team_away_xg,home_team_home_conceded_xg,away_team_away_conceded_xg, '
            f'home_team_away_goals,home_team_away_xg,home_team_away_goals_conceded,home_team_away_xg_conceded,away_team_home_goals, '
            f'away_team_home_xg,away_team_home_goals_conceded,away_team_home_xg_conceded FROM {self.primary_table}'
        )
        data_2 = self.cursor.fetchall()

        for fixture, home_previous_xg, away_previous_xg, home_team_home_goals, away_team_away_goals, home_team_home_goals_conceded, away_team_away_goals_conceded, home_team_home_xg, away_team_away_xg, home_team_home_conceded_xg, away_team_away_conceded_xg, home_team_away_goals, home_team_away_xg, home_team_away_goals_conceded, home_team_away_xg_conceded, away_team_home_goals, away_team_home_xg, away_team_home_goals_conceded, away_team_home_xg_conceded in data_2:
            # calculate lambda for home team
            home_scoring_efficiency = (home_team_home_goals + home_team_away_goals) / (
                        home_team_home_xg + home_team_away_xg)
            away_conceding_efficiency = (away_team_home_goals_conceded + away_team_away_goals_conceded) / (
                        away_team_home_xg_conceded + away_team_away_conceded_xg)
            home_lambda_value = home_scoring_efficiency * home_previous_xg * away_conceding_efficiency

            # calculate lambda for away team
            away_scoring_efficiency = (away_team_away_goals + away_team_home_goals) / (
                        away_team_away_xg + away_team_home_xg)
            home_conceding_efficiency = (home_team_home_goals_conceded + home_team_away_goals_conceded) / (
                        home_team_home_conceded_xg + home_team_away_xg_conceded)
            away_lambda_value = away_scoring_efficiency * away_previous_xg * home_conceding_efficiency

            # work out most probable scorelines
            home_probability_list = []
            away_probability_list = []
            for possible_output in range(15):
                home_probability_list.append(ppd(home_lambda_value, possible_output))
                away_probability_list.append(ppd(away_lambda_value, possible_output))

            home_probable_goals = home_probability_list.index(
                max(home_probability_list))  # finds the most probable outcome
            away_probable_goals = away_probability_list.index(max(away_probability_list))
            print(f'Method 1 : {fixture} : {home_probable_goals} - {away_probable_goals}')




a = Database('final test',previous_db_file_path,38)
a.create_table()
a.get_fixtures()
a.insert_data_simple()
a.insert_data_complex()
a.predictions()
