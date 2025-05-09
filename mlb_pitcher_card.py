# %% [markdown]
# # MLB Pitcher Player Cards

# %% [markdown]
# Import Packages

# %%
import pandas as pd
import numpy as np
import pybaseball as pyb
import matplotlib.pyplot as plt
import seaborn as sns

# %% [markdown]
# Plotting Preferences

# %%
# Define font properties for general text
font_properties = {'family': 'DejaVu Sans', 'size': 12}

# Define font properties for titles
font_properties_titles = {'family': 'DejaVu Sans', 'size': 20}

# Define font properties for axes labels
font_properties_axes = {'family': 'DejaVu Sans', 'size': 16}

# Set the theme for seaborn plots
sns.set_theme(style='whitegrid', 
              palette='deep', 
              font='DejaVu Sans', 
              font_scale=1.5, 
              color_codes=True, 
              rc=None)

# Import matplotlib
import matplotlib as mpl

# Set the resolution of the figures to 300 DPI
mpl.rcParams['figure.dpi'] = 300

# %% [markdown]
# Color Palette

# %%
### PITCH COLORS ###
pitch_colors = {
    ## Fastballs ##
    'FF': {'color': '#C21014', 'name': '4-Seam Fastball'},
    'FA': {'color': '#C21014', 'name': 'Fastball'},
    'SI': {'color': '#F4B400', 'name': 'Sinker'},
    'FC': {'color': '#993300', 'name': 'Cutter'},

    ## Offspeed ##
    'CH': {'color': '#00B386', 'name': 'Changeup'},
    'FS': {'color': '#66CCCC', 'name': 'Splitter'},
    'SC': {'color': '#33CC99', 'name': 'Screwball'},
    'FO': {'color': '#339966', 'name': 'Forkball'},

    ## Sliders ##
    'SL': {'color': '#FFCC00', 'name': 'Slider'},
    'ST': {'color': '#CCCC66', 'name': 'Sweeper'},
    'SV': {'color': '#9999FF', 'name': 'Slurve'},

    ## Curveballs ##
    'KC': {'color': '#0000CC', 'name': 'Knuckle Curve'},
    'CU': {'color': '#3399FF', 'name': 'Curveball'},
    'CS': {'color': '#66CCFF', 'name': 'Slow Curve'},

    ## Knuckleball ##
    'KN': {'color': '#3333CC', 'name': 'Knuckleball'},

    ## Others ##
    'EP': {'color': '#999966', 'name': 'Eephus'},
    'PO': {'color': '#CCCCCC', 'name': 'Pitchout'},
    'UN': {'color': '#9C8975', 'name': 'Unknown'},
}

# Create a dictionary mapping pitch types to their colors
dict_color = dict(zip(pitch_colors.keys(), [pitch_colors[key]['color'] for key in pitch_colors]))

# Create a dictionary mapping pitch types to their colors
dict_pitch = dict(zip(pitch_colors.keys(), [pitch_colors[key]['name'] for key in pitch_colors]))

import matplotlib.pyplot as plt
# Create a figure and axis
fig, ax = plt.subplots(figsize=(6, 10))

# Plot a square for each pitch type with its corresponding color
for i, pitch_type in enumerate(pitch_colors):
    ax.add_patch(plt.Rectangle((0, i), 1, 1, color=pitch_colors[pitch_type]['color']))
    ax.text(-0.02, i + 0.5, f'{pitch_type}: {pitch_colors[pitch_type]["name"]} - {pitch_colors[pitch_type]["color"]}', va='center', ha='right')

# Set the y-axis limits and remove ticks
ax.set_ylim(0, len(pitch_colors))
ax.set_yticks([])
ax.set_ylabel('')

# Remove the x-axis
ax.set_xticks([])
ax.set_xlabel('')
ax.invert_yaxis()

# Set the title
ax.set_title('Pitch Colors')


# %% [markdown]
# Player Pitch Data

# %%
pitcher_id = 687922
df_pyb = pyb.statcast_pitcher('2025-03-27', '2025-04-27', pitcher_id)
df_pyb.head()

# %% [markdown]
# Data Processing

# %%
def df_processing(df_pyb: pd.DataFrame):
    df = df_pyb.copy()
    # Define the codes for different types of swings and whiffs
    swing_code = ['foul_bunt','foul','hit_into_play','swinging_strike', 'foul_tip',
                'swinging_strike_blocked','missed_bunt','bunt_foul_tip']
    whiff_code = ['swinging_strike', 'foul_tip', 'swinging_strike_blocked']

    # Create new columns in the DataFrame to indicate swing, whiff, in-zone, out-zone, and chase
    df['swing'] = (df['description'].isin(swing_code))
    df['whiff'] = (df['description'].isin(whiff_code))
    df['in_zone'] = (df['zone'] < 10)
    df['out_zone'] = (df['zone'] > 10)
    df['chase'] = (df.in_zone==False) & (df.swing == 1)

    # Convert the pitch type to a categorical variable
    df['pfx_z'] = df['pfx_z'] * 12
    df['pfx_x'] = df['pfx_x'] * 12
    return df

df = df_processing(df_pyb)

# %% [markdown]
# 2025 League Average Metrics

# %%
df_statcast_group = pd.read_csv('statcast_2025_grouped.csv')

# %% [markdown]
# Player Headshot

# %%
from PIL import Image
import requests
from io import BytesIO
from matplotlib.offsetbox import OffsetImage, AnnotationBbox

# Function to get an image from a URL and display it on the given axis
def player_headshot(pitcher_id: str, ax: plt.Axes):
    # Construct the URL for the player's headshot image
    url = f'https://img.mlbstatic.com/mlb-photos/image/'\
          f'upload/d_people:generic:headshot:67:current.png'\
          f'/w_640,q_auto:best/v1/people/{pitcher_id}/headshot/silo/current.png'

    # Send a GET request to the URL
    response = requests.get(url)

    # Open the image from the response content
    img = Image.open(BytesIO(response.content))


    # Display the image on the axis
    ax.set_xlim(0, 1.3)
    ax.set_ylim(0, 1)
    ax.imshow(img, extent=[0, 1, 0, 1], origin='upper')

    # Turn off the axis
    ax.axis('off')


# Call the player_headshot function with the pitcher ID and current axis
player_headshot(pitcher_id=pitcher_id, ax=plt.subplots(figsize=(1, 1))[1])

# %% [markdown]
# Player Bio

# %%
def player_bio(pitcher_id: str, ax: plt.Axes):
    # Construct the URL to fetch player data
    url = f"https://statsapi.mlb.com/api/v1/people?personIds={pitcher_id}&hydrate=currentTeam"

    # Send a GET request to the URL and parse the JSON response
    data = requests.get(url).json()

    # Extract player information from the JSON data
    player_name = data['people'][0]['fullName']
    pitcher_hand = data['people'][0]['pitchHand']['code']
    age = data['people'][0]['currentAge']
    height = data['people'][0]['height']
    weight = data['people'][0]['weight']

    # Display the player's name, handedness, age, height, and weight on the axis
    ax.text(0.5, 1, f'{player_name}', va='top', ha='center', fontsize=56)
    ax.text(0.5, 0.65, f'{pitcher_hand}HP, Age:{age}, {height}/{weight}', va='top', ha='center', fontsize=30)
    ax.text(0.5, 0.40, f'Season Pitching Summary', va='top', ha='center', fontsize=40)
    ax.text(0.5, 0.15, f'2025 MLB Season', va='top', ha='center', fontsize=30, fontstyle='italic')

    # Turn off the axis
    ax.axis('off')

# Call the player_bio function with the pitcher ID and a new axis of size 10x2
player_bio(pitcher_id, ax=plt.subplots(figsize=(20, 4))[1])

# %% [markdown]
# MLB/MILB Logos

