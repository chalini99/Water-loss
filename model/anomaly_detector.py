import pandas as pd
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import MinMaxScaler

def detect_anomalies(df):
    df = df.copy()

    features = df[['Water_Usage_Liters', 'Pressure']]

    model = IsolationForest(contamination=0.2, random_state=42)
    df['anomaly'] = model.fit_predict(features)

    # Anomaly score (the lower, the more abnormal)
    df['anomaly_score'] = model.decision_function(features)

    # Normalize score to 0–100
    scaler = MinMaxScaler(feature_range=(0, 100))
    df['risk_score'] = scaler.fit_transform(
        (-df['anomaly_score']).values.reshape(-1, 1)
    )

    # Risk levels
    def risk_level(score):
        if score >= 70:
            return "High"
        elif score >= 40:
            return "Medium"
        else:
            return "Low"

    df['Risk_Level'] = df['risk_score'].apply(risk_level)

    return df
