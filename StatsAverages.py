import pandas as pd

def clean_percentage_column(series):
    return pd.to_numeric(series.str.rstrip('%'), errors='coerce')


def calculate_team_averages(file_path):
    # Load dataset
    df = pd.read_csv(file_path)

    # Ensure correct data types
    df["possession_home"] = clean_percentage_column(df["possession_home"])
    df["possession_away"] = clean_percentage_column(df["possession_away"])
    df["pass_accuracy_home"] = clean_percentage_column(df["pass_accuracy_home"])
    df["pass_accuracy_away"] = clean_percentage_column(df["pass_accuracy_away"])
    df["shots_home"] = pd.to_numeric(df["shots_home"], errors="coerce")
    df["shots_away"] = pd.to_numeric(df["shots_away"], errors="coerce")
    df["xG_home"] = pd.to_numeric(df["xG_home"], errors="coerce")
    df["xG_away"] = pd.to_numeric(df["xG_away"], errors="coerce")



    # Group by team to calculate averages
    home_averages = df.groupby("home_team").agg(
        avg_possession_home=("possession_home", "mean"),
        avg_shots_home=("shots_home", "mean"),
        avg_xG_home=("xG_home", "mean"),
        avg_pass_acc_home=("pass_accuracy_home", "mean"),
    ).reset_index()

    away_averages = df.groupby("away_team").agg(
        avg_possession_away=("possession_away", "mean"),
        avg_shots_away=("shots_away", "mean"),
        avg_xG_away=("xG_away", "mean"),
        avg_pass_acc_away=("pass_accuracy_away", "mean"),
    ).reset_index()

    # Merge home & away stats into one table
    team_averages = pd.merge(
        home_averages, away_averages, left_on="home_team", right_on="away_team", how="outer"
    ).rename(columns={"home_team": "team"}).drop(columns=["away_team"])

    # Save results to a new CSV file
    output_file = "team_averages.csv"
    team_averages.to_csv(output_file, index=False)
    print(f" Data saved to {output_file}")

    return team_averages

# Run the function
file_path = "football_data_combined.csv"
df_averages = calculate_team_averages(file_path)

# Preview the results
print(df_averages.head())
