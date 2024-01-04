import sqlite3
import tkinter as tk

root = tk.Tk()
root.title("Stats Table ")
root.geometry("500x900")



connection = sqlite3.connect('stats.db')
cursor = connection.cursor()
tuple_list = []  # Placeholder for tuple_list




## Sort the new list of tuples



#Determine how many buttons need to be made
for widget in root.winfo_children():
    widget.destroy()
    # Determine how many columns are ( as want to determine how many functions there are)
cursor.execute("PRAGMA table_info('teamStats')")
columns = cursor.fetchall()
# Create an empty list for the stats
stat_list = []
# Print column names
for column in columns:
    column_name = column[1]
    # We don't want the 'id' ,time,abbreviation,colourcode as they aren't stat. Also removing team as the table creator covers that
    if column_name != "id" and column_name != "date_and_time" and column_name != "team_name" and column_name != "abbreviation" and column_name!= "colour_code":
        stat_list.append(column_name)
    else:
        continue
def main_menu():
    # Clear the window
    for widget in root.winfo_children():
        widget.destroy()
    # Explain what's going on
    x_graph_label = tk.Label(root, text="Select a stat to create a table for:")
    x_graph_label.grid(row=0, column=0)
    # Set the column and row to 0 as the loop will place the buttons accordingly and increment
    column = 0
    row = 1
    for stat in stat_list:
        stat = tk.Button(root, text=str(stat), command=lambda s=stat: get_list(s))
        stat.grid(row=row, column=column)
        # We want 4 stats per column
        if column != 4:
            column += 1
        if column == 4:
            column = 0
            row += 1


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
    display_table(sorted_list,stat,True)



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



def display_table(sorted_list,stat,flip_order):
    for widget in root.winfo_children():
        widget.destroy()
    tk.Label(root,text='Teams by ' + stat).grid(row=0,column=0,pady=5)
    if flip_order == True:
        sorted_list.reverse()  # Reversing the sorted list to display in descending order
    row_number = 1
    for row in sorted_list:
        tk.Label(root, text=row[0]).grid(row=row_number, column=0)
        tk.Label(root, text=row[1]).grid(row=row_number, column=1)
        row_number += 1
    back_to_main_menu_button(8,4)
    flip_order_button(8,3,sorted_list,stat)


def back_to_main_menu_button(column, row):
    back_button = tk.Button(root, text="Main Menu", padx=5, pady=5, command=lambda: main_menu(), fg="white", bg="black")
    back_button.grid(row=row, column=column)


def flip_order_button(column,row,sorted_list,stat):

    flip_order_button = tk.Button(root,text='Toggle Order',padx=5,pady=5,command=lambda:display_table(sorted_list,stat,True))
    flip_order_button.grid(row=row,column=column)
main_menu()
root.mainloop()
