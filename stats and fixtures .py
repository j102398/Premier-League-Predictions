from datetime import datetime as datetime_module
import requests
from bs4 import BeautifulSoup
import sqlite3
import os
import shutil

url_stats = requests.get('https://fbref.com/en/comps/9/Premier-League-Stats')
soup_stats = BeautifulSoup(url_stats.text, "html.parser")
url_fixture = requests.get('https://fbref.com/en/comps/9/schedule/Premier-League-Scores-and-Fixtures')
soup_fixture = BeautifulSoup(url_fixture.text,"html.parser")


# List of tuples with data-stat and SQL data type, and py stats
stats_identifiers = [ #first element will be the primary key
    ("team","TEXT", str),
    ("players_used", "TEXT", str),
    ("avg_age", "REAL", float),
    ("possession", "REAL", float),
    ("games", "INTEGER", int),
    ("games_starts", "INTEGER", int),
    ("minutes", "INTEGER", int),
    ("minutes_90s", "REAL", float),
    ("goals_for", "INTEGER", int),
    ("assists", "INTEGER", int),
    ("goals_assists", "INTEGER", int),
    ("goals_pens", "INTEGER", int),
    ("pens_made", "INTEGER", int),
    ("cards_yellow", "INTEGER", int),
    ("cards_red", "INTEGER", int),
    ("xg", "REAL", float),
    ("npxg", "REAL", float),
    ("xg_assist", "REAL", float),
    ("progressive_carries", "TEXT", str),
    ("progressive_passes", "TEXT", str),
    ("progressive_passes_received", "TEXT", str),
    ("goals_per90", "REAL", float),
    ("assists_per90", "REAL", float),
    ("goals_assists_per90", "REAL", float),
    ("goals_pens_per90", "REAL", float),
    ("points", "REAL", float),
    ("wins", "INTEGER", int),
    ("ties", "INTEGER", int),
    ("losses", "TEXT", str),
    ("last_5", "TEXT", str),
    ("goal_diff", "REAL", float),
    ("xg_against","REAL", float),
    ("goals_against","REAL", float)
]

fixture_identifiers = [ #first element will be the primary key
    ("fixture","TEXT",str), #this is the primary key of the fixture database
    ("gameweek", "INTEGER",int),
    ("date", "TEXT",str),
    ("home_team", "TEXT",str),
    ("away_team", "TEXT",str),
    ("home_xg", "REAL",float),
    ("score", "TEXT",str),
    ("away_xg", "TEXT",str),
    ("referee", "TEXT",str)
]


