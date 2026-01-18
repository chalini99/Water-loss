import random
import pandas as pd
from datetime import datetime

def generate_live_data(df):
    df = df.copy()

    # Randomly change last row to simulate live reading
    idx = df.sample(1).index[0]

    df.loc[idx, "Water_Usage_Liters"] += random.randint(-50, 200)
    df.loc[idx, "Pressure"] += random.uniform(-0.3, 0.2)
    df.loc[idx, "Date"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    return df
