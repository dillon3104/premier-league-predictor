import pandas as pd
import numpy as np
import joblib
from sklearn.preprocessing import LabelEncoder

# Load the trained model
model = joblib.load("random_forest_model.pkl")

# Load full dataset and team averages
df_all = pd.read_csv("football_data_combined.csv")
team_avg = pd.read_csv("team_averages.csv")

# Clean percentage fields
for col in team_avg.columns:
    if team_avg[col].dtype == object and team_avg[col].str.contains('%').any():
        team_avg[col] = team_avg[col].str.rstrip('%').astype(float)

# Rename averages to match model training names
team_avg.rename(columns={
    "avg_pass_acc_home": "pass_accuracy_home",
    "avg_pass_acc_away": "pass_accuracy_away",
}, inplace=True)

# Filter only unplayed matches
unplayed = df_all[df_all["home_score"].isna() | df_all["away_score"].isna()].copy()

# Fit the label encoder to all teams
all_teams = pd.concat([df_all["home_team"], df_all["away_team"]]).unique()
team_encoder = LabelEncoder()
team_encoder.fit(all_teams)

predictions = []

for _, row in unplayed.iterrows():
    home_team = row["home_team"]
    away_team = row["away_team"]

    home_stats = team_avg[team_avg["team"] == home_team]
    away_stats = team_avg[team_avg["team"] == away_team]

    if home_stats.empty or away_stats.empty:
        print(f"Skipping {home_team} vs {away_team} - missing stats")
        continue

    # Add team encodings
    home_encoded = team_encoder.transform([home_team])[0]
    away_encoded = team_encoder.transform([away_team])[0]

    # Create feature row
    feature_row = pd.DataFrame([{
        "home_team_encoded": home_encoded,
        "away_team_encoded": away_encoded,
        "possession_home": home_stats["avg_possession_home"].values[0],
        "possession_away": away_stats["avg_possession_away"].values[0],
        "shots_home": home_stats["avg_shots_home"].values[0],
        "shots_away": away_stats["avg_shots_away"].values[0],
        "xG_home": home_stats["avg_xG_home"].values[0],
        "xG_away": away_stats["avg_xG_away"].values[0],
        "pass_accuracy_home": home_stats["pass_accuracy_home"].values[0],
        "pass_accuracy_away": away_stats["pass_accuracy_away"].values[0]
    }])

    predicted_score = model.predict(feature_row)[0]

    predictions.append({
        "date": row["date"],
        "home_team": home_team,
        "away_team": away_team,
        "predicted_home_goals": round(predicted_score[0], 2),
        "predicted_away_goals": round(predicted_score[1], 2)
    })

# Save predictions
df_predictions = pd.DataFrame(predictions)
df_predictions.to_csv("predicted_fixtures.csv", index=False)

print("✅ Predictions complete. Here are the first few:")
print(df_predictions.head())