# %%
# List of MLB and MILB teams and their corresponding logo URLs
teams = [
    # MLB
    {"team": "ATH", "logo_url": "https://a.espncdn.com/combiner/i?img=/i/teamlogos/mlb/500/scoreboard/ath.png&h=500&w=500"},
    {"team": "AZ", "logo_url": "https://a.espncdn.com/combiner/i?img=/i/teamlogos/mlb/500/scoreboard/ari.png&h=500&w=500"},
    {"team": "ATL", "logo_url": "https://a.espncdn.com/combiner/i?img=/i/teamlogos/mlb/500/scoreboard/atl.png&h=500&w=500"},
    {"team": "BAL", "logo_url": "https://a.espncdn.com/combiner/i?img=/i/teamlogos/mlb/500/scoreboard/bal.png&h=500&w=500"},
    {"team": "BOS", "logo_url": "https://a.espncdn.com/combiner/i?img=/i/teamlogos/mlb/500/scoreboard/bos.png&h=500&w=500"},
    {"team": "CHC", "logo_url": "https://a.espncdn.com/combiner/i?img=/i/teamlogos/mlb/500/scoreboard/chc.png&h=500&w=500"},
    {"team": "CWS", "logo_url": "https://a.espncdn.com/combiner/i?img=/i/teamlogos/mlb/500/scoreboard/chw.png&h=500&w=500"},
    {"team": "CIN", "logo_url": "https://a.espncdn.com/combiner/i?img=/i/teamlogos/mlb/500/scoreboard/cin.png&h=500&w=500"},
    {"team": "CLE", "logo_url": "https://a.espncdn.com/combiner/i?img=/i/teamlogos/mlb/500/scoreboard/cle.png&h=500&w=500"},
    {"team": "COL", "logo_url": "https://a.espncdn.com/combiner/i?img=/i/teamlogos/mlb/500/scoreboard/col.png&h=500&w=500"},
    {"team": "DET", "logo_url": "https://a.espncdn.com/combiner/i?img=/i/teamlogos/mlb/500/scoreboard/det.png&h=500&w=500"},
    {"team": "HOU", "logo_url": "https://a.espncdn.com/combiner/i?img=/i/teamlogos/mlb/500/scoreboard/hou.png&h=500&w=500"},
    {"team": "KC", "logo_url": "https://a.espncdn.com/combiner/i?img=/i/teamlogos/mlb/500/scoreboard/kc.png&h=500&w=500"},
    {"team": "LAA", "logo_url": "https://a.espncdn.com/combiner/i?img=/i/teamlogos/mlb/500/scoreboard/laa.png&h=500&w=500"},
    {"team": "LAD", "logo_url": "https://a.espncdn.com/combiner/i?img=/i/teamlogos/mlb/500/scoreboard/lad.png&h=500&w=500"},
    {"team": "MIA", "logo_url": "https://a.espncdn.com/combiner/i?img=/i/teamlogos/mlb/500/scoreboard/mia.png&h=500&w=500"},
    {"team": "MIL", "logo_url": "https://a.espncdn.com/combiner/i?img=/i/teamlogos/mlb/500/scoreboard/mil.png&h=500&w=500"},
    {"team": "MIN", "logo_url": "https://a.espncdn.com/combiner/i?img=/i/teamlogos/mlb/500/scoreboard/min.png&h=500&w=500"},
    {"team": "NYM", "logo_url": "https://a.espncdn.com/combiner/i?img=/i/teamlogos/mlb/500/scoreboard/nym.png&h=500&w=500"},
    {"team": "NYY", "logo_url": "https://a.espncdn.com/combiner/i?img=/i/teamlogos/mlb/500/scoreboard/nyy.png&h=500&w=500"},
    {"team": "PHI", "logo_url": "https://a.espncdn.com/combiner/i?img=/i/teamlogos/mlb/500/scoreboard/phi.png&h=500&w=500"},
    {"team": "PIT", "logo_url": "https://a.espncdn.com/combiner/i?img=/i/teamlogos/mlb/500/scoreboard/pit.png&h=500&w=500"},
    {"team": "SD", "logo_url": "https://a.espncdn.com/combiner/i?img=/i/teamlogos/mlb/500/scoreboard/sd.png&h=500&w=500"},
    {"team": "SF", "logo_url": "https://a.espncdn.com/combiner/i?img=/i/teamlogos/mlb/500/scoreboard/sf.png&h=500&w=500"},
    {"team": "SEA", "logo_url": "https://a.espncdn.com/combiner/i?img=/i/teamlogos/mlb/500/scoreboard/sea.png&h=500&w=500"},
    {"team": "STL", "logo_url": "https://a.espncdn.com/combiner/i?img=/i/teamlogos/mlb/500/scoreboard/stl.png&h=500&w=500"},
    {"team": "TB", "logo_url": "https://a.espncdn.com/combiner/i?img=/i/teamlogos/mlb/500/scoreboard/tb.png&h=500&w=500"},
    {"team": "TEX", "logo_url": "https://a.espncdn.com/combiner/i?img=/i/teamlogos/mlb/500/scoreboard/tex.png&h=500&w=500"},
    {"team": "TOR", "logo_url": "https://a.espncdn.com/combiner/i?img=/i/teamlogos/mlb/500/scoreboard/tor.png&h=500&w=500"},
    {"team": "WSH", "logo_url": "https://a.espncdn.com/combiner/i?img=/i/teamlogos/mlb/500/scoreboard/wsh.png&h=500&w=500"},

    # AAA
    {"team": "ABQ", "logo_url": "https://static.wikia.nocookie.net/minor-league-baseball/images/0/0b/Albuquerque_Isotopes.svg/revision/latest/smart/width/250/height/250?cb=20240522035213"},
    {"team": "BUF", "logo_url": "https://static.wikia.nocookie.net/minor-league-baseball/images/b/bc/Buffalo_Bisons.svg/revision/latest/smart/width/250/height/250?cb=20240522011841"},
    {"team": "CLT", "logo_url": "https://static.wikia.nocookie.net/minor-league-baseball/images/2/25/Charlotte_Knights.svg/revision/latest/smart/width/250/height/250?cb=20240522011908"},
    {"team": "COL", "logo_url": "https://static.wikia.nocookie.net/minor-league-baseball/images/1/19/Columbus_Clippers.svg/revision/latest/smart/width/250/height/250?cb=20240522011936"},
    {"team": "DUR", "logo_url": "https://static.wikia.nocookie.net/minor-league-baseball/images/c/c9/Durham_Bulls.svg/revision/latest/smart/width/250/height/250?cb=20240522011959"},
    {"team": "ELP", "logo_url": "https://static.wikia.nocookie.net/minor-league-baseball/images/4/4f/El_Paso_Chihuahuas.svg/revision/latest/smart/width/250/height/250?cb=20240522035226"},
    {"team": "GWN", "logo_url": "https://static.wikia.nocookie.net/minor-league-baseball/images/5/57/Gwinnett_Stripers.svg/revision/latest/smart/width/250/height/250?cb=20240522012022"},
    {"team": "IND", "logo_url": "https://static.wikia.nocookie.net/minor-league-baseball/images/b/b5/Indianapolis_Indians.svg/revision/latest/smart/width/250/height/250?cb=20240522012039"},
    {"team": "IOW", "logo_url": "https://static.wikia.nocookie.net/minor-league-baseball/images/e/e2/Iowa_Cubs.svg/revision/latest/smart/width/250/height/250?cb=20240522012105"},
    {"team": "JAX", "logo_url": "https://static.wikia.nocookie.net/minor-league-baseball/images/2/2b/Jacksonville_Jumbo_Shrimp.svg/revision/latest/smart/width/250/height/250?cb=20240522012119"},
    {"team": "LV", "logo_url": "https://static.wikia.nocookie.net/minor-league-baseball/images/b/ba/Las_Vegas_Aviators.svg/revision/latest/smart/width/250/height/250?cb=20240522035252"},
    {"team": "LEH", "logo_url": "https://static.wikia.nocookie.net/minor-league-baseball/images/3/30/Lehigh_Valley_IronPigs.svg/revision/latest/smart/width/250/height/250?cb=20240522012131"},
    {"team": "LOU", "logo_url": "https://static.wikia.nocookie.net/minor-league-baseball/images/d/d1/Louisville_Bats.svg/revision/latest/smart/width/250/height/250?cb=20240522012251"},
    {"team": "MEM", "logo_url": "https://static.wikia.nocookie.net/minor-league-baseball/images/7/75/Memphis_Redbirds.svg/revision/latest/smart/width/250/height/250?cb=20240522012306"},
    {"team": "NAS", "logo_url": "https://static.wikia.nocookie.net/minor-league-baseball/images/0/02/Nashville_Sounds.svg/revision/latest/smart/width/250/height/250?cb=20240522012505"},
    {"team": "NOR", "logo_url": "https://static.wikia.nocookie.net/minor-league-baseball/images/0/0d/Norfolk_Tides.svg/revision/latest/smart/width/250/height/250?cb=20240522012519"},
    {"team": "OKC", "logo_url": "https://static.wikia.nocookie.net/minor-league-baseball/images/7/75/Oklahoma_City_Comets.svg/revision/latest/scale-to-width-down/213?cb=20241028224007"},
    {"team": "OMA", "logo_url": "https://static.wikia.nocookie.net/minor-league-baseball/images/2/26/Omaha_Storm_Chasers.svg/revision/latest/scale-to-width-down/213?cb=20240522012708"},
    {"team": "RNO", "logo_url": "https://static.wikia.nocookie.net/minor-league-baseball/images/9/94/Reno_Aces.svg/revision/latest/scale-to-width-down/213?cb=20240522035313"},
    {"team": "ROC", "logo_url": "https://static.wikia.nocookie.net/minor-league-baseball/images/f/ff/Rochester_Red_Wings.svg/revision/latest/scale-to-width-down/213?cb=20240522012948"},
    {"team": "RR", "logo_url": "https://static.wikia.nocookie.net/minor-league-baseball/images/0/0c/Round_Rock_Express.svg/revision/latest/scale-to-width-down/213?cb=20240522034505"},
    {"team": "SAC", "logo_url": "https://static.wikia.nocookie.net/minor-league-baseball/images/7/7c/Sacramento_River_Cats.svg/revision/latest/scale-to-width-down/213?cb=20240522035338"},
    {"team": "SL", "logo_url": "https://static.wikia.nocookie.net/minor-league-baseball/images/8/89/Salt_Lake_Bees.svg/revision/latest/scale-to-width-down/155?cb=20240522035345"},
    {"team": "SWB", "logo_url": "https://static.wikia.nocookie.net/minor-league-baseball/images/a/a5/Scranton_Wilkes-Barre_RailRiders_3.svg/revision/latest/scale-to-width-down/213?cb=20240522012923"},
    {"team": "STP", "logo_url": "https://static.wikia.nocookie.net/minor-league-baseball/images/9/9d/St._Paul_Saints.svg/revision/latest/scale-to-width-down/164?cb=20240522012629"},
    {"team": "SUG", "logo_url": "https://static.wikia.nocookie.net/minor-league-baseball/images/4/4c/Sugar_Land_Space_Cowboys.svg/revision/latest/scale-to-width-down/166?cb=20240522035238"},
    {"team": "SYR", "logo_url": "https://static.wikia.nocookie.net/minor-league-baseball/images/c/cd/Syracuse_Mets.svg/revision/latest/scale-to-width-down/141?cb=20240522013011"},
    {"team": "TAC", "logo_url": "https://static.wikia.nocookie.net/minor-league-baseball/images/7/71/Tacoma_Rainiers.svg/revision/latest/scale-to-width-down/213?cb=20240522035352"},
    {"team": "TOL", "logo_url": "https://static.wikia.nocookie.net/minor-league-baseball/images/d/d3/Toledo_Mud_Hens.svg/revision/latest/scale-to-width-down/213?cb=20240522012741"},
    {"team": "WOR", "logo_url": "https://static.wikia.nocookie.net/minor-league-baseball/images/b/b7/Worcester_Red_Sox.svg/revision/latest/scale-to-width-down/213?cb=20240522013224"}
]

