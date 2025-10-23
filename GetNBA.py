import requests
import time
import matplotlib as mpl
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import sys
import json
import os
from datetime import datetime
import textwrap

# --- Configuration ---
# You can set this to 'PHI', 'NYY', or any other MLB team abbreviation.
TEAM_ABBREVIATION = 'WSH'
UPDATE_INTERVAL_SECONDS = 10 

# --- Define the output paths based on the script's location ---
# This makes the script work correctly when run from cron
try:
    script_dir = os.path.dirname(os.path.abspath(__file__))
except NameError:
    # Fallback for interactive environments
    script_dir = os.getcwd()
    
output_dir = os.path.join(script_dir, "output")
SAVE_PATH_JSON = os.path.join(output_dir, "scoreboard_data.json")
SAVE_PATH_PNG = os.path.join(output_dir, "scoreboard.png")


# --- ESPN API Endpoint (Updated to a more stable endpoint) ---
API_URL = "http://site.api.espn.com/apis/site/v2/sports/basketball/nba/scoreboard"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3",
}

#mpl.rcParams['font.family'] = "sans-serif"
#mpl.rcParams['font.sans-serif'] = "Georgia"

def ensure_output_directory_exists():
    """Ensure the output directory exists."""
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        print(f"Created directory: {output_dir}")

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

