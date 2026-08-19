import pandas as pd
from pathlib import Path

from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error

import joblib


BASE_DIR = Path(__file__).resolve().parent
DATASET_PATH = BASE_DIR.parent / "dataset.csv"
MODEL_PATH = BASE_DIR.parent / "model.joblib"


# Load dataset
df = pd.read_csv(DATASET_PATH)


# Convert date
df["date"] = pd.to_datetime(df["date"])


# Create useful features
df["day_of_year"] = df["date"].dt.dayofyear
df["month"] = df["date"].dt.month
df["day_of_week"] = df["date"].dt.dayofweek


# Features
X = df[
    [
        "product_id",
        "day_of_year",
        "month",
        "day_of_week"
    ]
]


# Target
y = df["units_sold"]


# Split dataset
X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.2,
    random_state=42
)


# Create model
model = RandomForestRegressor(
    n_estimators=200,
    random_state=42
)


# Train
model.fit(X_train, y_train)


# Test
predictions = model.predict(X_test)

mae = mean_absolute_error(
    y_test,
    predictions
)


# Save model
joblib.dump(
    model,
    MODEL_PATH
)


print("================================")
print("MODEL TRAINING COMPLETED")
print("================================")

print("Rows:", len(df))
print("Mean Absolute Error:", round(mae, 2))

print("Model saved at:")
print(MODEL_PATH)


# Predict next 7 days

last_date = df["date"].max()

future_dates = pd.date_range(
    start=last_date + pd.Timedelta(days=1),
    periods=7
)


future = pd.DataFrame({
    "product_id": [1] * 7,
    "day_of_year": future_dates.dayofyear,
    "month": future_dates.month,
    "day_of_week": future_dates.dayofweek
})


future_predictions = model.predict(
    future[X.columns]
)


print("\nNext 7 Days Prediction")

for date, prediction in zip(
    future_dates,
    future_predictions
):
    print(
        date.date(),
        "->",
        round(max(0, prediction), 2),
        "units"
    )