# Create a DataFrame from the list of dictionaries
df_image = pd.DataFrame(teams)
image_dict = df_image.set_index('team')['logo_url'].to_dict()

# %%
pitcher_id = 677161

# %% [markdown]
# Plot Logo

# %%
def plot_logo(pitcher_id: str, ax: plt.Axes):
    try:
        # Get player info and current team
        url = f"https://statsapi.mlb.com/api/v1/people?personIds={pitcher_id}&hydrate=currentTeam"
        data = requests.get(url).json()
        url_team = 'https://statsapi.mlb.com/' + data['people'][0]['currentTeam']['link']
        data_team = requests.get(url_team).json()

        # Extract team abbreviation
        team_abb = data_team['teams'][0].get('abbreviation')

        # If abbreviation is missing or not in the dictionary, skip
        if not team_abb or team_abb not in image_dict:
            print(f"Team abbreviation '{team_abb}' not found in logo dictionary.")
            ax.axis('off')
            return

        # Fetch and display the logo image
        logo_url = image_dict[team_abb]
        response = requests.get(logo_url)
        img = Image.open(BytesIO(response.content))

        ax.set_xlim(0, 1.3)
        ax.set_ylim(0, 1)
        ax.imshow(img, extent=[0.3, 1.3, 0, 1], origin='upper')
        ax.axis('off')

    except Exception as e:
        print(f"Could not load logo for pitcher ID {pitcher_id}: {e}")
        ax.axis('off')

plot_logo(pitcher_id, ax=plt.subplots(figsize=(1, 1))[1])

# %% [markdown]
# Pitch Velocity KDE

# %%
import math
import matplotlib.gridspec as gridspec

def velocity_kdes(df: pd.DataFrame,
                  ax: plt.Axes,
                  gs: gridspec,
                  gs_x: list,
                  gs_y: list,
                  fig: plt.Figure,
                  df_statcast_group: pd.DataFrame):

    # Get the count of each pitch type and sort them in descending order
    sorted_value_counts = df['pitch_type'].value_counts().sort_values(ascending=False)

    # Get the list of pitch types ordered from most to least frequent
    items_in_order = sorted_value_counts.index.tolist()

    # Turn off the axis and set the title for the main plot
    ax.axis('off')
    ax.set_title('Pitch Velocity Distribution', fontdict={'size': 20})

    # Create a grid for the inner subplots
    inner_grid_1 = gridspec.GridSpecFromSubplotSpec(len(items_in_order), 1, subplot_spec=gs[gs_x[0]:gs_x[-1], gs_y[0]:gs_y[-1]])
    ax_top = []

    # Create subplots for each pitch type
    for inner in inner_grid_1:
        ax_top.append(fig.add_subplot(inner))

    ax_number = 0

    # Loop through each pitch type and plot the velocity distribution
    for i in items_in_order:
        # Check if all release speeds for the pitch type are the same
        if np.unique(df[df['pitch_type'] == i]['release_speed']).size == 1:
            # Plot a single line if all values are the same
            ax_top[ax_number].plot([np.unique(df[df['pitch_type'] == i]['release_speed']),
                                    np.unique(df[df['pitch_type'] == i]['release_speed'])], [0, 1], linewidth=4,
                                   color=dict_color[df[df['pitch_type'] == i]['pitch_type'].values[0]], zorder=20)
        else:
            # Plot the KDE for the release speeds
            sns.kdeplot(df[df['pitch_type'] == i]['release_speed'], ax=ax_top[ax_number], fill=True,
                        clip=(df[df['pitch_type'] == i]['release_speed'].min(), df[df['pitch_type'] == i]['release_speed'].max()),
                        color=dict_color[df[df['pitch_type'] == i]['pitch_type'].values[0]])
        
        # Plot the mean release speed for the current data
        df_average = df[df['pitch_type'] == i]['release_speed']
        ax_top[ax_number].plot([df_average.mean(), df_average.mean()],
                               [ax_top[ax_number].get_ylim()[0], ax_top[ax_number].get_ylim()[1]],
                               color=dict_color[df[df['pitch_type'] == i]['pitch_type'].values[0]],
                               linestyle='--')

        # Plot the mean release speed for the statcast group data
        df_average = df_statcast_group[df_statcast_group['pitch_type'] == i]['release_speed']
        ax_top[ax_number].plot([df_average.mean(), df_average.mean()],
                               [ax_top[ax_number].get_ylim()[0], ax_top[ax_number].get_ylim()[1]],
                               color=dict_color[df[df['pitch_type'] == i]['pitch_type'].values[0]],
                               linestyle=':')

        # Set the x-axis limits
        ax_top[ax_number].set_xlim(math.floor(df['release_speed'].min() / 5) * 5, math.ceil(df['release_speed'].max() / 5) * 5)
        ax_top[ax_number].set_xlabel('')
        ax_top[ax_number].set_ylabel('')

        # Hide the top, right, and left spines for all but the last subplot
        if ax_number < len(items_in_order) - 1:
            ax_top[ax_number].spines['top'].set_visible(False)
            ax_top[ax_number].spines['right'].set_visible(False)
            ax_top[ax_number].spines['left'].set_visible(False)
            ax_top[ax_number].tick_params(axis='x', colors='none')

        # Set the x-ticks and y-ticks
        ax_top[ax_number].set_xticks(range(math.floor(df['release_speed'].min() / 5) * 5, math.ceil(df['release_speed'].max() / 5) * 5, 5))
        ax_top[ax_number].set_yticks([])
        ax_top[ax_number].grid(axis='x', linestyle='--')

        # Add text label for the pitch type
        ax_top[ax_number].text(-0.01, 0.5, i, transform=ax_top[ax_number].transAxes,
                               fontsize=14, va='center', ha='right')
        ax_number += 1

    # Hide the top, right, and left spines for the last subplot
    ax_top[-1].spines['top'].set_visible(False)
    ax_top[-1].spines['right'].set_visible(False)
    ax_top[-1].spines['left'].set_visible(False)

    # Set the x-ticks and x-label for the last subplot
    ax_top[-1].set_xticks(list(range(math.floor(df['release_speed'].min() / 5) * 5, math.ceil(df['release_speed'].max() / 5) * 5, 5)))
    ax_top[-1].set_xlabel('Velocity (mph)')

