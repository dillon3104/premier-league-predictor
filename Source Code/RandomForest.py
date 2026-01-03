import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, r2_score
from sklearn.preprocessing import LabelEncoder
import joblib

# Load dataset
df = pd.read_csv("football_data_combined.csv")

# Clean percentage columns
def clean_percentage_column(series):
    return pd.to_numeric(series.str.rstrip('%'), errors='coerce')

df["possession_home"] = clean_percentage_column(df["possession_home"])
df["possession_away"] = clean_percentage_column(df["possession_away"])
df["pass_accuracy_home"] = clean_percentage_column(df["pass_accuracy_home"])
df["pass_accuracy_away"] = clean_percentage_column(df["pass_accuracy_away"])

# Drop rows with missing data
df.dropna(inplace=True)

# Encode categorical features
label_enc = LabelEncoder()
df["home_team_encoded"] = label_enc.fit_transform(df["home_team"])
df["away_team_encoded"] = label_enc.fit_transform(df["away_team"])

# Define features (X) and targets (y)
features = [
    "home_team_encoded", "away_team_encoded",
    "possession_home", "possession_away",
    "shots_home", "shots_away",
    "xG_home", "xG_away",
    "pass_accuracy_home", "pass_accuracy_away"
]

# Make sure all features exist
features = [f for f in features if f in df.columns]

X = df[features]
y = df[["home_score", "away_score"]]

# Split into train/test sets
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Train Random Forest
model = RandomForestRegressor(n_estimators=100, random_state=42)
model.fit(X_train, y_train)

# Predictions
y_pred = model.predict(X_test)

# Evaluation
print("R2 Score:", r2_score(y_test, y_pred))
print("RMSE:", mean_squared_error(y_test, y_pred, squared=False))

# ✅ Save model to file
joblib.dump(model, "random_forest_model.pkl")
print("Model saved as random_forest_model.pkl")
