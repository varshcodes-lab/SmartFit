import pandas as pd
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_PATH = os.path.join(BASE_DIR, "data", "gyms.csv")

def recommend_gyms(city, workout_type):
    df = pd.read_csv(DATA_PATH)
    filtered = df[
        (df["city"] == city) &
        (df["type"] == workout_type)
    ]
    return filtered.sort_values(
        by="rating", ascending=False
    ).head(3).to_dict(orient="records")