class Database:
    def __init__(self,database_name,primary_table,primary_column_names_and_types,secondary_table,secondary_column_names_and_types): #initialise the database
        self.database_name = database_name
        self.primary_table = primary_table
        self.primary_columns = primary_column_names_and_types
        self.secondary_table = secondary_table
        self.secondary_columns = secondary_column_names_and_types

    def create_database(self):

        #we need to try and delete the current database, if it exists. this is because we are updating every stat from scratch
        try:
            os.remove(f"{self.database_name}.db")
        except Exception as error:
            print(f"An error occured when deleting {error}")
        self.connection = sqlite3.connect(f"{self.database_name}.db")
        self.cursor = self.connection.cursor()

        #create the stats table
        self.cursor.execute(f"CREATE TABLE IF NOT EXISTS {self.primary_table} (team TEXT PRIMARY KEY, last_5_points INTEGER)") #we made the primary key the team_name as that is what is unique
        # the last 5 points isn't a stat from the website, and we will deal with that later



        self.cursor.execute(f"CREATE TABLE IF NOT EXISTS {self.secondary_table} (fixture TEXT PRIMARY KEY )") #we made the primary key the team_name as that is what is unique

        #add the rest of the columns
        self.create_columns('primary') #create the rest of the columns for the primary table
        self.create_columns('secondary')  #create the rest of the columns for the secondary table
        #commit the changes
        self.connection.commit()



    def create_columns(self,table):
        if table == "primary":
            for column,column_type,py_type in self.primary_columns: #ignore the py_type variable as it is irrelvant right now as we are dealing with sql
                try:
                    if column == "team": #as we have already created a column called team
                        pass
                    else:
                        self.cursor.execute(f"ALTER TABLE {self.primary_table} ADD COLUMN {column} {column_type}")
                except:
                    pass
        elif table == "secondary":
            for column, column_type, py_type in self.secondary_columns:  # ignore the py_type variable as it is irrelvant right now as we are dealing with sql
                try:
                    if column == "team":  # as we have already created a column called team
                        pass
                    else:
                        self.cursor.execute(f"ALTER TABLE {self.secondary_table} ADD COLUMN {column} {column_type}")
                except:
                    pass

    def insert_teams(self): #insert the teams, which will be the primary key
        team_elements = soup_stats.find_all(attrs={"data-stat": "team"})
        for element in team_elements:
            #convert the element to a text
            team = element.get_text(strip=True)
            #don't insert if the team name is "Squad", as this is just hte name of the column!
            if team.lower() == "squad" or "vs"  in team.lower(): #exclude team names such as "vs Manchester City"

                pass
            else:
                try:
                    self.cursor.execute(f'INSERT INTO {self.primary_table} (team) VALUES (?)', (team,))
                    self.connection.commit()
                except:
                    pass



    def insert_stats(self):
        #insert the teams first
        self.insert_teams()
        #loop through the stats, excluding the team name
        for stat_name,sql_type,py_type in self.primary_columns: #we are going to ignore the sql type of the stat as that is irrelevant here
            team_elements = soup_stats.find_all(attrs={'data-stat':'team'})
            stat_elements = soup_stats.find_all(attrs={'data-stat':stat_name})
            #loop through the elements,inserting the stat where the team matches the team in the database
            for team,stat_value in zip(team_elements,stat_elements):
                team = team.get_text(strip=True)  # convert the team html element to a string
                stat_value = (stat_value.get_text(strip=True))  # converting the html element to the necessary python type


                if (team.lower() == "squad" or "vs" in team.lower()):  # exclude team names such as "vs Manchester City, and excluding header names
                    pass
                else:
                    try:

                        if stat_name.lower() == "last_5":#handle the last 5 differently, as we need to convert it from a string of characters to an integer value
                            points_counter = 0
                            for char in stat_value:
                                if char == "W":
                                    points_counter += 3
                                if char == "D":
                                    points_counter += 1

                            self.cursor.execute(f'UPDATE {self.primary_table} SET last_5 = ? , last_5_points = ? WHERE team = ?',(stat_value,points_counter, team,))
                            self.connection.commit()
                        else:
                            self.cursor.execute(f'UPDATE {self.primary_table} SET {stat_name} = ? WHERE team = ?',(stat_value, team,))
                            self.connection.commit()
                    except Exception as error:
                            print(f"An error occurred: {error}")



    def insert_fixtures(self):

        home_team_elements = soup_fixture.find_all(attrs={"data-stat": "home_team"})
        away_team_elements = soup_fixture.find_all(attrs={"data-stat": "away_team"})
        date_elements = soup_fixture.find_all(attrs={"data-stat": "date"})

        fixtures_inserted = 0 #will be 380 fixtures to be inserted
        for home, away, date in zip(home_team_elements, away_team_elements, date_elements):
            home_text = home.get_text(strip=True)
            away_text = away.get_text(strip=True)
            date_text = date.get_text(strip=True)

            if home_text and away_text and home_text != "Away" and away_text != "Away":
                fixture = home_text + " vs " + away_text


                # Insert data directly without try-except block
                self.cursor.execute('''INSERT INTO fixtures
                       (fixture, home_team, away_team, date)
                       VALUES (?,?,?,?)
                    ''', (fixture, home_text, away_text, date_text))
                self.connection.commit()

                fixtures_inserted += 1  # Increment games inserted counter

                if fixtures_inserted == 380:
                    print("Reached the limit of 380 games. Stopping further insertions.")
                    break

    def insert_results(self):
        self.insert_fixtures() #make sure all the fixtures have been inserted

        #we are going to loop through the provided identifiers, and insert them one by one
        for identifier,identifier_sql_type,identifier_py_type in self.secondary_columns:
            identifier_elements = soup_fixture.find_all(attrs={"data-stat": identifier})
            home_elements = soup_fixture.find_all(attrs={"data-stat": "home_team"})
            away_elements = soup_fixture.find_all(attrs={"data-stat": "away_team"})

            #loop through the elements, and insert where the home and away
            for identifier_value,home,away in zip(identifier_elements,home_elements,away_elements):
                #format the values



                identifier_value = (identifier_value.get_text(strip=True))
                home_value = home.get_text(strip=True)
                away_value = away.get_text(strip=True)
                fixture =  f"{home_value} vs {away_value}"

                try: #try and except clause necessary as can't convert an empty space to an integer
                    identifier_value = identifier_py_type(identifier_value)
                    self.cursor.execute(f'UPDATE {self.secondary_table} SET {identifier} = ? WHERE FIXTURE = ?',(identifier_value,fixture))
                    self.connection.commit()
                except Exception as error:
                    print(f"An error occured: {error}")



db = Database('test','stats',stats_identifiers,'fixtures',fixture_identifiers)
db.create_database()
db.insert_stats()
db.insert_results()

