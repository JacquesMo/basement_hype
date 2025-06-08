import requests
import time
import matplotlib.pyplot as plt
import sys
import json
import os

# --- Configuration ---
# You can set this to 'PHI', 'NYY', or any other MLB team abbreviation.
TEAM_ABBREVIATION = 'LAD'
UPDATE_INTERVAL_SECONDS = 60

# --- Define the filename for the saved JSON file ---
SAVE_PATH_JSON = "scoreboard_data.json"

# --- ESPN API Endpoint (Updated to a more stable endpoint) ---
API_URL = "http://site.api.espn.com/apis/site/v2/sports/baseball/mlb/scoreboard"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3",
}

def on_close(event):
    """When the plot window is closed, this function is called to exit the script."""
    print("Plot window closed. Exiting program.")
    sys.exit(0)

def fetch_and_find_game():
    """
    Fetches data from the API, saves the raw JSON to a file, 
    and finds the game for the configured team.
    """
    try:
        response = requests.get(API_URL, headers=HEADERS, timeout=10)
        # This will raise an HTTPError for bad responses (4xx or 5xx)
        response.raise_for_status()
        json_data = response.json()
        
        # Save the JSON to the same directory as the script
        with open(SAVE_PATH_JSON, "w") as f:
            json.dump(json_data, f, indent=4)
        print(f"Successfully saved latest data to {SAVE_PATH_JSON}")

        # Search through the data for the specified team's game
        for event in json_data.get('events', []):
            # This is a robust way to find the game by checking team abbreviations directly.
            if any(TEAM_ABBREVIATION == comp.get('team', {}).get('abbreviation') for comp in event.get('competitions', [{}])[0].get('competitors', [])):
                # The game details are inside the first competition
                return event.get('competitions', [{}])[0]
                        
    except requests.exceptions.HTTPError as e:
        print(f"HTTP Error: Could not fetch data. Status code: {e.response.status_code}")
    except requests.exceptions.RequestException as e:
        # This catches other network-related errors (e.g., timeout, no internet)
        print(f"A network error occurred: {e}")
    except Exception as e:
        # This catches other potential errors (e.g., JSON decoding, file permissions)
        print(f"An unexpected error occurred in fetch_and_find_game: {e}")
        
    return None

def setup_plot():
    """Sets up the initial matplotlib figure, axes, and tables."""
    fig, ax = plt.subplots(figsize=(16, 9))
    fig.patch.set_facecolor('#333333')
    
    # Connect the 'on_close' function to the figure to handle closing the window
    fig.canvas.mpl_connect('close_event', on_close)
    
    ax.axis('off')

    # --- Create the new Linescore Table ---
    linescore_table = ax.table(
        cellText=[[''] * 13] * 2, # 2 rows, 13 columns
        colLabels=['', '1', '2', '3', '4', '5', '6', '7', '8', '9', 'R', 'H', 'E'],
        colWidths=[0.1] + [0.05] * 12, # Widths for Team Abbr, 9 innings, R, H, E
        loc='center',
        cellLoc='center',
        bbox=[0.1, 0.7, 0.8, 0.2] # Increased table size
    )
    linescore_table.set_visible(False) # Hidden by default

    # --- Main table for team names and status (Moved Lower) ---
    main_table = ax.table(
        cellText=[['', ''], ['', '']],
        colLabels=["Team", "Status"],
        colWidths=[0.3, 0.4],
        loc='center',
        cellLoc='center',
        bbox=[0.25, 0.45, 0.5, 0.2] # Repositioned below linescore
    )
    
    # --- Live details table for when a game is active (Moved Lower) ---
    live_table = ax.table(
        cellText=[['']],
        loc='center',
        cellLoc='center',
        bbox=[0.15, 0.35, 0.7, 0.1] # Repositioned below main table
    )
    live_table.set_visible(False)

    # --- Set the main title ---
    title = ax.set_title(
        f"DISTRICT SCOREBOARD\n{TEAM_ABBREVIATION}",
        fontsize=40, pad=40, fontweight='bold', color='white'
    )

    # --- Style the smaller tables ---
    for table in [main_table, live_table]:
        table.auto_set_font_size(False)
        table.set_fontsize(24)
        for key, cell in table.get_celld().items():
            cell.set_text_props(weight='bold', color='white')
            cell.set_facecolor('none')
            cell.set_edgecolor('none')

    # --- Style the linescore table with a larger font ---
    linescore_table.auto_set_font_size(False)
    linescore_table.set_fontsize(30) # Increased font size
    for key, cell in linescore_table.get_celld().items():
        cell.set_text_props(weight='bold', color='white')
        cell.set_facecolor('none')
        cell.set_edgecolor('none')

    # Style header rows for main and linescore tables
    for i in range(2):
        main_table.get_celld()[(0, i)].set_text_props(color='#AAAAAA')
    for i in range(13):
        linescore_table.get_celld()[(0, i)].set_text_props(color='#AAAAAA')

    # Color the R, H, E columns in the linescore table with a light grey background
    light_grey = '#4A4A4A'
    for row_idx in range(3): # Loop through header row (0) and data rows (1, 2)
        for col_idx in range(10, 13): # Columns for R, H, E
             linescore_table.get_celld()[(row_idx, col_idx)].set_facecolor(light_grey)

    plt.subplots_adjust(left=0.1, right=0.9, top=0.8, bottom=0.1)
    
    # Robust full-screen logic
    mng = plt.get_current_fig_manager()
    try:
        mng.window.showMaximized()
    except AttributeError:
        try:
            mng.full_screen_toggle()
        except AttributeError:
            print("Warning: Could not automatically maximize or full-screen the window.")

    return fig, ax, main_table, live_table, linescore_table, title