# Create a figure and axis
fig, ax = plt.subplots(figsize=(6, 6))
velocity_kdes(df=df,
              ax=ax,
              gs=gridspec.GridSpec(1, 1),
              gs_x=[0, 1],
              gs_y=[0, 1],
              fig=fig,
              df_statcast_group=df_statcast_group)

# %% [markdown]
# Short Form Pitch Movement

# %% [markdown]
# Pitch Movement WITH LEAGUE AVERAGES

# %%
df_pitch_movement = pd.read_csv('statcast_2025_pitch_movement.csv')

# %%
from matplotlib.ticker import FuncFormatter
from matplotlib.patches import Ellipse
import matplotlib.transforms as transforms

def add_ellipse(ax, x, y, color, label):
    if len(x) < 2:
        return  # skip if not enough points to compute covariance

    cov = np.cov(x, y)
    lambda_, v = np.linalg.eig(cov)
    lambda_ = np.sqrt(lambda_)

    angle = np.degrees(np.arctan2(*v[:, 0][::-1]))

    ell = Ellipse(
        xy=(np.mean(x), np.mean(y)),
        width=lambda_[0]*4,
        height=lambda_[1]*4,
        angle=angle,
        edgecolor=color,
        facecolor=color,     # same color as pitch
        alpha=0.2,            # transparency for filled ellipse
        lw=1.5,
        zorder=1
    )
    ax.add_patch(ell)


def break_plot(df: pd.DataFrame, ax: plt.Axes, df_statcast_group: pd.DataFrame = None):

    # Check if the pitcher throws with the right hand
    if df['p_throws'].values[0] == 'R':
        sns.scatterplot(ax=ax,
                        x=df['pfx_x']*-1,
                        y=df['pfx_z'],
                        hue=df['pitch_type'],
                        palette=dict_color,
                        ec='black',
                        alpha=1,
                        zorder=2)

    # Check if the pitcher throws with the left hand
    if df['p_throws'].values[0] == 'L':
        sns.scatterplot(ax=ax,
                        x=df['pfx_x'],
                        y=df['pfx_z'],
                        hue=df['pitch_type'],
                        palette=dict_color,
                        ec='black',
                        alpha=1,
                        zorder=2)

    # Add league average ellipses for reference
    if df_statcast_group is not None:
        pitcher_hand = df['p_throws'].iloc[0]

        for pitch_type in df['pitch_type'].unique():
            match = df_statcast_group[
                (df_statcast_group['pitch_type'] == pitch_type) &
                (df_statcast_group['p_throws'] == pitcher_hand)
            ]

            if match.empty:
                continue

            row = match.iloc[0]

            # Flip horizontal for RHP to match plot orientation
            league_x = -row['pfx_x'] if pitcher_hand == 'R' else row['pfx_x']
            league_y = row['pfx_z']

            color = dict_color.get(pitch_type, 'gray')

            ell = Ellipse(
                xy=(league_x, league_y),
                width=7,        # make this bigger/smaller as needed
                height=7,
                angle=0,
                edgecolor=color,
                facecolor=color,
                alpha=0.5,
                lw=2,
                zorder=0
            )
            ax.add_patch(ell)


    # Draw horizontal and vertical lines at y=0 and x=0 respectively
    ax.axhline(y=0, color='#808080', alpha=0.5, linestyle='--', zorder=1)
    ax.axvline(x=0, color='#808080', alpha=0.5, linestyle='--', zorder=1)

    # Set the labels for the x and y axes
    ax.set_xlabel('Horizontal Break (in)', fontdict=font_properties_axes)
    ax.set_ylabel('Induced Vertical Break (in)', fontdict=font_properties_axes)

    # Add title and subtitle to plot
    if 'arm_angle' in df.columns:
        avg_angle = df['arm_angle'].mean()
    
        # Set plot title
        title = f"Pitch Breaks - Arm Angle: {avg_angle:.0f}°"

        # Set title with extra padding to make room for subtitle
        ax.set_title(title, fontdict=font_properties_titles, pad=25)
        
        # Additional Note: MLB average movement ellipses
        ax.text(0.5, 1.02, "Note: Ellipses = League average pitch movement",
            transform=ax.transAxes,
            ha='center',
            fontsize=11,
            style='italic',
            color='dimgray',
            zorder=4)

    # Remove the legend
    ax.get_legend().remove()

    # Set the tick positions and labels for the x and y axes
    ax.set_xticks(range(-20, 21, 10))
    ax.set_xticklabels(range(-20, 21, 10), fontdict=font_properties)
    ax.set_yticks(range(-20, 21, 10))
    ax.set_yticklabels(range(-20, 21, 10), fontdict=font_properties)

    # Set the limits for the x and y axes
    ax.set_xlim((-25, 25))
    ax.set_ylim((-25, 25))

    # Add text annotations based on the pitcher's throwing hand
    if df['p_throws'].values[0] == 'R':
        ax.text(-24.2, -24.2, s='← Glove Side', fontstyle='italic', ha='left', va='bottom',
                bbox=dict(facecolor='white', edgecolor='black'), fontsize=10, zorder=3)
        ax.text(24.2, -24.2, s='Arm Side →', fontstyle='italic', ha='right', va='bottom',
                bbox=dict(facecolor='white', edgecolor='black'), fontsize=10, zorder=3)

    if df['p_throws'].values[0] == 'L':
        ax.invert_xaxis()
        ax.text(24.2, -24.2, s='← Arm Side', fontstyle='italic', ha='left', va='bottom',
                bbox=dict(facecolor='white', edgecolor='black'), fontsize=10, zorder=3)
        ax.text(-24.2, -24.2, s='Glove Side →', fontstyle='italic', ha='right', va='bottom',
                bbox=dict(facecolor='white', edgecolor='black'), fontsize=10, zorder=3)
        
    # Add dashed arm angle line from the origin
    if 'arm_angle' in df.columns and not df['arm_angle'].isnull().all():
        mean_angle_deg = df['arm_angle'].mean()
        mean_angle_rad = np.deg2rad(mean_angle_deg)  # Don't subtract from π

        length = 35  # Length of the line

        # Compute end coordinates regardless of throwing hand
        x_end = length * np.cos(mean_angle_rad)
        y_end = length * np.sin(mean_angle_rad)

        ax.plot([0, x_end], [0, y_end], linestyle='--', color='black', alpha=0.7, label='Arm Angle')
  
    # Set the aspect ratio of the plot to be equal
    ax.set_aspect('equal', adjustable='box')

    # Format the x and y axis tick labels as integers
    ax.xaxis.set_major_formatter(FuncFormatter(lambda x, _: int(x)))
    ax.yaxis.set_major_formatter(FuncFormatter(lambda x, _: int(x)))

