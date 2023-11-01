from PIL import ImageTk, Image
import tkinter as tk
import requests
from bs4 import BeautifulSoup

root = tk.Tk()
root.title("Premier League Stats")
root.geometry("500x900")

def back_to_main_menu_button(column, row):
    back_button = tk.Button(root, text="Main Menu", padx=5, pady=5, command=lambda: main_menu(), fg="white", bg="black")
    back_button.grid(row=row, column=column)

def main_menu():
    root.geometry("200x200")
    for widget in root.winfo_children():
        widget.destroy()
    stats_by_team = tk.Button(root, text="Statistics by team", padx=5, pady=5, command=lambda: display_eplteams())
    stats_by_team.grid(row=0, column=0)

    display_epl_table = tk.Button(root, text="Display EPL Table", padx=5, pady=5, command=lambda: display_epltable())
    display_epl_table.grid(row=1, column=0)

def display_eplteams():
    root.geometry("700x900")
    for widget in root.winfo_children():
        widget.destroy()
    label = tk.Label(root, text="Select a team:")
    label.grid(row=0, column=0)

    eplteams = ['Arsenal', 'Aston Villa', 'Bournemouth', 'Brentford', 'Brighton', 'Burnley', 'Chelsea',
                'Crystal Palace', 'Everton', 'Fulham', 'Liverpool', 'Luton', 'Manchester City', 
                'Manchester Utd', 'Newcastle Utd', 'Nottm Forest', 'Sheffield Utd', 'Tottenham', 
                'West Ham', 'Wolves']
    column = 0
    row = 1
    for team in eplteams:
        team_badge_location = "badges/" + str(team) + ".png"
        team_badge = ImageTk.PhotoImage(Image.open(team_badge_location))
        team_button = tk.Button(root, text=str(team), image=team_badge, compound="top", padx=5, pady=5,
                                command=lambda t=team: display_functions(t))
        team_button.image = team_badge
        team_button.grid(row=row, column=column)
        column += 1
        if column % 4 == 0:
            row += 1
            column = 0
    back_to_main_menu_button(3, 10)

def display_functions(t):
    for widget in root.winfo_children():
        widget.destroy()
    team_badge_location = "badges/" + str(t) + ".png"
    team_badge = ImageTk.PhotoImage(Image.open(team_badge_location))
    team_label = tk.Label(root, image=team_badge, compound="top", padx=5, pady=5)
    team_label.image = team_badge
    team_label.grid(row=0, column=0)

    most_goals_button = tk.Button(root, text="Top Scorer", padx=20, pady=20,
                                  command=lambda: display_top_scorer(t))
    most_goals_button.grid(row=1, column=0)
    goals_conceded_button = tk.Button(root, text="Goals Conceded", padx=20, pady=20,
                                      command=lambda: display_goals_conceded(t))
    goals_conceded_button.grid(row=2, column=0)

    team_total_goals_button = tk.Button(root, text="Team Total Goals", padx=20, pady=20,
                                        command=lambda: team_total_goals(t))
    team_total_goals_button.grid(row=3, column=0)

    cleansheets_button = tk.Button(root, text="Clean sheets", padx=20, pady=20,
                                   command=lambda: clean_sheets(t))
    cleansheets_button.grid(row=4, column=0)

    back_to_main_menu_button(3, 10)
    back_button = tk.Button(root, text="Back", padx=5, pady=5, command=lambda: display_eplteams(),
                            fg="white", bg="black")
    back_button.grid(row=10, column=0)

def display_top_scorer(t):
    for widget in root.winfo_children():
        widget.destroy()
    team_badge_location = "badges/" + str(t) + ".png"
    team_badge = ImageTk.PhotoImage(Image.open(team_badge_location))
    team_label = tk.Label(root, image=team_badge, compound="top", padx=5, pady=5)
    team_label.image = team_badge
    team_label.grid(row=0, column=0)

    pageToScrape = requests.get('https://fbref.com/en/comps/9/Premier-League-Stats')
    soup = BeautifulSoup(pageToScrape.text, "html.parser")

    top_scorers_elements = soup.find_all(attrs={"data-stat": "top_team_scorers"})
    team_elements = soup.find_all(attrs={"data-stat": "team"})

    if top_scorers_elements and team_elements:
        for top_scorer, team in zip(top_scorers_elements, team_elements):
            player_data = top_scorer.get_text(strip=True)
            team_name = team.get_text(strip=True)
            if team_name == t:
                goals = tk.Label(root, text=str(player_data) + " goals", padx=5, pady=5)
                goals.grid(row=1, column=0)
    else:
        print("Elements with 'data-stat' 'top_team_scorers' or 'team' were not found on the page.")

    back_to_main_menu_button(3, 10)
    back_button = tk.Button(root, text="Back", padx=5, pady=5, command=lambda: display_functions(t),
                            fg="white", bg="black")
    back_button.grid(row=10, column=0)

