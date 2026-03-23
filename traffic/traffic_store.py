import os
from collections import defaultdict, deque
from datetime import datetime, timezone
from pathlib import Path
from threading import Lock
from typing import Dict, List, Optional

try:
    import psycopg2
except ImportError:
    psycopg2 = None

try:
    from dotenv import load_dotenv
except ImportError:
    load_dotenv = None


MAX_HISTORY = 20
DEFAULT_SCORE = 0.5
EMA_LAMBDA = 0.3

_lock = Lock()
_route_scores = defaultdict(lambda: deque(maxlen=MAX_HISTORY))
_route_ema: Dict[str, float] = {}
_vehicle_positions: Dict[str, dict] = {}

# Backward compatibility for existing imports
traffic_db = _route_scores

_db_conn = None


def _init_env() -> None:
    if load_dotenv is not None:
        env_path = Path(__file__).resolve().parents[1] / ".env"
        load_dotenv(dotenv_path=env_path)


def _init_db():
    global _db_conn
    if _db_conn is not None or psycopg2 is None:
        return _db_conn

    _init_env()
    db_host = os.getenv("DB_HOST", "localhost")
    db_port = int(os.getenv("DB_PORT", "5432"))
    db_name = os.getenv("DB_NAME", "traffic_db")
    db_user = os.getenv("DB_USER", "postgres")
    db_password = os.getenv("DB_PASSWORD", "postgres")

    try:
        _db_conn = psycopg2.connect(
            host=db_host,
            port=db_port,
            dbname=db_name,
            user=db_user,
            password=db_password,
        )
        _db_conn.autocommit = True
        with _db_conn.cursor() as cur:
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS traffic_data (
                    id SERIAL PRIMARY KEY,
                    route_id TEXT NOT NULL,
                    traffic_score FLOAT NOT NULL,
                    timestamp TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
                )
                """
            )
    except Exception:
        _db_conn = None
    return _db_conn


def _persist_traffic(route_id: str, traffic_score: float, ts: Optional[datetime] = None) -> None:
    conn = _init_db()
    if conn is None:
        return
    timestamp = ts or datetime.now(timezone.utc)
    try:
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO traffic_data (route_id, traffic_score, timestamp) VALUES (%s, %s, %s)",
                (route_id, float(traffic_score), timestamp),
            )
    except Exception:
        pass


def update_route(route_id: str, score: float, ts: Optional[datetime] = None) -> float:
    bounded_score = max(0.0, min(1.0, float(score)))
    with _lock:
        old = _route_ema.get(route_id, DEFAULT_SCORE)
        smoothed = (EMA_LAMBDA * bounded_score) + ((1.0 - EMA_LAMBDA) * old)
        _route_ema[route_id] = smoothed
        _route_scores[route_id].append(smoothed)
    _persist_traffic(route_id, smoothed, ts=ts)
    return smoothed


def update_traffic(route_id: str, value: float) -> None:
    update_route(route_id, value)


def get_route_average(route_id: str) -> float:
    with _lock:
        history = list(_route_scores.get(route_id, []))
    if not history:
        return DEFAULT_SCORE
    return sum(history) / len(history)


def get_traffic(route_id: str) -> float:
    return get_route_average(route_id)


def get_all_route_averages() -> Dict[str, float]:
    with _lock:
        return {
            route_id: (sum(values) / len(values)) if values else DEFAULT_SCORE
            for route_id, values in _route_scores.items()
        }


def get_route_history(route_id: str) -> List[float]:
    with _lock:
        return list(_route_scores.get(route_id, []))


def update_vehicle_position(vehicle_payload: dict) -> None:
    vehicle_id = str(vehicle_payload.get("vehicle_id", "")).strip()
    if not vehicle_id:
        return
    record = {
        "vehicle_id": vehicle_id,
        "route_id": str(vehicle_payload.get("route_id", "")),
        "latitude": float(vehicle_payload.get("latitude", 0.0)),
        "longitude": float(vehicle_payload.get("longitude", 0.0)),
        "speed": float(vehicle_payload.get("speed", 0.0)),
        "timestamp": vehicle_payload.get("ts"),
    }
    with _lock:
        _vehicle_positions[vehicle_id] = record


def get_live_vehicles() -> List[dict]:
    with _lock:
        return list(_vehicle_positions.values())
