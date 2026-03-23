from pathlib import Path

import joblib
import numpy as np
import pandas as pd


ML_DIR = Path(__file__).resolve().parent


def _load_with_fallback(*names: str):
    for name in names:
        path = ML_DIR / name
        if path.exists():
            return joblib.load(path)
    raise FileNotFoundError(f"Could not load any of: {names}")


MODEL = _load_with_fallback("traffic_optimized_model.pkl", "traffic_model.pkl")
SCALER = _load_with_fallback("traffic_scaler.pkl", "scaler.pkl")
FEATURES = _load_with_fallback("traffic_features.pkl", "feature_names.pkl", "features.pkl")


def _safe_float(payload: dict, key: str, default: float = 0.0) -> float:
    try:
        return float(payload.get(key, default))
    except (TypeError, ValueError):
        return default


def _build_feature_row(sensor_payload: dict) -> dict:
    speed = _safe_float(sensor_payload, "speed")
    ax = _safe_float(sensor_payload, "Ax", _safe_float(sensor_payload, "ax"))
    ay = _safe_float(sensor_payload, "Ay", _safe_float(sensor_payload, "ay"))
    az = _safe_float(sensor_payload, "Az", _safe_float(sensor_payload, "az"))
    distance_front = _safe_float(sensor_payload, "front_distance", _safe_float(sensor_payload, "distance_front"))
    distance_rear = _safe_float(sensor_payload, "back_distance", _safe_float(sensor_payload, "distance_rear"))
    gyro_x = _safe_float(sensor_payload, "Gx", _safe_float(sensor_payload, "gyro_x"))
    gyro_y = _safe_float(sensor_payload, "Gy", _safe_float(sensor_payload, "gyro_y"))
    gyro_z = _safe_float(sensor_payload, "Gz", _safe_float(sensor_payload, "gyro_z"))
    temperature = _safe_float(sensor_payload, "temperature")
    humidity = _safe_float(sensor_payload, "humidity")
    latitude = _safe_float(sensor_payload, "latitude")
    longitude = _safe_float(sensor_payload, "longitude")

    acc_magnitude = float(np.sqrt((ax * ax) + (ay * ay) + (az * az)))
    gyro_magnitude = float(np.sqrt((gyro_x * gyro_x) + (gyro_y * gyro_y) + (gyro_z * gyro_z)))
    avg_distance = max((distance_front + distance_rear) / 2.0, 0.1)
    speed_distance_ratio = speed / avg_distance

    return {
        "latitude": latitude,
        "longitude": longitude,
        "speed(km/h)": speed,
        "Ax(m/s2)": ax,
        "Ay(m/s2)": ay,
        "Az(m/s2)": az,
        "Gx(rad/s)": gyro_x,
        "Gy(rad/s)": gyro_y,
        "Gz(rad/s)": gyro_z,
        "temperature(°C)": temperature,
        "temperature(Â°C)": temperature,
        "humidity(%)": humidity,
        "front_distance(m)": distance_front,
        "back_distance(m)": distance_rear,
        "acc_magnitude": acc_magnitude,
        "gyro_magnitude": gyro_magnitude,
        "speed_distance_ratio": speed_distance_ratio,
    }


def predict_traffic(sensor_payload: dict) -> float:
    row = _build_feature_row(sensor_payload)
    feature_frame = pd.DataFrame([row])

    for feature in FEATURES:
        if feature not in feature_frame.columns:
            feature_frame[feature] = 0.0

    X = feature_frame[FEATURES]
    X_scaled = SCALER.transform(X)

    if hasattr(MODEL, "predict_proba"):
        score = float(MODEL.predict_proba(X_scaled)[0][1])
    else:
        score = float(MODEL.predict(X_scaled)[0])

    return max(0.0, min(1.0, score))
