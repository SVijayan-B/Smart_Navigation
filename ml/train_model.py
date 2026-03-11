import pandas as pd
import numpy as np
import joblib

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestClassifier

df = pd.read_csv("../data/iot_traffic_large.csv")

traffic_map = {
"Low Traffic":0,
"Medium Traffic":1,
"High Traffic":2,
"Heavy Traffic":3
}

df["traffic_status"] = df["traffic_status"].map(traffic_map)

features = [
"speed(km/h)",
"Ax(m/s2)",
"Ay(m/s2)",
"Az(m/s2)",
"Gx(rad/s)",
"Gy(rad/s)",
"Gz(rad/s)",
"front_distance(m)",
"back_distance(m)",
"jerk",
"temperature(°C)",
"humidity(%)",
"latitude",
"longitude"
]

df = df[features + ["traffic_status"]]

df["acc_mag"] = np.sqrt(df["Ax(m/s2)"]**2 + df["Ay(m/s2)"]**2 + df["Az(m/s2)"]**2)
df["gyro_mag"] = np.sqrt(df["Gx(rad/s)"]**2 + df["Gy(rad/s)"]**2 + df["Gz(rad/s)"]**2)

X = df.drop("traffic_status",axis=1)
y = df["traffic_status"]

X_train,X_test,y_train,y_test = train_test_split(X,y,test_size=0.2)

scaler = StandardScaler()

X_train = scaler.fit_transform(X_train)

model = RandomForestClassifier(n_estimators=200)

model.fit(X_train,y_train)

joblib.dump(model,"traffic_model.pkl")
joblib.dump(scaler,"scaler.pkl")
joblib.dump(list(X.columns),"features.pkl")

print("Model trained")