def update_and_redraw_plot(fig):
    """Fetches new data and completely redraws the plot."""
    
    # Clear the entire figure to ensure a fresh draw
    plt.clf()
    ax = fig.add_subplot(111) # Add a new axes object
    ax.axis('off')
    
    # Adjust the top of the subplot to move all content down
    plt.subplots_adjust(top=0.78)
    
    game = fetch_and_find_game()

    # --- Set the main title ---
    title = ax.set_title(
        f"DC SCOREBOARD\n{TEAM_ABBREVIATION} HYPE",
        fontsize=50, pad=40, fontweight='bold', color='white', 
        #fontname='Georgia'
    )

    if not game:
        title.set_text(f"No Game Today for {TEAM_ABBREVIATION}\nAnd The Mets Still Suck")
        return

    status = game.get('status', {})
    status_type = status.get('type', {})
    status_name = status_type.get('name')
    status_detail = status_type.get('shortDetail', 'TBD')

    competitors = game.get('competitors', [])
    away_comp = next((c for c in competitors if c.get('homeAway') == 'away'), {})
    home_comp = next((c for c in competitors if c.get('homeAway') == 'home'), {})
    away_team = away_comp.get('team', {}).get('abbreviation', 'N/A')
    home_team = home_comp.get('team', {}).get('abbreviation', 'N/A')
    
    # Get team IDs for coloring logic
    away_team_id = away_comp.get('id')
    home_team_id = home_comp.get('id')
    
    # Get team colors
    away_color = f"#{away_comp.get('team', {}).get('color', 'FFFFFF')}"
    away_alt_color = f"#{away_comp.get('team', {}).get('alternateColor', '000000')}"
    home_color = f"#{home_comp.get('team', {}).get('color', 'FFFFFF')}"
    home_alt_color = f"#{home_comp.get('team', {}).get('alternateColor', '000000')}"

    # --- Draw tables based on game status ---
    if status_name == 'STATUS_SCHEDULED':
        # --- PRE-GAME DISPLAY ---
        
        # --- Odds Extraction for Pre-Game ---
        away_odds, home_odds = 'N/A', 'N/A'
        odds_container = game.get('odds')
        if isinstance(odds_container, list) and odds_container:
            odds_data = odds_container[0]
            away_odds = odds_data.get('details', 'N/A')
            home_odds = odds_data.get('overUnder', 'N/A')

            if (away_odds == 'N/A' or home_odds == 'N/A') and 'details' in odds_data:
                details_str = odds_data['details']
                parts = details_str.split(' ')
                if len(parts) == 2:
                    team_abbr_from_details, odds_val_from_details = parts
                    if team_abbr_from_details == away_team: away_odds = odds_val_from_details
                    elif team_abbr_from_details == home_team: home_odds = odds_val_from_details

        if str(away_odds).upper() == 'EVEN': away_odds = 100
        if str(home_odds).upper() == 'EVEN': home_odds = 100

        away_odds_str = f"+{away_odds}" if isinstance(away_odds, (int, float)) and away_odds > 0 else str(away_odds)
        home_odds_str = f"+{home_odds}" if isinstance(home_odds, (int, float)) and home_odds > 0 else str(home_odds)

        main_table = ax.table(
            cellText=[[away_team, '', away_odds_str], [home_team, '', home_odds_str]],
            colLabels=["Team", "Status", "Odds"], colWidths=[0.3, 0.4, 0.3],
            loc='center', cellLoc='center', bbox=[0.2, 0.65, 0.6, 0.4]
        )
        time_part = ""
        if ' - ' in status_detail:
            time_part = status_detail.split(' - ')[1].strip()
        elif ',' in status_detail:
            time_part = status_detail.split(',')[1].strip()
        status_detail = ' '.join(time_part.split(' ')[:-1]) if time_part else status_detail
        main_table.get_celld()[(1, 1)].get_text().set_text(status_detail)
        
        # Style the pre-game table
        main_table.auto_set_font_size(False)
        main_table.set_fontsize(32)
        for key, cell in main_table.get_celld().items():
            cell.set_text_props(weight='bold', color='white')
            cell.set_facecolor('none')
            cell.set_edgecolor('none')
        for i in range(3):
            main_table.get_celld()[(0, i)].set_text_props(color='#AAAAAA')
        for key, cell in main_table.get_celld().items():
                cell.set_text_props(weight='bold', color='white')
                cell.set_facecolor('#444444')
                cell.set_edgecolor('none')
        for i in range(3):
            main_table.get_celld()[(0, i)].set_facecolor('none')
        main_table.get_celld()[(1, 0)].set_facecolor(away_color)
        main_table.get_celld()[(1, 0)].get_text().set_color(away_alt_color)
        main_table.get_celld()[(2, 0)].set_facecolor(home_color)
        main_table.get_celld()[(2, 0)].get_text().set_color(home_alt_color)
        
        
    else:
        # --- LIVE OR POST-GAME DISPLAY ---
        # Draw Linescore Table
        linescore_table = ax.table(
            cellText=[[''] * 6] * 2,
            colLabels=['', '1', '2', '3', '4', 'TOT'],
            colWidths=[0.20] + [0.15] * 5, loc='center', cellLoc='center',
            bbox=[0.075, 0.55, 0.85, 0.35]
        )
        linescore_table.auto_set_font_size(False)
        linescore_table.set_fontsize(38)
        
        lighter_grey_bg = "#FFFFFF"
        for key, cell in linescore_table.get_celld().items():
            cell.set_facecolor(lighter_grey_bg)
            cell.set_text_props(weight='bold', color='white')
            cell.set_edgecolor('none')
            
        for i in range(6):
            linescore_table.get_celld()[(0, i)].set_text_props(color="#CBCBCB")
        
        for row_idx in range(3):
            for col_idx in range(6):
                linescore_table.get_celld()[(row_idx, col_idx)].set_facecolor("#3D3D3D")
        
        for row_idx in range(1, 3):
            for col_idx in range(1, 6):
                linescore_table.get_celld()[(row_idx, col_idx)].set_edgecolor("#555555")
        
        away_linescores = away_comp.get('linescores', [])
        home_linescores = home_comp.get('linescores', [])
        away_score = str(away_comp.get('score', ''))
        home_score = str(home_comp.get('score', ''))

        linescore_table.get_celld()[(1, 0)].get_text().set_text(away_team)
        linescore_table.get_celld()[(1, 0)].set_facecolor(away_color)
        linescore_table.get_celld()[(1, 0)].get_text().set_color(away_alt_color)
        for i, score in enumerate(away_linescores):
            if i < 9: linescore_table.get_celld()[(1, i + 1)].get_text().set_text(str(int(score.get('value', 0))))
        linescore_table.get_celld()[(1, 5)].get_text().set_text(away_score)
        
        linescore_table.get_celld()[(2, 0)].get_text().set_text(home_team)
        linescore_table.get_celld()[(2, 0)].set_facecolor(home_color)
        linescore_table.get_celld()[(2, 0)].get_text().set_color(home_alt_color)
        for i, score in enumerate(home_linescores):
            if i < 9: linescore_table.get_celld()[(2, i + 1)].get_text().set_text(str(int(score.get('value', 0))))
        linescore_table.get_celld()[(2, 5)].get_text().set_text(home_score)
        # Add the status detail below the linescore table
        ax.text(
            0.5, 1, status_detail,
            transform=ax.transAxes,
            fontsize=38,
            color="#26FF00",
            ha='center',
            va='top',
            fontweight='bold'
        )

        if status_name == 'STATUS_IN_PROGRESS':
            # --- Points, Assists, Rebounds Leaders Table ---
            # 3 rows: header, away, home
            par_table = ax.table(
                cellText=[['', '', ''], ['', '', ''], ['', '', '']],
                colLabels=["Points", "Assists", "Rebounds"],
                colWidths=[0.3, 0.3, 0.3], loc='center', cellLoc='center', bbox=[0.25, 0.1, 0.6, 0.3]
            )

            # Style the PAR table
            par_table.auto_set_font_size(False)
            par_table.set_fontsize(18)
            par_table_bg = '#555555'  # Lighter grey background
            for key, cell in par_table.get_celld().items():
                cell.set_text_props(weight='bold', color='white')
                cell.set_facecolor(par_table_bg)
                cell.set_edgecolor('none')

            # Style headers for PAR table
            for i in range(3):
                par_table.get_celld()[(0, i)].set_text_props(color='#AAAAAA')

            # Get leaders for points, assists, and rebounds for each team
            away_leaders = away_comp.get('leaders', [])
            home_leaders = home_comp.get('leaders', [])

            def get_leader_info(leaders, stat):
                for leader in leaders:
                    if leader.get('type', {}).get('name') == stat:
                        if leader.get('leaders'):
                            athlete = leader['leaders'][0].get('athlete', {})
                            value = leader['leaders'][0].get('value', 0)
                            name = athlete.get('displayName', 'N/A')
                            return f"{name} ({value})"
                return "N/A"

            # Populate PAR Table (row 1 = away, row 2 = home)
            par_table.get_celld()[(1, 0)].get_text().set_text(get_leader_info(away_leaders, 'points'))
            par_table.get_celld()[(1, 1)].get_text().set_text(get_leader_info(away_leaders, 'assists'))
            par_table.get_celld()[(1, 2)].get_text().set_text(get_leader_info(away_leaders, 'rebounds'))
            par_table.get_celld()[(2, 0)].get_text().set_text(get_leader_info(home_leaders, 'points'))
            par_table.get_celld()[(2, 1)].get_text().set_text(get_leader_info(home_leaders, 'assists'))
            par_table.get_celld()[(2, 2)].get_text().set_text(get_leader_info(home_leaders, 'rebounds'))

            # --- Dynamic Coloring for PAR Table ---
            for i in range(3):
                par_table.get_celld()[(1, i)].set_facecolor(away_color)
                par_table.get_celld()[(1, i)].get_text().set_color(away_alt_color)
                par_table.get_celld()[(2, i)].set_facecolor(home_color)
                par_table.get_celld()[(2, i)].get_text().set_color(home_alt_color)

        elif status_name == 'STATUS_FINAL':
             # --- Draw Post-Game Table ---
             post_game_table = ax.table(
                cellText=[[away_team, away_score, status_detail], [home_team, home_score, '']],
                #colLabels=["Team", "Runs", "Status"], 
                colWidths=[0.3, 0.2, 0.4],
                loc='center', cellLoc='center', bbox=[0.35, 0.3, 0.3, 0.25]
             )
             post_game_table.auto_set_font_size(False)
             post_game_table.set_fontsize(30)
             for key, cell in post_game_table.get_celld().items():
                cell.set_text_props(weight='bold', color='white')
                cell.set_facecolor('#444444')
                cell.set_edgecolor('none')
             #post_game_table.get_celld()[(0, 0)].set_text_props(color='#AAAAAA')
             #post_game_table.get_celld()[(0, 1)].set_text_props(color='#AAAAAA')
             #post_game_table.get_celld()[(0, 2)].set_text_props(color='#AAAAAA')
             post_game_table.get_celld()[(0, 0)].set_facecolor(away_color)
             post_game_table.get_celld()[(0, 0)].get_text().set_color(away_alt_color)
             post_game_table.get_celld()[(1, 0)].set_facecolor(home_color)
             post_game_table.get_celld()[(1, 0)].get_text().set_color(home_alt_color)

             # --- WINNER MESSAGE LOGIC ---
             winner_abbr = ''
             if int(away_score) > int(home_score):
                 winner_abbr = away_team
             elif int(home_score) > int(away_score):
                 winner_abbr = home_team
             
             if winner_abbr == TEAM_ABBREVIATION:
                 ax.text(0.5, 0.15, 'YANKEES WIN',
                         transform=ax.transAxes, fontsize=60, color='blue',
                         horizontalalignment='center', fontweight='bold',
                         bbox=dict(facecolor='white', alpha=0.5, edgecolor='none', boxstyle='round,pad=0.2'))

    update_time = datetime.now().strftime('%H:%M:%S')
    ax.text(0.99, 0.01, f'Last Updated: {update_time}',
            transform=ax.transAxes, fontsize=12, color='gray',
            horizontalalignment='right')
    
    fig.savefig(SAVE_PATH_PNG, facecolor=fig.get_facecolor(), edgecolor='none')
    print(f"Scoreboard image saved to {SAVE_PATH_PNG}")

if __name__ == "__main__":
    ensure_output_directory_exists()
    plt.ion()
    fig = plt.figure(figsize=(16, 9))
    fig.patch.set_facecolor('#606060')
    fig.canvas.mpl_connect('close_event', lambda event: sys.exit(0))

    mng = plt.get_current_fig_manager()
    try: mng.window.showMaximized()
    except AttributeError:
        try: mng.full_screen_toggle()
        except AttributeError: print("Warning: Could not automatically maximize or full-screen the window.")
    
    while True:
        now = datetime.now()
        if now.hour == 1 and now.minute >= 30:
            print(f"Shutdown time reached ({now.strftime('%H:%M')}). Exiting script.")
            sys.exit(0)

        try:
            update_and_redraw_plot(fig)
            plt.pause(UPDATE_INTERVAL_SECONDS)
        except Exception as e:
            print(f"An error occurred in the main loop: {e}")
            break
