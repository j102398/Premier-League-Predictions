import sqlite3
import tkinter as tk
import seaborn as sns
import matplotlib.pyplot as plt



root = tk.Tk()
root.title("Stats Visualiser using Graphs")
root.geometry("500x900")

connection = sqlite3.connect('stats.db')
cursor = connection.cursor()

#Determine how many columns are ( as want to determine how many functions there are)
cursor.execute("PRAGMA table_info('teamStats')")
columns = cursor.fetchall()
#Create an empty list for the stats
stat_list = []
# Print column names
for column in columns:
    column_name = column[1]
    #We don't want the 'id' or date and time column as they aren't stats. Also removing team as the table creator covers that
    if column_name != "id" and column_name != "date_and_time" and column_name != "team_name":
        stat_list.append(column_name)
    else:
        continue



def x_axis():
    #Clear the window
    for widget in root.winfo_children():
        widget.destroy()
    #Explain what's going on
    x_graph_label = tk.Label(root,text="Select the stat on the x axis:")
    x_graph_label.grid(row=0,column=0)
    # Set the column and row to 0 as the loop will place the buttons accordingly and increment
    column = 0
    row = 1
    for stat in stat_list:
        stat = tk.Button(root,text=str(stat),command=lambda s = stat: y_axis(s))
        stat.grid(row=row,column=column)
        # We want 4 stats per column
        if column != 4:
            column += 1
        if column == 4:
            column = 0
            row += 1
# Your additional code can go here...

def y_axis(x_axis_stat):
    #Clear the window
    for widget in root.winfo_children():
        widget.destroy()
    #Remove the x-axis stat from the list as plotting two identical things results in a straight line
    updated_stat_list = stat_list
    updated_stat_list.remove(x_axis_stat)
    # Explain what's going on
    y_graph_label = tk.Label(root, text="Select the stat on the y axis:")
    y_graph_label.grid(row=0, column=0)
    # Set the column and row to 0 as the loop will place the buttons accordingly and increment
    column = 0
    row = 1
    for stat in stat_list:
        stat = tk.Button(root, text=str(stat), command=lambda s = stat: draw_graph(x_axis_stat,s))
        stat.grid(row=row, column=column)
        #We want 4 stats per column
        if column != 4:
            column += 1
        if column == 4:
            column = 0
            row += 1



def draw_graph(x_axis_stat,y_axis_stat):
    #Clear the window
    for widget in root.winfo_children():
        widget.destroy()

    #Extract the relevant data into 3 arrays
    x_stat_array = []
    y_stat_array = []
    team_abbreviation_list = []
    colour_code_list = []
    query = "SELECT " + x_axis_stat + "," + y_axis_stat + ", team_abbreviation , colour_code " + " FROM teamStats"
    cursor.execute(query)
    rows = cursor.fetchall()
    for row in rows:
        x_stat_array.append(row[0])
        y_stat_array.append(row[1])
        team_abbreviation_list.append(row[2])
        colour_code_list.append(row[3])
    title = y_axis_stat + " vs" + x_axis_stat
    plt.scatter(x_stat_array,y_stat_array,color=colour_code_list)
    plt.xlabel(x_axis_stat)
    plt.ylabel(y_axis_stat)
    plt.title(title)
    plt.grid(False)
    #Show the team name next to data point
    for i,abbreviation in enumerate(team_abbreviation_list):
        plt.text(x_stat_array[i], y_stat_array[i], abbreviation, fontsize=8, ha='right', va='bottom')
    plt.show()



x_axis()
root.mainloop()

