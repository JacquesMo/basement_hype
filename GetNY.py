import matplotlib

matplotlib.use('Qt5Agg')

from PyQt5.QtWidgets import QMainWindow

from PyQt5.QtCore import Qt

import requests

from datetime import datetime

import matplotlib.image as mpimg

import matplotlib.pyplot as plt

import os

import json

import matplotlib.font_manager as fm

from tabulate import tabulate

import numpy as np







# API URL

url = "https://tank01-mlb-live-in-game-real-time-statistics.p.rapidapi.com/getMLBScoresOnly"



# Current date in the format "YYYYMMDD"

current_date = datetime.now().strftime("%Y%m%d")



# Query parameters

#querystring = {"gameDate": 20240508, "topPerformers": "false"}

querystring = {"gameDate": current_date, "topPerformers": "false"}



# Request headers

headers = {

    "X-RapidAPI-Key": "f5f34764b7msha305d7eccdad995p1a1d42jsn8183b627147e",

    "X-RapidAPI-Host": "tank01-mlb-live-in-game-real-time-statistics.p.rapidapi.com"

}



# Send GET request

response = requests.get(url, headers=headers, params=querystring)







# Check if the request was successful

if response.status_code == 200:

    # Parse JSON response

    json_data = response.json()



    #print(json_data)



    # Extract games involving New York Yankees (NYY)

    yankees_games = [game_info for game_info in json_data.get("body", {}).values() if game_info["home"] == "NYY" or game_info["away"] == "NYY"]



    print(yankees_games)



    # Prepare data for the table

    table_data = []

    for game_info in yankees_games:

        home_score = game_info["lineScore"]["home"]["R"]

        away_score = game_info["lineScore"]["away"]["R"]

        home_hits = game_info["lineScore"]["home"]["H"]

        away_hits = game_info["lineScore"]["away"]["H"]

        home_errors = game_info["lineScore"]["home"]["E"]

        away_errors = game_info["lineScore"]["away"]["E"]



        table_data.append([game_info['away'], away_score, away_hits, away_errors])

        table_data.append([game_info['home'], home_score, home_hits, home_errors])



    # Add headers

    headers = [" ", "R", "H", "E"]



    # Prepare data for the second table (scores by inning)

    inning_table_data = []

    inning_headers = [" ", "1", "2", "3", "4", "5", "6", "7", "8", "9"]



    # Prepare data for the second table (scores by inning)

    for game_info in yankees_games:

        home_innings = [game_info["lineScore"]["home"]["scoresByInning"].get(str(i), "") for i in range(1, 10)]

        away_innings = [game_info["lineScore"]["away"]["scoresByInning"].get(str(i), "") for i in range(1, 10)]



        home_team_row = [game_info['home']] + home_innings

        away_team_row = [game_info['away']] + away_innings



        inning_table_data.append(away_team_row)

        inning_table_data.append(home_team_row)



    live_table_data = []

    # Prepare data for the second table (scores by inning)

    for game_info in yankees_games:
        currentInning = game_info["currentInning"]

        if currentInning == "Final":
            continue

        currentCount = game_info["currentCount"]
        currentOuts = str(game_info["currentOuts"])

        # Ensure currentOuts is a string

        currentOuts_labeled = f"{currentOuts} Outs"

        live_table_data.append(currentInning)

        #live_table_data.append(currentCount)

        # NOTE: nothing here will execute since at this point everything is NOT final
        if currentInning != "Final":
            continue

        live_table_data.append([currentOuts_labeled])

        #live_table_data.append("Outs")



        #live_table_data.append([currentInning, currentCount, currentOuts_labeled])

    # Print table

    #print(tabulate(table_data, headers=headers))



    # Plotting section (table as PNG image)

    fig, ax = plt.subplots(figsize=(10, 6))



    #img = mpimg.imread('/home/jacq/Sports/yankees_logo_in_stripes_background_baseball_hd_yankees-1280x720-712316160.jpg')

    #ax.imshow(img, extent=[0, 1, 0, 1,], aspect='auto')



    # Create the figure and toggle full-screen mode

    mng = plt.get_current_fig_manager()

    mng.full_screen_toggle()







    ax.axis('tight')



    ax.axis('off')



    print("Table data:", table_data)



    team_table = ax.table(cellText=table_data, colLabels=headers, loc='center', cellLoc='center')

    team_table.auto_set_font_size(False)

    #team_table.set_fontweight('bold')

    team_table.set_fontsize(48)

    team_table.scale(.6, 2.75)





    #prop =   prop = fm.FontProperties(family='Times New Roman')

    for cell in team_table._cells.values():

        cell.set_text_props(weight='bold')





    # Set face color for header cells

    for i in range(len(headers)):

        header_cells = team_table.get_celld()[(0, i)]

        header_cells.set_facecolor('#777777')



    for cell in team_table.get_celld().values():

        cell.set_linewidth(0)





        # Second table (scores by inning)

    inning_table = ax.table(cellText=inning_table_data, colLabels=inning_headers, loc='lower center', cellLoc='center')

    inning_table.auto_set_font_size(False)

    inning_table.set_fontsize(32)

    inning_table.scale(1, 2)



    # Set face color for header cells in the second table

    for i in range(len(inning_headers)):

        header_cells = inning_table.get_celld()[(0, i)]

        header_cells.set_facecolor('#777777')



    # Remove borders from all cells in the second table

    for cell in inning_table.get_celld().values():

        cell.set_linewidth(0)



    # Set font properties to bold for all cells

    for cell in inning_table._cells.values():

        cell.set_text_props(weight='bold')



    # Color the cells in the first row

    for key, cell in inning_table._cells.items():

        row, col = key

        if col == 0:

            cell.set_facecolor('#777777')  # Light gray color



# Color the cells in the first row

    for key, cell in team_table._cells.items():

        row, col = key

        if col == 0:

            cell.set_facecolor('#777777')  # Light gray color



       # Third table (inning)

    live_table = ax.table(cellText=live_table_data, bbox=[.85, .4, .15, .2], cellLoc='center')

    live_table.auto_set_font_size(False)

    live_table.set_fontsize(36)

    #live_table.set_type('Times New Roman')

    live_table.scale(1, 1)



    # Remove borders from all cells in the second table

    for cell in live_table.get_celld().values():

        cell.set_linewidth(0)

        cell.set_facecolor('#154c79')



    # Set font properties to bold for all cells

    for cell in live_table._cells.values():

        cell.set_text_props(weight='bold')

        cell.set_text_props(color='white')



    fig.patch.set_facecolor('#154c79')



    print(live_table)



    plt.title("BASEMENT SCOREBOARD \nYANKEES HYPE", fontsize=86, pad=10, fontweight='bold', color='white', y=.75)



    plt.savefig('C:/Users/jgeni/NBA/basement_hype/yankees.png', bbox_inches='tight', pad_inches=0.1)



    # Function to close the plot after a specified duration

    def close_plot(event):

        plt.close()



    # Set a timer to close the plot after 10 min

    timer = fig.canvas.new_timer(interval= 12000)  # 10 min

    timer.add_callback(close_plot, None)

    timer.start()



    # Set the plot window to be non-topmost (behind any open window)

    #plt.get_current_fig_manager().window.wm_attributes('-topmost', 0)



    # Retrieve the window associated with the figure manager

    window = mng.window



    # Set window attributes to make it non-topmost

    window.setWindowFlags(window.windowFlags() & ~Qt.WindowStaysOnTopHint)



    plt.show()

    #try on crontab with timing



else:

    print("Failed to fetch data. Status code:", response.status_code)

