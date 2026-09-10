import requests
import pandas as pd
from understat import Understat
import aiohttp
import asyncio
import json
import os

API_FOOTBALL_KEY = os.environ["API_FOOTBALL_KEY"]
API_FOOTBALL_URL = "https://v3.football.api-sports.io/fixtures"

def fetch_api_football():
    headers = {"x-apisports-key": API_FOOTBALL_KEY}
    params = {"league": 39, "season": 2024}  # 39 = Premier League

    response = requests.get(API_FOOTBALL_URL, headers=headers, params=params)
    data = response.json()

    matches = []
    for fixture in data["response"]:
        match = fixture["fixture"]
        teams = fixture["teams"]
        
        # Fetch fixture statistics separately
        fixture_id = match["id"]
        stats_url = f"https://v3.football.api-sports.io/fixtures/statistics?fixture={fixture_id}"
        stats_response = requests.get(stats_url, headers=headers).json()

        # Initialize variables for possession, shots, and passing accuracy
        possession_home, possession_away = None, None
        shots_home, shots_away = None, None
        shots_on_target_home, shots_on_target_away = None, None
        shots_off_target_home, shots_off_target_away = None, None
        pass_accuracy_home, pass_accuracy_away = None, None

        # Extract statistics if available
        if "response" in stats_response and len(stats_response["response"]) > 1:
            for team_stats in stats_response["response"]:
                team_name = team_stats["team"]["name"]
                statistics = team_stats["statistics"]

                for stat in statistics:
                    # Extract Ball Possession
                    if stat["type"] == "Ball Possession":
                        if team_name == teams["home"]["name"]:
                            possession_home = stat["value"]
                        elif team_name == teams["away"]["name"]:
                            possession_away = stat["value"]

                    # Extract Total Shots
                    elif stat["type"] == "Total Shots":
                        if team_name == teams["home"]["name"]:
                            shots_home = stat["value"]
                        elif team_name == teams["away"]["name"]:
                            shots_away = stat["value"]

                    # Extract Shots on Target
                    elif stat["type"] == "Shots on Goal":
                        if team_name == teams["home"]["name"]:
                            shots_on_target_home = stat["value"]
                        elif team_name == teams["away"]["name"]:
                            shots_on_target_away = stat["value"]

                    # Extract Shots off Target
                    elif stat["type"] == "Shots off Goal":
                        if team_name == teams["home"]["name"]:
                            shots_off_target_home = stat["value"]
                        elif team_name == teams["away"]["name"]:
                            shots_off_target_away = stat["value"]

                    # Extract Pass Accuracy
                    elif stat["type"] == "Passes %":
                        if team_name == teams["home"]["name"]:
                            pass_accuracy_home = stat["value"]
                        elif team_name == teams["away"]["name"]:
                            pass_accuracy_away = stat["value"]

        matches.append({
            "date": match["date"].split("T")[0],  # Convert to YYYY-MM-DD
            "home_team": teams["home"]["name"],
            "away_team": teams["away"]["name"],
            "home_score": fixture["goals"]["home"],
            "away_score": fixture["goals"]["away"],
            "possession_home": possession_home,
            "possession_away": possession_away,
            "shots_home": shots_home,
            "shots_away": shots_away,
            "shots_on_target_home": shots_on_target_home,
            "shots_on_target_away": shots_on_target_away,
            "shots_off_target_home": shots_off_target_home,
            "shots_off_target_away": shots_off_target_away,
            "pass_accuracy_home": pass_accuracy_home,  # ✅ New field
            "pass_accuracy_away": pass_accuracy_away   # ✅ New field
        })

    return pd.DataFrame(matches)

async def fetch_understat():
    """Fetch Expected Goals (xG) and match statistics using the Understat API."""
    async with aiohttp.ClientSession() as session:
        understat = Understat(session)

        # Fetch Premier League teams for the 2023 season
        teams = await understat.get_teams("epl", 2024)

        # Create a mapping of team IDs to team names
        team_id_to_name = {team["id"]: team["title"] for team in teams}

        matches = []
        for team in teams:
            team_id = team["id"]
            team_name = team["title"]

            # Fetch match history for each team
            team_matches = await understat.get_team_results(team_name, 2024)

            for match in team_matches:
                home_team_id = match["h"]["id"]
                away_team_id = match["a"]["id"]

                # Extract xG and xGA
                if str(home_team_id) == str(team_id):  # Home team
                    xG = float(match["xG"]["h"])
                    xGA = float(match["xG"]["a"])
                    home_team = team_name
                    away_team = team_id_to_name.get(away_team_id, "Unknown")
                else:  # Away team
                    xG = float(match["xG"]["a"])
                    xGA = float(match["xG"]["h"])
                    away_team = team_name
                    home_team = team_id_to_name.get(home_team_id, "Unknown")

                matches.append({
                    "date": match["datetime"].split(" ")[0],  # ✅ Extract YYYY-MM-DD only
                    "home_team": home_team,
                    "away_team": away_team,
                    "xG_home": xG if home_team == team_name else xGA,
                    "xG_away": xGA if home_team == team_name else xG,
                })

        return pd.DataFrame(matches)




# Run the function asynchronously
df_understat = asyncio.run(fetch_understat())

# Print first few rows to verify
print(df_understat.head())

# Fetch data and check first rows
df_api_football = fetch_api_football()

def test_api_football():
    headers = {"x-apisports-key": API_FOOTBALL_KEY}
    params = {"league": 39, "season": 2024}  # 39 = Premier League

    response = requests.get(API_FOOTBALL_URL, headers=headers, params=params)
    data = response.json()

    # Print the entire API response to check for issues
    print(json.dumps(data, indent=4))

test_api_football()

df_merged = pd.merge(df_api_football, df_understat, 
                     on=["date", "home_team", "away_team"], 
                     how="left")


# Save to CSV
df_merged.to_csv("football_data_combined.csv", index=False)
print(" Data successfully saved as football_data_combined.csv")



