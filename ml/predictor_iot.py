import joblib
import numpy as np

model = joblib.load("ml/traffic_model.pkl")
scaler = joblib.load("ml/scaler.pkl")


def predict_traffic(sensor_data):

    features = [
        sensor_data["speed"],
        sensor_data["Ax"],
        sensor_data["Ay"],
        sensor_data["Az"],
        sensor_data["Gx"],
        sensor_data["Gy"],
        sensor_data["Gz"],
        sensor_data["front_distance"],
        sensor_data["back_distance"],
        sensor_data["jerk"],
        sensor_data["temperature"],
        sensor_data["humidity"],
        sensor_data["latitude"],
        sensor_data["longitude"]
    ]

    features = np.array(features).reshape(1, -1)

    features = scaler.transform(features)

    pred = model.predict(features)[0]

    return float(pred)