import requests
import pandas as pd
from datetime import datetime

# Replace this with your actual API key
API_KEY = "d6715e87ec4d257bfdb7bd2463cf9e62"

headers = {
    'x-apisports-key': API_KEY
}

# -------- Get Standings --------
standings_url = "https://v3.football.api-sports.io/standings"
standings_params = {
    'league': 39,
    'season': 2024
}

standings_response = requests.get(standings_url, headers=headers, params=standings_params)

if standings_response.status_code == 200:
    standings_data = standings_response.json()
    standings = standings_data['response'][0]['league']['standings'][0]

    standings_rows = []
    for team in standings:
        standings_rows.append({
            "Rank": team['rank'],
            "Team": team['team']['name'],
            "Points": team['points'],
            "Played": team['all']['played'],
            "Wins": team['all']['win'],
            "Draws": team['all']['draw'],
            "Losses": team['all']['lose'],
            "GF": team['all']['goals']['for'],
            "GA": team['all']['goals']['against'],
            "GD": team['goalsDiff']
        })

    df_standings = pd.DataFrame(standings_rows)
    df_standings.to_csv("premier_league_standings.csv", index=False)
    print("Standings saved to 'premier_league_standings.csv'")
else:
    print("Failed to fetch standings")
    print(standings_response.text)