break_plot(df=df, ax=plt.subplots(figsize=(6, 6))[1], df_statcast_group=df_pitch_movement)

# %% [markdown]
# Season Pitching Summary

# %%
def fangraphs_pitching_leaderboards(season:int):
    url = f"https://www.fangraphs.com/api/leaders/major-league/data?age=&pos=all&stats=pit&lg=all&season={season}&season1={season}&ind=0&qual=0&type=8&month=0&pageitems=500000"
    data = requests.get(url).json()
    df = pd.DataFrame(data=data['data'])
    return df

df_fangraphs = fangraphs_pitching_leaderboards(season = 2025)
df_fangraphs.head()

# %%
### FANGRAPHS STATS DICT ###
fangraphs_stats_dict = {'IP':{'table_header':'$\\bf{IP}$','format':'.1f',} ,
 'TBF':{'table_header':'$\\bf{PA}$','format':'.0f',} ,
 'AVG':{'table_header':'$\\bf{AVG}$','format':'.3f',} ,
 'K/9':{'table_header':'$\\bf{K\/9}$','format':'.2f',} ,
 'BB/9':{'table_header':'$\\bf{BB\/9}$','format':'.2f',} ,
 'K/BB':{'table_header':'$\\bf{K\/BB}$','format':'.2f',} ,
 'HR/9':{'table_header':'$\\bf{HR\/9}$','format':'.2f',} ,
 'K%':{'table_header':'$\\bf{K\%}$','format':'.1%',} ,
 'BB%':{'table_header':'$\\bf{BB\%}$','format':'.1%',} ,
 'K-BB%':{'table_header':'$\\bf{K-BB\%}$','format':'.1%',} ,
 'WHIP':{'table_header':'$\\bf{WHIP}$','format':'.2f',} ,
 'BABIP':{'table_header':'$\\bf{BABIP}$','format':'.3f',} , 
 'GB%': {'table_header':'$\\bf{GB\%}$','format':'.1%',} ,
 'LOB%':{'table_header':'$\\bf{LOB\%}$','format':'.1%',} ,
 'xFIP':{'table_header':'$\\bf{xFIP}$','format':'.2f',} ,
 'FIP':{'table_header':'$\\bf{FIP}$','format':'.2f',} ,
 'H':{'table_header':'$\\bf{H}$','format':'.0f',} ,
 '2B':{'table_header':'$\\bf{2B}$','format':'.0f',} ,
 '3B':{'table_header':'$\\bf{3B}$','format':'.0f',} ,
 'R':{'table_header':'$\\bf{R}$','format':'.0f',} ,
 'ER':{'table_header':'$\\bf{ER}$','format':'.0f',} ,
 'HR':{'table_header':'$\\bf{HR}$','format':'.0f',} ,
 'BB':{'table_header':'$\\bf{BB}$','format':'.0f',} ,
 'IBB':{'table_header':'$\\bf{IBB}$','format':'.0f',} ,
 'HBP':{'table_header':'$\\bf{HBP}$','format':'.0f',} ,
 'SO':{'table_header':'$\\bf{SO}$','format':'.0f',} ,
 'OBP':{'table_header':'$\\bf{OBP}$','format':'.0f',} ,
 'SLG':{'table_header':'$\\bf{SLG}$','format':'.0f',} ,
 'ERA':{'table_header':'$\\bf{ERA}$','format':'.2f',} ,
 'wOBA':{'table_header':'$\\bf{wOBA}$','format':'.3f',} ,
 'G':{'table_header':'$\\bf{G}$','format':'.0f',},
 'GS':{'table_header':'$\\bf{GS}$','format':'.0f',} }

# %%
def fangraphs_pitcher_stats(pitcher_id: int, ax: plt.Axes,stats:list, season:int,fontsize:int=20):
    df_fangraphs = fangraphs_pitching_leaderboards(season = season)

    df_fangraphs_pitcher = df_fangraphs[df_fangraphs['xMLBAMID'] == pitcher_id][stats].reset_index(drop=True)
    df_fangraphs_pitcher = df_fangraphs_pitcher.astype('object')

    df_fangraphs_pitcher.loc[0] = [format(df_fangraphs_pitcher[x][0],fangraphs_stats_dict[x]['format']) if df_fangraphs_pitcher[x][0] != '---' else '---' for x in df_fangraphs_pitcher]
    table_fg = ax.table(cellText=df_fangraphs_pitcher.values, colLabels=stats, cellLoc='center',
                    bbox=[0.00, 0.0, 1, 1])

    table_fg.set_fontsize(fontsize)


    new_column_names = [fangraphs_stats_dict[x]['table_header'] if x in df_fangraphs_pitcher else '---' for x in stats]
    # #new_column_names = ['Pitch Name', 'Pitch%', 'Velocity', 'Spin Rate','Exit Velocity', 'Whiff%', 'CSW%']
    for i, col_name in enumerate(new_column_names):
        table_fg.get_celld()[(0, i)].get_text().set_text(col_name)

    ax.axis('off')

stats = ['G','GS', 'IP','WHIP','ERA', 'FIP', 'K%', 'BB%', 'GB%']
fangraphs_pitcher_stats(pitcher_id = pitcher_id,
                        ax = plt.subplots(figsize=(10, 1))[1],
                        stats = stats,
                        season = 2025)

# %% [markdown]
# Pitcher Percentile Rankings

# %%
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import matplotlib.colors as mcolors

def plot_percentile_rankings_by_pitcher(df_fangraphs, pitcher_id, ax=None):
    label_map = {
        'xERA': 'xERA',
        'EV': 'Avg Exit Velocity',
        'pfxZone%': 'Zone%',
        'pfxO-Swing%': 'O-Swing%',
        'K%': 'K%',
        'BB%': 'BB%',
        'Barrel%': 'Barrel%',
        'HardHit%': 'Hard-Hit%',
        'GB%': 'GB%',
    }

    # Find the pitcher by pitcher_id (xMLBAMID)
    pitcher_row = df_fangraphs[df_fangraphs['xMLBAMID'] == pitcher_id].iloc[0]

    # Calculate percentiles
    percentiles = {}
    for col in label_map.keys():
        percentiles[col] = (df_fangraphs[col] < pitcher_row[col]).mean() * 100

    # Reverse metrics for which lower is better
    reverse_metrics = ['xERA', 'EV', 'Barrel%', 'HardHit%', 'BB%']
    for metric in reverse_metrics:
        percentiles[metric] = 100 - percentiles[metric]

    # Prepare data for plotting
    plot_data = pd.DataFrame({
        'Metric': [label_map[k] for k in label_map],
        'Percentile': [percentiles[k] for k in label_map],
        'Value': [
            round(pitcher_row[k] * 100, 1) if '%' in k else round(pitcher_row[k], 2)
            for k in label_map
        ]
    })

    # Ensure the DataFrame is ordered by label_map
    plot_data['Metric'] = pd.Categorical(
        plot_data['Metric'],
        categories=[label_map[k] for k in label_map],
        ordered=True
    )
    plot_data = plot_data.sort_values('Metric', ascending=False)

    # Normalize the percentiles for colormap
    norm = mcolors.Normalize(vmin=0, vmax=100)
    cmap = plt.get_cmap("coolwarm")

    # If no axis is passed, create a new figure and axis
    if ax is None:
        fig, ax = plt.subplots(figsize=(12, 7))  # Adjusted figsize to avoid squishing

    # Plotting the percentile rankings
    for i, row in plot_data.iterrows():
        color = cmap(norm(row['Percentile']))
        ax.barh(row['Metric'], row['Percentile'], color=color)

        # Adjust the placement of the percentile text
        if row['Percentile'] > 90:
            percentile_x = row['Percentile'] - 5
            label_color = 'white'
            ha = 'right'
        else:
            percentile_x = row['Percentile'] + 1
            label_color = 'black'
            ha = 'left'

        ax.text(percentile_x, row['Metric'], f"{int(row['Percentile'])}",
        va='center', ha=ha, color=label_color)

        # Handle special formatting for xERA
        value_label = f"{row['Value']:.2f}" if row['Metric'] == "xERA" else f"{row['Value']:.1f}"
        ax.text(105, row['Metric'], value_label, va='center', ha='left')

    # Decorations
    ax.axvline(33, color='lightgray', linestyle='--')
    ax.axvline(67, color='lightgray', linestyle='--')
    ax.set_title("Percentile Rankings (Fangraphs)", fontsize=20)
    ax.set_xlabel("Percentile")
    ax.spines['right'].set_visible(False)
    ax.set_xlim(0, 100)

    # Adjust layout for a better fit (important for tight layouts)
    if ax is None:
        plt.tight_layout()
        plt.subplots_adjust(left=0.05, right=0.95, top=0.95, bottom=0.05)  # Fine-tuned margins
        plt.show()

