import matplotlib

import requests

from datetime import datetime

import matplotlib.image as mpimg

import matplotlib.pyplot as plt

import os

import json

import matplotlib.font_manager as fm

from tabulate import tabulate

import numpy as np

import json





url = "https://site.web.api.espn.com/apis/v2/scoreboard/header?sport=baseball&league=mlb&region=us&lang=en&contentorigin=espn&buyWindow=1m&showAirings=buy%2Clive%2Creplay&showZipLookup=true&tz=America%2FNew_York"



headers = {

    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3",

}



response = requests.get(url, headers=headers)



if response.status_code == 200:

    # Parse JSON response

    json_data = response.json()

   
    # Extract and filter Yankees games

    yankees_games = [game for league in json_data['sports'][0]['leagues'] for game in league['events'] if 'NYM' in game['shortName']]

    
 # Save JSON data for Yankees games to a file
    with open("Yankees_Games.json", "w") as file:
        json.dump(json_data, file, indent=4)
    
    print("JSON data for Yankees games saved to Yankees_Games.json")
          
    fig, ax = plt.subplots(figsize=(10, 6))  # 1920x1200 pixels



    # Create a table

    ax.axis('off')  # Hide axes



    # Column titles

    

    # Data rows

    data = []

    for game in yankees_games:

        away_team = game['odds']['awayTeamOdds']['team']['abbreviation']

        home_team = game['odds']['homeTeamOdds']['team']['abbreviation']

        away_score = next((comp['score'] for comp in game['competitors'] if comp['homeAway'] == "away"), "")

        home_score = next((comp['score'] for comp in game['competitors'] if comp['homeAway'] == "home"), "")

        #print(home_score)

        

        away_moneyline_data = game['odds']['moneyline']['away']

        away_moneyline = str(away_moneyline_data['current']['odds']) if 'current' in away_moneyline_data else str(game['odds']['awayTeamOdds']['moneyLine'])

        "100" if str(away_moneyline) == "EVEN" else away_moneyline

        #away_sign = '+' + str(away_moneyline) if int(away_moneyline) >= 0 else str(away_moneyline)
        if str(away_moneyline).upper() == "OFF":
            away_sign = "OFF"
        else:
            away_sign = '+' + str(away_moneyline) if int(away_moneyline) >= 0 else str(away_moneyline)

        home_moneyline_data = game['odds']['moneyline']['home']

        home_moneyline = str(home_moneyline_data['current']['odds']) if 'current' in home_moneyline_data else str(game['odds']['homeTeamOdds']['moneyLine'])

        "100" if str(home_moneyline) == "EVEN" else home_moneyline

        #home_sign = '+' + str(home_moneyline) if int(home_moneyline) >= 0 else str(home_moneyline)
        if str(home_moneyline).upper() == "OFF":
            home_sign = "OFF"
        else:
            home_sign = '+' + str(home_moneyline) if int(home_moneyline) >= 0 else str(home_moneyline)

        inning = game['fullStatus']['type']['shortDetail']

        #runs_scored = int(home_score + away_score)

        #print(runs_scored)

        total = game['odds']['total'].get('current', {}).get('line', f"o/{game['odds']['total']['under']['close']['line']}")

        away_cell_color = next((comp['color'] for comp in game['competitors'] if comp['homeAway'] == "away"), None)

        home_cell_color = next((comp['color'] for comp in game['competitors'] if comp['homeAway'] == "home"), None)

        away_text_color = next((comp['alternateColor'] for comp in game['competitors'] if comp['homeAway'] == "away"), None)

        home_text_color = next((comp['alternateColor'] for comp in game['competitors'] if comp['homeAway'] == "home"), None)

        

        

        data.append([away_team, away_score, inning, away_sign])

        data.append([home_team, home_score, total, home_moneyline])

        

    #col_titles = ["", '' if str(away_score) == "" else "Runs", '', "Odds"]

    # Determine if both home and away scores are blank

    if str(home_score) == "":

        col_titles = ["", "", "", "Odds"]  # Both scores are blank, so set both titles blank

    else:

        col_titles = ["", "Runs", "", "Odds"]

    

    table = ax.table(cellText=data, colLabels=col_titles, loc='left', cellLoc='center')

    # Create the figure and toggle full-screen mode

        

    bg_color = '#808080'

    

    



    # Adjust font size

    table.auto_set_font_size(False)

    table.set_fontsize(48)

    table.scale(.6, 2.75)

    

    table.auto_set_column_width(col=list(range(len(col_titles))))

    

    pitcher = []

    for game in yankees_games:

        away_starter = next((comp['summaryAthletes'][0]['athlete']['shortName'] for comp in game['competitors'] if comp['homeAway'] == "away"), None)

        home_starter = next((comp['summaryAthletes'][0]['athlete']['shortName'] for comp in game['competitors'] if comp['homeAway'] == "home"), None)

        

        pitcher.append([away_starter])

        pitcher.append([home_starter])

        

    pitcher_col_titles = ["Starting Pitchers"]

    pitcher_table = ax.table(cellText=pitcher, colLabels=pitcher_col_titles, bbox=[1, .4, .3, .2], cellLoc='center')

    print(pitcher)

    

    pitcher_table.auto_set_font_size(False)

    pitcher_table.set_fontsize(24)

    #pitcher_table.scale(.6, 2.25)

    

    pitcher_table.auto_set_column_width(10)

    #pitcher_table.auto_set_column_width(col=list(range(len(max(home_starter, away_starter))))

    

    

    if 'situation' in game:

        live = []

        for game_data in yankees_games:

            outs = game_data['outsText']

            bases = game_data['baseRunnersText']

            balls = game_data['situation']['balls']

            strikes = game_data['situation']['strikes']

            #print(outs, " Outs", bases)

            

            live.append([bases])

            live.append([outs])

            live.append([f"{balls}-{strikes}"])

            

        #pitcher_col_titles = ["Starters"]

        live_table = ax.table(cellText=live, bbox=[-.35, .1, .5, .2], cellLoc='center')

        #print(pitcher)

        

        live_table.auto_set_font_size(False)

        live_table.set_fontsize(24)

        #live_table.scale(.6, 2.75)

        for key, cell in live_table._cells.items():

            row, col = key

            if col == 0:

                cell.set_facecolor(bg_color)  # Light gray color

                cell.set_text_props(color= 'white')

        for cell in live_table.get_celld().values():

            cell.set_linewidth(0)

                #prop =   prop = fm.FontProperties(family='Times New Roman')

        for cell in live_table._cells.values():

            cell.set_text_props(weight='bold')  

        

        live_table.auto_set_column_width(col=list(range(len(bases))))

        

        bat = []

        for games_data in yankees_games:

            batter = games_data['situation']['batter']['athlete']['shortName']

            play = games_data['situation']['lastPlay']['shortText']

            

            bat.append([batter])

            bat.append([play])

        

        #pitcher_col_titles = ["Starters"]

        bat_table = ax.table(cellText=bat, bbox=[0.35, 0.1, .75, .2], cellLoc='center')

        #print(pitcher)

        

        bat_table.auto_set_font_size(False)

        bat_table.set_fontsize(24)

        #live_table.scale(.6, 2.75)

        for key, cell in bat_table._cells.items():

            row, col = key

            if col == 0:

                cell.set_facecolor(bg_color)  # Light gray color

                cell.set_text_props(color= 'white')

        for cell in bat_table.get_celld().values():

            cell.set_linewidth(0)

        

           

    else:

        None

    

    

    

    

  

        #prop =   prop = fm.FontProperties(family='Times New Roman')

    for cell in pitcher_table._cells.values():

        cell.set_text_props(weight='bold')

    

        #prop =   prop = fm.FontProperties(family='Times New Roman')

    for cell in table._cells.values():

        cell.set_text_props(weight='bold')

    

    

    # Set face color for header cells

    for i in range(len(headers)):

        header_cells = table.get_celld()[(0, i)]

        header_cells.set_facecolor('#777777')

        

    # Set face color for header cells

    for i in range(len(headers)):

        header_cells = pitcher_table.get_celld()[(0, i)]

        header_cells.set_facecolor('#777777')

    

    for cell in table.get_celld().values():

        cell.set_linewidth(0)

        

    for cell in pitcher_table.get_celld().values():

        cell.set_linewidth(0)

        

    # Color the cells in the first row and column

    for key, cell in table._cells.items():

        row, col = key

        if row == 0:

            cell.set_facecolor('#666666')  # Light gray color

        if col == 0 and row == 1:

            cell.set_facecolor(f"#{away_cell_color}")

            cell.set_text_props(color=f"#{away_text_color}")

        if col == 0 and row == 2:

            cell.set_facecolor(f"#{home_cell_color}")

            cell.set_text_props(color=f"#{home_text_color}")

        if col == 0 and row == 0:

            cell.set_facecolor(bg_color)



    # Add title

    plt.title("BASEMENT SCOREBOARD \nYANKEES HYPE", fontsize=72, pad=10, fontweight='bold', color='white', y=.75)



    # Adjust layout to fit the table properly

    plt.subplots_adjust(left=0.2, right=0.8, top=0.9, bottom=0.1)



    fig.patch.set_facecolor(bg_color)  # Set the background color here (e.g., light gray)





    # Save the figure as PNG

    plt.savefig('yankees_games.png', bbox_inches='tight')

     

    # Function to close the plot after a specified duration

    def close_plot(event):

        plt.close()



    # Se

    

    # Set the plot window to be non-topmost (behind any open window)

    #plt.get_current_fig_manager().window.wm_attributes('-topmost', 0)

    

    # Retrieve the window associated with the figure manager


    

    plt.show()



else:

    print("Failed to fetch data. Status code:", response.status_code)

