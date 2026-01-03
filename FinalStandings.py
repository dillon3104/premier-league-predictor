import pandas as pd

# Load predicted fixtures and league table
predicted = pd.read_csv("predicted_fixtures.csv")
table = pd.read_csv("premier_league_standings.csv")

# Round predicted scores to nearest integer
predicted["predicted_home_goals"] = predicted["predicted_home_goals"].round().astype(int)
predicted["predicted_away_goals"] = predicted["predicted_away_goals"].round().astype(int)

# Ensure consistent casing (optional)
table["Team"] = table["Team"].str.strip()
predicted["home_team"] = predicted["home_team"].str.strip()
predicted["away_team"] = predicted["away_team"].str.strip()

# Loop through predictions and update standings
for _, match in predicted.iterrows():
    home = match["home_team"]
    away = match["away_team"]
    home_goals = match["predicted_home_goals"]
    away_goals = match["predicted_away_goals"]

    # Locate teams in table
    home_row = table[table["Team"] == home].index[0]
    away_row = table[table["Team"] == away].index[0]

    # Update games played
    table.at[home_row, "Played"] += 1
    table.at[away_row, "Played"] += 1

    # Update goals
    table.at[home_row, "GF"] += home_goals
    table.at[home_row, "GA"] += away_goals
    table.at[away_row, "GF"] += away_goals
    table.at[away_row, "GA"] += home_goals

    # Update win/draw/loss
    if home_goals > away_goals:
        table.at[home_row, "Wins"] += 1
        table.at[away_row, "Losses"] += 1
        table.at[home_row, "Points"] += 3
    elif home_goals < away_goals:
        table.at[away_row, "Wins"] += 1
        table.at[home_row, "Losses"] += 1
        table.at[away_row, "Points"] += 3
    else:
        table.at[home_row, "Draws"] += 1
        table.at[away_row, "Draws"] += 1
        table.at[home_row, "Points"] += 1
        table.at[away_row, "Points"] += 1

# Recalculate goal difference
table["GD"] = table["GF"] - table["GA"]

# Sort final table
final_table = table.sort_values(by=["Points", "GD", "GF"], ascending=False).reset_index(drop=True)

final_table.drop(columns="Rank", inplace=True)
final_table.insert(0, "Rank", range(1, len(final_table) + 1))

# Save and show
final_table.to_csv("final_league_table.csv", index=False)
print("✅ Final league table saved to 'final_league_table.csv'")
print(final_table.head(10))