def update_display(main_table, live_table, linescore_table, title):
    """Fetches new data and updates the text and colors in the existing tables."""
    game = fetch_and_find_game()

    if not game:
        title.set_text(f"No Game Today for {TEAM_ABBREVIATION}\n(Or Error Fetching Data)")
        for row in range(1, 3):
            for col in range(2):
                main_table.get_celld()[(row, col)].get_text().set_text('')
        linescore_table.set_visible(False)
        live_table.set_visible(False)
        return

    status = game.get('status', {})
    status_type = status.get('type', {})
    status_name = status_type.get('name')
    status_detail = status_type.get('shortDetail', 'TBD')

    # If the game hasn't started, show only the time.
    if status_name == 'STATUS_SCHEDULED':
        linescore_table.set_visible(False)
        main_table.set_visible(True)
        time_part = ""
        if ' - ' in status_detail:
            time_part = status_detail.split(' - ')[1].strip()
        elif ',' in status_detail:
            time_part = status_detail.split(',')[1].strip()
        
        if time_part:
            status_detail = ' '.join(time_part.split(' ')[:-1])
    else:
        # If game is live or final, show the linescore table and hide the main table status
        linescore_table.set_visible(True)
        main_table.set_visible(False)


    competitors = game.get('competitors', [])
    away_comp = next((c for c in competitors if c.get('homeAway') == 'away'), {})
    home_comp = next((c for c in competitors if c.get('homeAway') == 'home'), {})

    away_team = away_comp.get('team', {}).get('abbreviation', 'N/A')
    home_team = home_comp.get('team', {}).get('abbreviation', 'N/A')
    
    # --- Update Main Table ---
    main_table.get_celld()[(1, 0)].get_text().set_text(away_team)
    main_table.get_celld()[(1, 1)].get_text().set_text(status_detail if status_name == 'STATUS_SCHEDULED' else '')
    main_table.get_celld()[(2, 0)].get_text().set_text(home_team)
    # The status in the main table is only shown for scheduled games
    main_table.get_celld()[(2, 1)].get_text().set_text('')

    
    # --- Update Linescore Table ---
    if status_name != 'STATUS_SCHEDULED':
        # Away Team Linescore
        linescore_table.get_celld()[(1, 0)].get_text().set_text(away_team)
        away_linescores = away_comp.get('linescores', [])
        # Clear previous scores before adding new ones
        for i in range(9):
            linescore_table.get_celld()[(1, i + 1)].get_text().set_text('')
        for i, score in enumerate(away_linescores):
            if i < 9: # Only show first 9 innings
                score_value = score.get('value')
                # Convert to int to remove decimals, then to string for display
                display_score = str(int(score_value)) if score_value is not None else ''
                linescore_table.get_celld()[(1, i + 1)].get_text().set_text(display_score)
        linescore_table.get_celld()[(1, 10)].get_text().set_text(str(away_comp.get('score', ''))) # R
        linescore_table.get_celld()[(1, 11)].get_text().set_text(str(away_comp.get('hits', '')))  # H
        linescore_table.get_celld()[(1, 12)].get_text().set_text(str(away_comp.get('errors', ''))) # E
        
        # Home Team Linescore
        linescore_table.get_celld()[(2, 0)].get_text().set_text(home_team)
        home_linescores = home_comp.get('linescores', [])
        # Clear previous scores
        for i in range(9):
            linescore_table.get_celld()[(2, i + 1)].get_text().set_text('')
        for i, score in enumerate(home_linescores):
            if i < 9:
                score_value = score.get('value')
                display_score = str(int(score_value)) if score_value is not None else ''
                linescore_table.get_celld()[(2, i + 1)].get_text().set_text(display_score)
        linescore_table.get_celld()[(2, 10)].get_text().set_text(str(home_comp.get('score', ''))) # R
        linescore_table.get_celld()[(2, 11)].get_text().set_text(str(home_comp.get('hits', '')))  # H
        linescore_table.get_celld()[(2, 12)].get_text().set_text(str(home_comp.get('errors', ''))) # E

    # Set team colors
    away_color = f"#{away_comp.get('team', {}).get('color', 'FFFFFF')}"
    away_alt_color = f"#{away_comp.get('team', {}).get('alternateColor', '000000')}"
    home_color = f"#{home_comp.get('team', {}).get('color', 'FFFFFF')}"
    home_alt_color = f"#{home_comp.get('team', {}).get('alternateColor', '000000')}"

    main_table.get_celld()[(1, 0)].set_facecolor(away_color)
    main_table.get_celld()[(1, 0)].get_text().set_color(away_alt_color)
    main_table.get_celld()[(2, 0)].set_facecolor(home_color)
    main_table.get_celld()[(2, 0)].get_text().set_color(home_alt_color)

    # Set team colors in linescore table if it's visible
    if status_name != 'STATUS_SCHEDULED':
        linescore_table.get_celld()[(1, 0)].set_facecolor(away_color)
        linescore_table.get_celld()[(1, 0)].get_text().set_color(away_alt_color)
        linescore_table.get_celld()[(2, 0)].set_facecolor(home_color)
        linescore_table.get_celld()[(2, 0)].get_text().set_color(home_alt_color)

    # --- Update Live Table ---
    if 'situation' in game and status_name == 'STATUS_IN_PROGRESS':
        live_table.set_visible(True)
        # Also update the status in the main table to show the current inning
        main_table.set_visible(True)
        main_table.get_celld()[(2, 1)].get_text().set_text(status_detail)
        
        sit = game['situation']
        outs_text = sit.get('outsText', '')
        bases = sit.get('baseRunnersText', 'Bases Empty')
        count = f"{sit.get('balls', 0)}-{sit.get('strikes', 0)} Count"
        live_text = f"Bases: {bases}   |   {outs_text}   |   {count}"
        live_table.get_celld()[(0, 0)].get_text().set_text(live_text)
    elif status_name != 'STATUS_SCHEDULED':
        # If the game is over, show the final status
        main_table.set_visible(True)
        main_table.get_celld()[(2, 1)].get_text().set_text(status_detail)
        live_table.set_visible(False)
    else:
        live_table.set_visible(False)
        
    title.set_text(f"DISTRICT HYPE\n{TEAM_ABBREVIATION} SCOREBOARD")

if __name__ == "__main__":
    fig, ax, main_table, live_table, linescore_table, title = setup_plot()
    while True:
        try:
            update_display(main_table, live_table, linescore_table, title)
        except Exception as e:
            print(f"An unexpected error occurred in the update loop: {e}")
            title.set_text("An Error Occurred\nCheck Console")
        
        try:
            plt.pause(UPDATE_INTERVAL_SECONDS)
        except Exception:
            print("Exiting loop.")
            break