def display_goals_conceded(t):
    for widget in root.winfo_children():
        widget.destroy()
    team_badge_location = "badges/" + str(t) + ".png"
    team_badge = ImageTk.PhotoImage(Image.open(team_badge_location))
    team_label = tk.Label(root, image=team_badge, compound="top", padx=5, pady=5)
    team_label.image = team_badge
    team_label.grid(row=0, column=0)

    pageToScrape = requests.get('https://fbref.com/en/comps/9/Premier-League-Stats')
    soup = BeautifulSoup(pageToScrape.text, "html.parser")

    goals_conceded_elements = soup.find_all(attrs={"data-stat": "gk_goals_against"})
    team_elements = soup.find_all(attrs={"data-stat": "team"})

    if goals_conceded_elements and team_elements:
        for goals_conceded, team in zip(goals_conceded_elements, team_elements):
            player_data = goals_conceded.get_text(strip=True)
            team_name = team.get_text(strip=True)
            if team_name == t:
                goals = tk.Label(root, text=str(player_data) + " goals conceded", padx=5, pady=5)
                goals.grid(row=1, column=0)
    else:
        print("Not found")

    psxg_conceded_elements = soup.find_all(attrs={"data-stat": "gk_psxg"})
    if psxg_conceded_elements and team_elements:
        for psxg_conceded, team in zip(psxg_conceded_elements, team_elements):
            player_data = psxg_conceded.get_text(strip=True)
            team_name = team.get_text(strip=True)
            if team_name == t:
                outputted_pxsg_message = "From an expected " + player_data + " goals"
                goals = tk.Label(root, text=str(outputted_pxsg_message), padx=5, pady=5)
                goals.grid(row=2, column=0)
    else:
        print("Not found")

    back_to_main_menu_button(3, 10)
    back_button = tk.Button(root, text="Back", padx=5, pady=5, command=lambda: display_functions(t),
                            fg="white", bg="black")
    back_button.grid(row=10, column=0)

def team_total_goals(t):
    for widget in root.winfo_children():
        widget.destroy()

    team_badge_location = "badges/" + str(t) + ".png"
    team_badge = ImageTk.PhotoImage(Image.open(team_badge_location))
    team_label = tk.Label(root, image=team_badge, compound="top", padx=5, pady=5)
    team_label.image = team_badge
    team_label.grid(row=0, column=0)

    pageToScrape = requests.get('https://fbref.com/en/comps/9/Premier-League-Stats')
    soup = BeautifulSoup(pageToScrape.text, "html.parser")

    team_total_goals_elements = soup.find_all(attrs={"data-stat": "goals"})
    team_elements = soup.find_all(attrs={"data-stat": "team"})

    if team_total_goals_elements and team_elements:
        for team_total_goals, team in zip(team_total_goals_elements, team_elements):
            player_data = team_total_goals.get_text(strip=True)
            team_name = team.get_text(strip=True)
            if team_name == t:
                goals = tk.Label(root, text=str(player_data) + " goals", padx=5, pady=5)
                goals.grid(row=1, column=0)
    else:
        print("Not found")

    team_total_xg_elements = soup.find_all(attrs={"data-stat": "xg"})
    if team_total_xg_elements and team_elements:
        for team_total_xg, team in zip(team_total_xg_elements, team_elements):
            player_data = team_total_xg.get_text(strip=True)
            team_name = team.get_text(strip=True)
            if team_name == t:
                outputtedsentence = "From an expected " + str(player_data) + " goals"
                goals = tk.Label(root, text=outputtedsentence, padx=5, pady=5)
                goals.grid(row=2, column=0)

    back_to_main_menu_button(3, 10)
    back_button = tk.Button(root, text="Back", padx=5, pady=5, command=lambda: display_functions(t),
                            fg="white", bg="black")
    back_button.grid(row=10, column=0)

