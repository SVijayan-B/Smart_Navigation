import pandas as pd
import numpy as np
import joblib

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import GradientBoostingRegressor

DATA_PATH = "../data/iot_traffic_large.csv"

df = pd.read_csv(DATA_PATH)

df.columns = df.columns.str.replace("Â", "")

df["traffic_status"] = pd.to_numeric(df["traffic_status"])

max_label = df["traffic_status"].max()

df["traffic_score"] = 1 - (df["traffic_status"] / max_label)

df["acc_magnitude"] = np.sqrt(
    df["Ax(m/s2)"]**2 +
    df["Ay(m/s2)"]**2 +
    df["Az(m/s2)"]**2
)

df["gyro_magnitude"] = np.sqrt(
    df["Gx(rad/s)"]**2 +
    df["Gy(rad/s)"]**2 +
    df["Gz(rad/s)"]**2
)

df["speed_distance_ratio"] = df["speed(km/h)"] / (df["front_distance(m)"] + 1)

features = [
    "latitude","longitude","speed(km/h)",
    "Ax(m/s2)","Ay(m/s2)","Az(m/s2)",
    "Gx(rad/s)","Gy(rad/s)","Gz(rad/s)",
    "temperature(°C)","humidity(%)",
    "front_distance(m)","back_distance(m)",
    "acc_magnitude","gyro_magnitude",
    "speed_distance_ratio"
]

X = df[features]
y = df["traffic_score"]

X_train,X_test,y_train,y_test = train_test_split(X,y,test_size=0.2)

scaler = StandardScaler()

X_train = scaler.fit_transform(X_train)

model = GradientBoostingRegressor(
    n_estimators=600,
    learning_rate=0.02,
    max_depth=6
)

model.fit(X_train,y_train)

joblib.dump(model,"traffic_model.pkl")
joblib.dump(scaler,"scaler.pkl")
joblib.dump(features,"features.pkl")

print("Model saved")