# Example of standalone usage:
pitcher_id = 668881  # example pitcher ID
plot_percentile_rankings_by_pitcher(df_fangraphs, pitcher_id)  # Standalone call


# %% [markdown]
# Pitch Metric Summary

# %%
def df_grouping(df: pd.DataFrame):
    # Group the DataFrame by pitch type and aggregate various statistics
    df_group = df.groupby(['pitch_type']).agg(
                        pitch = ('pitch_type','count'),  # Count of pitches
                        release_speed = ('release_speed','mean'),  # Average release speed
                        pfx_z = ('pfx_z','mean'),  # Average vertical movement
                        pfx_x = ('pfx_x','mean'),  # Average horizontal movement
                        release_spin_rate = ('release_spin_rate','mean'),  # Average spin rate
                        release_pos_x = ('release_pos_x','mean'),  # Average horizontal release position
                        release_pos_z = ('release_pos_z','mean'),  # Average vertical release position
                        release_extension = ('release_extension','mean'),  # Average release extension
                        delta_run_exp = ('delta_run_exp','sum'),  # Total change in run expectancy
                        swing = ('swing','sum'),  # Total swings
                        whiff = ('whiff','sum'),  # Total whiffs
                        in_zone = ('in_zone','sum'),  # Total in-zone pitches
                        out_zone = ('out_zone','sum'),  # Total out-of-zone pitches
                        chase = ('chase','sum'),  # Total chases
                    ).reset_index()
    
    # Calculate xwOBAcon (xwOBA on batted balls)
    df_group['xwobacon'] = df_group['pitch_type'].map(
    lambda pt: df[(df['pitch_type'] == pt) & (df['type'] == 'X')]['estimated_woba_using_speedangle'].mean())

    # Map pitch types to their descriptions
    df_group['pitch_description'] = df_group['pitch_type'].map(dict_pitch)

    # Calculate pitch usage as a percentage of total pitches
    df_group['pitch_usage'] = df_group['pitch'] / df_group['pitch'].sum()

    # Calculate whiff rate as the ratio of whiffs to swings
    df_group['whiff_rate'] = df_group['whiff'] / df_group['swing']

    # Calculate in-zone rate as the ratio of in-zone pitches to total pitches
    df_group['in_zone_rate'] = df_group['in_zone'] / df_group['pitch']

    # Calculate chase rate as the ratio of chases to out-of-zone pitches
    df_group['chase_rate'] = df_group['chase'] / df_group['out_zone']

    # Calculate delta run expectancy per 100 pitches
    df_group['delta_run_exp_per_100'] = -df_group['delta_run_exp'] / df_group['pitch'] * 100

    # Map pitch types to their colors
    df_group['color'] = df_group['pitch_type'].map(dict_color)

    # Sort the DataFrame by pitch usage in descending order
    df_group = df_group.sort_values(by='pitch_usage', ascending=False)
    color_list = df_group['color'].tolist()

    plot_table_all = pd.DataFrame(data={
                'pitch_type': 'All',
                'pitch_description': 'All',  # Description for the summary row
                'pitch': df['pitch_type'].count(),  # Total count of pitches
                'pitch_usage': 1,  # Usage percentage for all pitches (100%)
                'release_speed': np.nan,  # Placeholder for release speed
                'pfx_z': np.nan,  # Placeholder for vertical movement
                'pfx_x': np.nan,  # Placeholder for horizontal movement
                'release_spin_rate': np.nan,  # Placeholder for spin rate
                'release_pos_x': np.nan,  # Placeholder for horizontal release position
                'release_pos_z': np.nan,  # Placeholder for vertical release position
                'release_extension': df['release_extension'].mean(),  # Placeholder for release extension
                'delta_run_exp_per_100': df['delta_run_exp'].sum() / df['pitch_type'].count() * -100,  # Delta run expectancy per 100 pitches
                'whiff_rate': df['whiff'].sum() / df['swing'].sum(),  # Whiff rate
                'in_zone_rate': df['in_zone'].sum() / df['pitch_type'].count(),  # In-zone rate
                'chase_rate': df['chase'].sum() / df['out_zone'].sum(),  # Chase rate
                'xwobacon': df[df['type'] == 'X']['estimated_woba_using_speedangle'].mean() # Average expected wOBA on batted balls
            }, index=[0])

    # Concatenate the group DataFrame with the summary row DataFrame
    df_plot = pd.concat([df_group, plot_table_all], ignore_index=True)


    return df_plot, color_list

# %%
pitch_stats_dict = {
    'pitch': {'table_header': '$\\bf{Count}$', 'format': '.0f'},
    'release_speed': {'table_header': '$\\bf{Velocity}$', 'format': '.1f'},
    'pfx_z': {'table_header': '$\\bf{iVB}$', 'format': '.1f'},
    'pfx_x': {'table_header': '$\\bf{HB}$', 'format': '.1f'},
    'release_spin_rate': {'table_header': '$\\bf{Spin}$', 'format': '.0f'},
    'release_pos_x': {'table_header': '$\\bf{hRel}$', 'format': '.1f'},
    'release_pos_z': {'table_header': '$\\bf{vRel}$', 'format': '.1f'},
    'release_extension': {'table_header': '$\\bf{Ext.}$', 'format': '.1f'},
    'xwobacon': {'table_header': '$\\bf{xwOBA}$\n$\\bf{con}$', 'format': '.3f'},
    'pitch_usage': {'table_header': '$\\bf{Pitch\%}$', 'format': '.1%'},
    'whiff_rate': {'table_header': '$\\bf{Whiff\%}$', 'format': '.1%'},
    'in_zone_rate': {'table_header': '$\\bf{Zone\%}$', 'format': '.1%'},
    'chase_rate': {'table_header': '$\\bf{Chase\%}$', 'format': '.1%'},
    'delta_run_exp_per_100': {'table_header': '$\\bf{RV\//100}$', 'format': '.1f'}
    }

table_columns = [ 'pitch_description',
            'pitch',
            'pitch_usage',
            'release_speed',
            'pfx_z',
            'pfx_x',
            'release_spin_rate',
            'release_pos_x',
            'release_pos_z',
            'release_extension',
            'delta_run_exp_per_100',
            'in_zone_rate',
            'chase_rate',
            'whiff_rate',
            'xwobacon',
            ]

# %%
def plot_pitch_format(df: pd.DataFrame):
    # Create a DataFrame for the summary row with aggregated statistics for all pitches
    df_group = df[table_columns].fillna('—')

    # Apply the formats to the DataFrame
    # Iterate over each column in pitch_stats_dict
    for column, props in pitch_stats_dict.items():
        # Check if the column exists in df_plot
        if column in df_group.columns:
            # Apply the specified format to the column values
            df_group[column] = df_group[column].apply(lambda x: format(x, props['format']) if isinstance(x, (int, float)) else x)
    return df_group

