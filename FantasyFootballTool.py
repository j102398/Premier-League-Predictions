import tkinter as tk
from bs4 import BeautifulSoup
import requests

root = tk.Tk()
root.title("Premier League Stats")
root.geometry("500x500")


def back_to_main_menu_button():
  back_button = tk.Button(root,text = "Back to main menu", padx=10,pady=10,command = lambda:main_menu(),fg = "white",bg = "black")
  back_button.grid(row = 10, column = 1,)


























def main_menu():
  for widget in root.winfo_children():
    widget.destroy()
  stats_by_team = tk.Button(root,text = "Statistics by team",padx=5,pady=5,command =lambda: display_eplteams())
  stats_by_team.grid(row=0,column=0)

  display_epl_table = tk.Button(root,text = "Display EPL Table",padx=5,pady=5,command=lambda : display_epltable())
  display_epl_table.grid(row=1,column=0)



def display_eplteams():
  for widget in root.winfo_children():
      widget.destroy()
  label = tk.Label(root, text="Select a team:")
  label.grid(row=0, column=0)

  eplteams = ['Arsenal', 'Aston Villa', 'Bournemouth', 'Brentford', 'Brighton', 'Burnley', 'Chelsea', 'Crystal Palace', 'Everton', 'Fulham', 'Liverpool', 'Luton', 'Manchester City', 'Manchester Utd', 'Newcastle Utd', 'Nott\'ham Forest', 'Sheffield Utd', 'Tottenham', 'West Ham', 'Wolves']
  column = 0
  row = 1
  for team in eplteams:
      team_button = tk.Button(root, text=str(team), padx=5, pady=5, command=lambda t=team: display_functions(t))
      team_button.grid(row=row, column=column)
      column += 1
      if column % 4 == 0:
          row += 1
          column = 0
  back_to_main_menu_button()

def display_functions(t):
    for widget in root.winfo_children():
      widget.destroy()
    label = tk.Label(root, text="Select the function:")
    label.grid(row=0, column=0)

    most_goals_button = tk.Button(root, text="Top Scorer", padx=20, pady=20, command=lambda: display_top_scorer(t))
    most_goals_button.grid(row=1, column=0)
    goals_conceded_button = tk.Button(root, text="Goals Conceded", padx=20, pady=20, command=lambda: display_goals_conceded(t))
    goals_conceded_button.grid(row=2, column=0)

    team_total_goals_button = tk.Button(root,text = "Team Total Goals",padx = 20, pady=20,
  command = lambda:team_total_goals(t))
    team_total_goals_button.grid(row=3,column=0)

    cleansheets_button = tk.Button(root,text = "Clean sheets",padx=20,pady=20,command = lambda: clean_sheets(t))
    cleansheets_button.grid(row=4,column=0)

    back_to_main_menu_button()
    back_button = tk.Button(root,text = "Back",padx = 5,pady=5,command = lambda: display_eplteams(),fg = "white",bg = "black")
    back_button.grid(row=10,column=0)


def display_top_scorer(t):
    for widget in root.winfo_children():
      widget.destroy()
    pageToScrape = requests.get('https://fbref.com/en/comps/9/Premier-League-Stats')
    soup = BeautifulSoup(pageToScrape.text, "html.parser")

    top_scorers_elements = soup.find_all(attrs={"data-stat": "top_team_scorers"})
    team_elements = soup.find_all(attrs={"data-stat": "team"})

    if top_scorers_elements and team_elements:
        for top_scorer, team in zip(top_scorers_elements, team_elements):
            player_data = top_scorer.get_text(strip=True)
            team_name = team.get_text(strip=True)
            if team_name == t:
                goals = tk.Label(root,text = str(player_data) + " goals" , padx=5, pady=5)
                goals.grid(row=0,column=0)
    else:
        print("Elements with 'data-stat' 'top_team_scorers' or 'team' were not found on the page.")

    back_to_main_menu_button()
    back_button = tk.Button(root,text = "Back",padx = 5,pady=5,command = lambda: display_functions(t),fg = "white",bg = "black")
    back_button.grid(row=10,column=0)


def display_goals_conceded(t):
  for widget in root.winfo_children():
    widget.destroy()
  pageToScrape = requests.get('https://fbref.com/en/comps/9/Premier-League-Stats')
  soup = BeautifulSoup(pageToScrape.text, "html.parser")

  goals_conceded_elements = soup.find_all(attrs={"data-stat": "gk_goals_against"})
  team_elements = soup.find_all(attrs={"data-stat": "team"})

  if goals_conceded_elements and team_elements:
     for goals_conceded, team in zip(goals_conceded_elements, team_elements):
       player_data = goals_conceded.get_text(strip=True)
       team_name = team.get_text(strip=True)
       if team_name == t:
         goals = tk.Label(root,text = str(player_data) + " goals conceded" , padx=5, pady=5)
         goals.grid(row=0,column=0)
  else:
    print("Not found")
  psxg_conceded_elements = soup.find_all(attrs={"data-stat": "gk_psxg"})
  if psxg_conceded_elements and team_elements:
    for psxg_conceded,team in zip(psxg_conceded_elements,team_elements):
      player_data = psxg_conceded.get_text(strip=True)
      team_name = team.get_text(strip=True)
      if team_name == t:
        outputted_pxsg_message = "From an expected " + player_data +" goals"
        goals = tk.Label(root,text = str(outputted_pxsg_message) , padx=5, pady=5)
        goals.grid(row=1,column=0)
  else:
    print("Not found")

  back_to_main_menu_button()
  back_button = tk.Button(root,text = "Back",padx = 5,pady=5,command = lambda: display_functions(t),fg = "white",bg = "black")
  back_button.grid(row=10,column=0)




