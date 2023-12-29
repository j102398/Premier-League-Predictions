import os
import sqlite3
import tkinter as tk

root = tk.Tk()
root.title("Stats Table ")
root.geometry("500x900")


global connection
global cursor
connection = sqlite3.connect('stats.db')
cursor = connection.cursor()
tuple_list = []  # Placeholder for tuple_list




## Sort the new list of tuples

def main_menu():
    for widget in root.winfo_children():
        widget.destroy()
    xg_button = tk.Button(root, text="xg", padx=5, pady=5, command=lambda: get_list("xg_value"))
    xg_button.grid(row=0, column=0)

    goals_scored_button = tk.Button(root, text="Goals Scored", padx=5, pady=5, command=lambda: get_list("goals_scored"))
    goals_scored_button.grid(row=1, column=0)

    goals_conceded_button = tk.Button(root, text="Goals Conceded", padx=5, pady=5, command=lambda: get_list("goals_conceded"))
    goals_conceded_button.grid(row=2, column=0)

    average_age_button = tk.Button(root, text="Average Age", padx=5, pady=5, command=lambda: get_list("average_age"))
    average_age_button.grid(row=3, column=0)

    yellow_cards_button = tk.Button(root, text="Yellow Cards", padx=5, pady=5, command=lambda: get_list("yellow_cards"))
    yellow_cards_button.grid(row=0, column=1)

    red_cards_button = tk.Button(root, text="Red Cards", padx=5, pady=5, command=lambda: get_list("red_cards"))
    red_cards_button.grid(row=1, column=1)

    pens_made_button = tk.Button(root, text="Penalties Made", padx=5, pady=5, command=lambda: get_list("pens_made"))
    pens_made_button.grid(row=2, column=1)

    progressive_carries_button = tk.Button(root, text="Progressive Carries", padx=5, pady=5, command=lambda: get_list("progressive_carries"))
    progressive_carries_button.grid(row=3, column=1)



def get_list(stat):
    for widget in root.winfo_children():
        widget.destroy()

    query = "SELECT team_name, " + stat + " FROM teamStats"
    cursor.execute(query)
    results = cursor.fetchall()
    tuple_list = []
    for row in results:
        tuple_list.append(row)

    sorted_list = merge_sort_tuples(tuple_list,1)
    display_table(sorted_list)



def merge_sort_tuples(tuple_list, index):
    if len(tuple_list) > 1:
        LeftSideArray = tuple_list[0:len(tuple_list) // 2]
        RightSideArray = tuple_list[len(tuple_list) // 2:len(tuple_list)]

        merge_sort_tuples(LeftSideArray, index)
        merge_sort_tuples(RightSideArray, index)

        i = 0
        j = 0
        k = 0
        while i < len(LeftSideArray) and j < len(RightSideArray):
            if LeftSideArray[i][index] < RightSideArray[j][index]:
                tuple_list[k] = LeftSideArray[i]
                i += 1
            else:
                tuple_list[k] = RightSideArray[j]
                j += 1
            k += 1

        while i < len(LeftSideArray):
            tuple_list[k] = LeftSideArray[i]
            i += 1
            k += 1

        while j < len(RightSideArray):
            tuple_list[k] = RightSideArray[j]
            j += 1
            k += 1

    return tuple_list



def display_table(sorted_list):
    sorted_list.reverse()  # Reversing the sorted list to display in descending order
    row_number = 0
    for row in sorted_list:
        tk.Label(root, text=row[0]).grid(row=row_number, column=0)
        tk.Label(root, text=row[1]).grid(row=row_number, column=1)
        row_number += 1



def back_to_main_menu_button(column, row):
    back_button = tk.Button(root, text="Main Menu", padx=5, pady=5, command=lambda: main_menu(), fg="white", bg="black")
    back_button.grid(row=row, column=column)


main_menu()
display_table(tuple_list)
root.mainloop()
