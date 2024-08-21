from datetime import datetime as datetime_module
import requests
from bs4 import BeautifulSoup
import sqlite3
import os
import shutil

pageToScrape = requests.get('https://fbref.com/en/comps/9/Premier-League-Stats')
soup = BeautifulSoup(pageToScrape.text, "html.parser")

# List of tuples with data-stat and SQL data type, and py stats
identifiers_and_types_standard = [
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
    ("last_5", "INTEGER", int),
    ("goal_diff", "REAL", float),
    ("xg_against","REAL", float),
    ("goals_against","REAL", float)
]




class Database:
    def __init__(self,database_name,primary_table,column_names_and_types): #initialise the database
        self.database_name = database_name
        self.primary_table = primary_table
        self.columns = column_names_and_types

    def create_database(self):
        self.connection = sqlite3.connect(f"{self.database_name}.db")
        self.cursor = self.connection.cursor()
        self.cursor.execute(f"CREATE TABLE IF NOT EXISTS {self.primary_table} (team TEXT PRIMARY KEY,last_5_points INTEGER)") #we made the primary key the team_name as that is what is unique
        #the last 5 points isn't a stat from the website, and we will deal with that later

    def create_columns(self):
        for column,column_type,py_type in self.columns: #ignore the py_type variable as it is irrelvant right now as we are dealing with sql
            try:
                if column == "team": #as we have already created a column called team
                    pass
                else:
                    self.cursor.execute(f"ALTER TABLE {self.primary_table} ADD COLUMN {column} {column_type}")
            except:
                pass

    def insert_teams(self): #insert the teams, which will be the primary key
        team_elements = soup.find_all(attrs={"data-stat": "team"})
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
        #loop through the stats, excluding the team name
        for stat_name,sql_type,py_type in identifiers_and_types_standard: #we are going to ignore the sql type of the stat as that is irrelevant here
            team_elements = soup.find_all(attrs={'data-stat':'team'})
            stat_elements = soup.find_all(attrs={'data-stat':stat_name})
            #loop through the elements,inserting the stat where the team matches the team in the database
            for team,stat_value in zip(team_elements,stat_elements):
                team = team.get_text(strip=True)  # convert the team html element to a string
                stat_value = (stat_value.get_text(strip=True))  # converting the html element to the necessary python type


                if (team.lower() == "squad" or "vs" in team.lower()):  # exclude team names such as "vs Manchester City, and excluding header names
                    pass
                else:
                    try:
                        self.cursor.execute(f'UPDATE {self.primary_table} SET {stat_name} = ? WHERE team = ?',(stat_value, team,))
                        self.connection.commit()
                    except:
                        pass




stats_db = Database('test','test_table',identifiers_and_types_standard)
stats_db.create_database()
stats_db.create_columns()
stats_db.insert_teams()
stats_db.insert_stats()