# %%
import matplotlib
import matplotlib.colors as mcolors
import pandas as pd
import numpy as np

# Define color maps
cmap_sum = matplotlib.colors.LinearSegmentedColormap.from_list("", ['#648FFF','#FFFFFF','#FFB000'])
cmap_sum_r = matplotlib.colors.LinearSegmentedColormap.from_list("", ['#FFB000','#FFFFFF','#648FFF'])

# List of statistics to color
color_stats = ['release_speed', 'release_extension', 'delta_run_exp_per_100', 'whiff_rate', 'in_zone_rate', 'chase_rate', 'xwobacon']

### GET COLORS ###
def get_color(value, normalize, cmap_sum):
    color = cmap_sum(normalize(value))
    return mcolors.to_hex(color)

def get_cell_colouts(df_group: pd.DataFrame,
                     df_statcast_group: pd.DataFrame,
                     color_stats: list,
                     cmap_sum: matplotlib.colors.LinearSegmentedColormap,
                     cmap_sum_r: matplotlib.colors.LinearSegmentedColormap):
    color_list_df = []
    for pt in df_group.pitch_type.unique():
        color_list_df_inner = []
        select_df = df_statcast_group[df_statcast_group['pitch_type'] == pt]
        df_group_select = df_group[df_group['pitch_type'] == pt]

        for tb in table_columns:

            if tb in color_stats and type(df_group_select[tb].values[0]) == np.float64:
                if np.isnan(df_group_select[tb].values[0]):
                    color_list_df_inner.append('#ffffff')
                elif tb == 'release_speed':
                    normalize = mcolors.Normalize(vmin=(pd.to_numeric(select_df[tb], errors='coerce')).mean() * 0.95,
                                                  vmax=(pd.to_numeric(select_df[tb], errors='coerce')).mean() * 1.05)
                    color_list_df_inner.append(get_color((pd.to_numeric(df_group_select[tb], errors='coerce')).mean(), normalize, cmap_sum))
                elif tb == 'delta_run_exp_per_100':
                    normalize = mcolors.Normalize(vmin=-1.5, vmax=1.5)
                    color_list_df_inner.append(get_color((pd.to_numeric(df_group_select[tb], errors='coerce')).mean(), normalize, cmap_sum))
                elif tb == 'xwobacon':
                    normalize = mcolors.Normalize(vmin=(pd.to_numeric(select_df[tb], errors='coerce')).mean() * 0.7,
                                                  vmax=(pd.to_numeric(select_df[tb], errors='coerce')).mean() * 1.3)
                    color_list_df_inner.append(get_color((pd.to_numeric(df_group_select[tb], errors='coerce')).mean(), normalize, cmap_sum_r))
                else:
                    normalize = mcolors.Normalize(vmin=(pd.to_numeric(select_df[tb], errors='coerce')).mean() * 0.7,
                                                  vmax=(pd.to_numeric(select_df[tb], errors='coerce')).mean() * 1.3)
                    color_list_df_inner.append(get_color((pd.to_numeric(df_group_select[tb], errors='coerce')).mean(), normalize, cmap_sum))
            else:
                color_list_df_inner.append('#ffffff')
        color_list_df.append(color_list_df_inner)
    return color_list_df

