from datetime import timedelta
from pathlib import Path

import joblib
import pandas as pd


BASE_DIR = Path(__file__).resolve().parent.parent

DATASET_PATH = BASE_DIR / "ml" / "dataset.csv"
MODEL_PATH = BASE_DIR / "ml" / "model.joblib"


FEATURES = [
    "product_id",
    "day_of_year",
    "month",
    "day_of_week"
]


def load_model():

    if not MODEL_PATH.exists():

        raise FileNotFoundError(
            "ML model not found. "
            "Run python ml/ml/train_model.py first."
        )

    return joblib.load(MODEL_PATH)


def predict_demand(
    product_id: int,
    days: int = 7
):

    if days < 1 or days > 30:

        raise ValueError(
            "days must be between 1 and 30"
        )


    df = pd.read_csv(
        DATASET_PATH
    )


    df["date"] = pd.to_datetime(
        df["date"]
    )


    product_data = df[
        df["product_id"] == product_id
    ].sort_values("date")


    if product_data.empty:

        raise ValueError(
            f"No sales history for product {product_id}"
        )


    model = load_model()


    last_date = product_data["date"].max()


    future_dates = [
        last_date + timedelta(days=i)
        for i in range(1, days + 1)
    ]


    future = pd.DataFrame({

        "product_id": [
            product_id
        ] * days,

        "day_of_year": [
            d.dayofyear
            for d in future_dates
        ],

        "month": [
            d.month
            for d in future_dates
        ],

        "day_of_week": [
            d.dayofweek
            for d in future_dates
        ]
    })


    predictions = model.predict(
        future[FEATURES]
    )


    result = []


    for date, prediction in zip(
        future_dates,
        predictions
    ):

        result.append({

            "date": date.date().isoformat(),

            "predicted_units": round(
                max(0, float(prediction)),
                2
            )

        })


    return result