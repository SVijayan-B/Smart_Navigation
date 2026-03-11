import joblib
import numpy as np

model = joblib.load("traffic_model.pkl")
scaler = joblib.load("scaler.pkl")

def predict(features):

    arr = np.array(features).reshape(1,-1)

    arr = scaler.transform(arr)

    pred = model.predict(arr)[0]

    return int(pred)