def clean_sheets(t):
    for widget in root.winfo_children():
        widget.destroy()

    team_badge_location = "badges/" + str(t) + ".png"
    team_badge = ImageTk.PhotoImage(Image.open(team_badge_location))
    team_label = tk.Label(root, image=team_badge, compound="top", padx=5, pady=5)
    team_label.image = team_badge
    team_label.grid(row=0, column=0)

    pageToScrape = requests.get('https://fbref.com/en/comps/9/Premier-League-Stats')
    soup = BeautifulSoup(pageToScrape.text, "html.parser")

    team_elements = soup.find_all(attrs={"data-stat": "team"})
    clean_sheets_total = soup.find_all(attrs={"data-stat": "gk_clean_sheets"})
    clean_sheets_percentage = soup.find_all(attrs={"data-stat": "gk_clean_sheets_pct"})

    if clean_sheets_total and team_elements:
        for clean_sheets, team in zip(clean_sheets_total, team_elements):
            player_data = clean_sheets.get_text(strip=True)
            team_name = team.get_text(strip=True)
            if team_name == t:
                outputtedsentence = str(player_data) + " total clean sheets"
                clean_sheetslabel = tk.Label(root, text=outputtedsentence, padx=0, pady=0)
                clean_sheetslabel.grid(row=1, column=0)

    if clean_sheets_percentage and team_elements:
        for clean_sheets_pctg, team in zip(clean_sheets_percentage, team_elements):
            player_data = clean_sheets_pctg.get_text(strip=True)
            team_name = team.get_text(strip=True)
            if team_name == t:
                outputtedsentence = "(" + str(player_data) + "% clean sheet percentage)"
                cleansheetpercentagelabel = tk.Label(root, text=outputtedsentence, padx=5, pady=5)
                cleansheetpercentagelabel.grid(row=2, column=0)

    back_to_main_menu_button(3, 5)
    back_button = tk.Button(root, text="Back", padx=5, pady=5, command=lambda: display_functions(t),
                            fg="white", bg="black")
    back_button.grid(row=10, column=0)

def display_epltable():
    root.geometry("700x800")
    for widget in root.winfo_children():
        widget.destroy()


    pageToScrape = requests.get('https://fbref.com/en/comps/9/Premier-League-Stats')
    soup = BeautifulSoup(pageToScrape.text, "html.parser")

    team_elements = soup.find_all(attrs={"data-stat": "team"})
    position_elements = soup.find_all(attrs={"data-stat": "rank"})
    points_elements = soup.find_all(attrs={"data-stat": "points"})
    matches_played_elements = soup.find_all(attrs={"data-stat": "games"})
    last_5_elements = soup.find_all(attrs={"data-stat": "last_5"})
    goal_difference_elements = soup.find_all(attrs={"data-stat": "goal_diff"})

    if team_elements and position_elements and points_elements and matches_played_elements and last_5_elements and goal_difference_elements:
        row = 0

        for position, team, points, matchesPlayed, last5, goalDifference in zip(position_elements, team_elements, points_elements,
                                                                                matches_played_elements, last_5_elements,
                                                                                goal_difference_elements):

            position = position.get_text(strip=True)
            team_name = team.get_text(strip=True)
            points = points.get_text(strip=True)
            matchesPlayed = matchesPlayed.get_text(strip=True)
            last5 = last5.get_text(strip=True)
            goalDifference = goalDifference.get_text(strip=True)

            outputtedsentenceposition = tk.Label(root, text=(str(position) + ". "))
            outputtedsentenceposition.grid(row=row, column=0, pady=1)

            outputtedsentenceteam = tk.Label(root, text=(str(team_name)))
            outputtedsentenceteam.grid(row=row, column=2, pady=1)

            outputtedsentencematchesplayed = tk.Label(root, text=str(matchesPlayed))
            outputtedsentencematchesplayed.grid(row=row, column=4, pady=1)

            outputtedsentencegoaldifference = tk.Label(root, text=str(goalDifference))
            outputtedsentencegoaldifference.grid(row=row, column=5, pady=1)

            outputtedsentencepoints = tk.Label(root, text=(str(points)), font=('Helvetica', 9, 'bold'))
            outputtedsentencepoints.grid(row=row, column=6, pady=1)

            outputtedsentencelast5 = tk.Label(root, text=str(last5))
            outputtedsentencelast5.grid(row=row, column=7, pady=1)

            row += 1
            if row == 21:
                back_to_main_menu_button(7, 21)
                break

main_menu()
root.mainloop()