# %%
def pitch_table(df: pd.DataFrame, ax: plt.Axes,fontsize:int=20):
    df_group, color_list = df_grouping(df)
    color_list_df = get_cell_colouts(df_group, df_statcast_group, color_stats, cmap_sum, cmap_sum_r)
    df_plot = plot_pitch_format(df_group)

    # Create a table plot with the DataFrame values and specified column labels
    table_plot = ax.table(cellText=df_plot.values, colLabels=table_columns, cellLoc='center',
                        bbox=[0, -0.1, 1, 1],
                        colWidths=[2.5, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
                        cellColours=color_list_df)

    # Disable automatic font size adjustment and set the font size
    table_plot.auto_set_font_size(False)

    table_plot.set_fontsize(fontsize)

    # Scale the table plot
    table_plot.scale(1, 0.5)

    # Correctly format the new column names using LaTeX formatting
    new_column_names = ['$\\bf{Pitch\\ Name}$'] + [pitch_stats_dict[x]['table_header'] if x in pitch_stats_dict else '---' for x in table_columns[1:]]

    # Update the table headers with the new column names
    for i, col_name in enumerate(new_column_names):
        table_plot.get_celld()[(0, i)].get_text().set_text(col_name)

    # Bold the first column in the table
    for i in range(len(df_plot)):
        table_plot.get_celld()[(i+1, 0)].get_text().set_fontweight('bold')

    # Set the color for the first column, all rows except header and last
    for i in range(1, len(df_plot)):
        # Check if the pitch type is in the specified list
        if table_plot.get_celld()[(i, 0)].get_text().get_text() in ['Split-Finger', 'Slider', 'Changeup']:
            table_plot.get_celld()[(i, 0)].set_text_props(color='#000000', fontweight='bold')
        else:
            table_plot.get_celld()[(i, 0)].set_text_props(color='#FFFFFF')
        # Set the background color of the cell
        table_plot.get_celld()[(i, 0)].set_facecolor(color_list[i-1])

    # Remove the axis
    ax.axis('off')

pitch_table(df = df, ax = plt.subplots(figsize=(25, 8))[1])

# %% [markdown]
# Generating the Pitching Summary

# %%
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec

def pitching_dashboard(pitcher_id: str, df: pd.DataFrame, stats: list):
    # Create a 22 by 20 figure
    df = df_processing(df)
    fig = plt.figure(figsize=(22, 20))

    # Create a gridspec layout with 8 columns and 6 rows
    # Include border plots for the header, footer, left, and right
    gs = gridspec.GridSpec(6, 8,
                       height_ratios=[2, 20, 9, 36, 36, 7],
                       width_ratios=[1, 22, 22, 18, 18, 28, 28, 1])

    # Define the positions of each subplot in the grid
    ax_headshot = fig.add_subplot(gs[1,1:3])
    ax_bio = fig.add_subplot(gs[1,3:5])
    ax_logo = fig.add_subplot(gs[1,5:7])

    ax_season_table = fig.add_subplot(gs[2,1:7])

    ax_plot_1 = fig.add_subplot(gs[3,1:3])
    ax_plot_2 = fig.add_subplot(gs[3,3:5])  # This is where the percentile ranking plot will go
    ax_plot_3 = fig.add_subplot(gs[3,5:7])

    ax_table = fig.add_subplot(gs[4,1:7])

    ax_footer = fig.add_subplot(gs[-1,1:7])
    ax_header = fig.add_subplot(gs[0,1:7])
    ax_left = fig.add_subplot(gs[:,0])
    ax_right = fig.add_subplot(gs[:,-1])

    # Hide axes for footer, header, left, and right
    ax_footer.axis('off')
    ax_header.axis('off')
    ax_left.axis('off')
    ax_right.axis('off')

    # Call the functions to populate the other subplots
    fontsize = 16
    fangraphs_pitcher_stats(pitcher_id, ax_season_table, stats, season=2025, fontsize=20)
    pitch_table(df, ax_table, fontsize=fontsize)

    player_headshot(pitcher_id, ax=ax_headshot)
    player_bio(pitcher_id, ax=ax_bio)
    plot_logo(pitcher_id, ax=ax_logo)

    velocity_kdes(df=df, ax=ax_plot_1, gs=gs, gs_x=[3,4], gs_y=[1,3], fig=fig, df_statcast_group=df_statcast_group)
    plot_percentile_rankings_by_pitcher(df_fangraphs, ax=ax_plot_2, pitcher_id=pitcher_id)
    break_plot(df=df, ax=ax_plot_3, df_statcast_group=df_pitch_movement)

    # Add footer text
    ax_footer.text(0, 1, 'By: Jake Vickroy', ha='left', va='top', fontsize=24)
    ax_footer.text(0, 0.5, 'Thanks to: @TJStats', ha='left', va='top', fontsize=16)
    ax_footer.text(0.5, 1, 'Color Coding Compares to League Average By Pitch', ha='center', va='top', fontsize=16)
    ax_footer.text(1, 1, 'Data: MLB, Fangraphs\nImages: MLB, ESPN, Fandom', ha='right', va='top', fontsize=24)

    # Adjust the spacing between subplots
    plt.tight_layout()

    return fig



# %%
df_chadwick = pyb.chadwick_register()

# %%
df_chadwick_2025 = df_chadwick[df_chadwick['mlb_played_last'] == 2025]
df_chadwick_2025 = df_chadwick_2025[df_chadwick_2025['key_mlbam'].notna() & (df_chadwick_2025['key_mlbam'] > 0)]
df_chadwick_2025['full_name'] = df_chadwick_2025['name_first'].fillna('') + ' ' + df_chadwick_2025['name_last'].fillna('')

# %%
def enrich_chadwick(df, batch_size=200):
    df = df.copy()
    df['team'] = 'Unknown'
    df['position'] = 'Unknown'
    df['team_level'] = 'Unknown'

    # Step 1: Batch-fetch person info (position and currentTeam ID)
    valid_ids = df['key_mlbam'].dropna().astype(int).tolist()
    n_batches = math.ceil(len(valid_ids) / batch_size)

    team_ids = set()
    person_team_map = {}

    for i in range(n_batches):
        batch_ids = valid_ids[i * batch_size:(i + 1) * batch_size]
        ids_str = ",".join(map(str, batch_ids))

        try:
            url = f"https://statsapi.mlb.com/api/v1/people?personIds={ids_str}&hydrate=currentTeam"
            response = requests.get(url, timeout=5)
            data = response.json()

            for person in data.get('people', []):
                pid = person['id']
                team = person.get('currentTeam', {})
                position = person.get('primaryPosition', {}).get('name', 'Unknown')

                team_name = team.get('name', 'Unknown')
                team_id = team.get('id', None)

                person_team_map[pid] = {
                    'team': team_name,
                    'team_id': team_id,
                    'position': position
                }

                if team_id:
                    team_ids.add(team_id)

        except Exception as e:
            print(f"Person batch {i+1} failed: {e}")

    # Step 2: Fetch team level info by unique team IDs
    team_level_map = {}

    for team_id in team_ids:
        try:
            url_team = f"https://statsapi.mlb.com/api/v1/teams/{team_id}"
            team_data = requests.get(url_team, timeout=3).json()

            if 'teams' in team_data and team_data['teams']:
                sport_name = team_data['teams'][0].get('sport', {}).get('name', 'Unknown')
                team_level_map[team_id] = sport_name
        except Exception as e:
            print(f"Team fetch failed for team_id {team_id}: {e}")
            team_level_map[team_id] = 'Unknown'

    # Step 3: Assign everything back to the DataFrame
    for idx, row in df.iterrows():
        pid = int(row['key_mlbam'])
        info = person_team_map.get(pid, {})
        team_id = info.get('team_id')

        df.at[idx, 'team'] = info.get('team', 'Unknown')
        df.at[idx, 'position'] = info.get('position', 'Unknown')
        df.at[idx, 'team_level'] = team_level_map.get(team_id, 'Unknown')

    return df


# %%
df_enriched = enrich_chadwick(df_chadwick_2025)

df_enriched['team_level'] = df_enriched['team_level'].replace({
    'Major League Baseball': 'MLB',
    'Triple-A': 'AAA',
    'Double-A': 'AA',
    'High-A': 'A+',
    'Single-A': 'A',
})

# Sort the DataFrame by last name
df_enriched= df_enriched.sort_values('name_last')

# Only keep players listed as pitchers
df_pitchers = df_enriched[df_enriched['position'].str.contains("Pitcher", na=False)]

# %%
import io
import base64
from dash import Dash, html, dcc, Output, Input

# Generate dropdown options using the cleaned `df_pitchers`
dropdown_pitcher_options = [
    {'label': row['full_name'], 'value': int(row['key_mlbam'])}
    for _, row in df_pitchers.iterrows()
]

# Generate team options based on the `team` column
dropdown_team_options = [
    {'label': team, 'value': team}
    for team in df_pitchers['team'].unique()
]

# Generate team level options based on the `team_level` column
dropdown_level_options = [
    {'label': level, 'value': level}
    for level in df_pitchers['team_level'].unique()
]

# Your dashboard figure generation function
def get_dashboard_image(pitcher_id, stats):
    # Assuming `pyb.statcast_pitcher` fetches the pitcher data for the selected pitcher
    df_pyb = pyb.statcast_pitcher('2025-03-15', '2025-10-01', pitcher_id)
    df_pyb = df_pyb[df_pyb['game_type'] == 'R']  # Filter for regular season games
    fig = pitching_dashboard(pitcher_id, df_pyb, stats)  # Should return a matplotlib figure
    buf = io.BytesIO()
    fig.savefig(buf, format="png", bbox_inches="tight")
    buf.seek(0)
    encoded_image = base64.b64encode(buf.read()).decode("utf-8")
    buf.close()
    return f"data:image/png;base64,{encoded_image}"

# Initialize Dash app
app = Dash(__name__)
stats = ['G', 'GS', 'IP', 'TBF', 'WHIP', 'ERA', 'FIP', 'K%', 'BB%', 'GB%']

# Layout with dropdowns and image
app.layout = html.Div([
    html.H1("2025 MLB Season Pitching Dashboard", style={'textAlign': 'center'}),

    html.Div([
        dcc.Dropdown(id='level-dropdown', placeholder='Select a level', style={'flex': 1}),
        dcc.Dropdown(id='team-dropdown', placeholder='Select a team', style={'flex': 1}),
        dcc.Dropdown(id='pitcher-dropdown', placeholder='Select a pitcher', style={'flex': 1}),
    ], style={
        'display': 'flex',
        'justifyContent': 'center',
        'alignItems': 'center',
        'gap': '2%',
        'maxWidth': '100%',
        'margin': '0 auto',
        'padding': '10px 0'
    }),

    html.Div([
        dcc.Loading(
            id="loading-spinner",
            type="circle",
            children=html.Img(id='dashboard-img', style={'width': '100%', 'maxWidth': '1600px'}),
            fullscreen=False
        )
    ], style={
        'textAlign': 'center',
        'margin': '0 auto'
    }),

    dcc.Interval(id='data-update-interval', interval=24 * 60 * 60 * 1000, n_intervals=0)

], style={
    'maxWidth': '1800px',
    'margin': '0 auto',
    'padding': '20px'
})

from dash.dependencies import Output, Input

# Unique level options
@app.callback(
    Output('level-dropdown', 'options'),
    Input('data-update-interval', 'n_intervals')
)
def populate_levels(_):
    levels = sorted(df_pitchers['team_level'].dropna().unique())
    return [{'label': lvl, 'value': lvl} for lvl in levels]

# Teams filtered by selected level
@app.callback(
    Output('team-dropdown', 'options'),
    Input('level-dropdown', 'value')
)
def update_teams(selected_level):
    if not selected_level:
        return []
    teams = df_pitchers[df_pitchers['team_level'] == selected_level]['team'].dropna().unique()
    return [{'label': team, 'value': team} for team in sorted(teams)]

# Pitchers filtered by selected team
@app.callback(
    Output('pitcher-dropdown', 'options'),
    Input('team-dropdown', 'value')
)
def update_pitchers(selected_team):
    if not selected_team:
        return []
    pitchers = df_pitchers[df_pitchers['team'] == selected_team]
    return [
        {'label': row['full_name'], 'value': int(row['key_mlbam'])}
        for _, row in pitchers.iterrows()
    ]

@app.callback(
    Output('dashboard-img', 'src'),
    Input('pitcher-dropdown', 'value')
)
def update_dashboard_image(pitcher_id):
    if pitcher_id is None:
        return None
    return get_dashboard_image(pitcher_id, stats)

# Run the app
if __name__ == '__main__':
    app.run(debug=True)



