# Smart Traffic Navigation System 🚦🗺

An intelligent navigation system that predicts **traffic intensity using IoT sensor data and machine learning**, and dynamically computes the best route for users.

This project simulates a **Google Maps–like system** where users share traffic data in real-time using MQTT, and the system calculates optimal routes using a traffic-aware routing algorithm.

---

## 🚀 Features

- Real-time traffic updates from IoT devices
- Machine learning traffic prediction
- Dynamic routing based on traffic conditions
- Interactive map interface
- MQTT-based communication between devices
- OpenStreetMap road network
- FastAPI backend for route computation

---

## 🧠 System Architecture

The system follows an **IoT → ML → Routing → Web Interface pipeline**.

Traffic data is collected from IoT sensor boxes, processed using a machine learning model, and used to compute optimal navigation routes.

IoT Sensor Box  
(GPS + IMU + Distance Sensors)  
        │  
        │ MQTT publish  
        ▼  
MQTT Broker  
        │  
        ▼  
Traffic Server  
        │  
        ├── ML Model Prediction  
        ├── Traffic Database  
        └── Routing Engine  
                │  
                ▼  
              FastAPI  
                │  
                ▼  
        Web Map Interface  

---

## 🛠 Tech Stack

| Component | Technology |
|----------|------------|
| Backend API | FastAPI |
| Routing Engine | NetworkX |
| Map Data | OpenStreetMap |
| Map Visualization | Leaflet.js |
| Messaging Protocol | MQTT |
| ML Model | Scikit-Learn |
| Programming Language | Python |

---

## 📂 Project Structure

smart_navigation/

api/  
 └── main.py  

routing/  
 ├── map_loader.py  
 ├── router.py  
 └── traffic_manager.py  

mqtt/  
 └── subscriber.py  

ml/  
 ├── train_model.py  
 └── predictor.py  

traffic/  
 └── traffic_store.py  

simulation/  
 └── vehicle_simulator.py  

frontend/  
 └── map.html  

data/  
 └── iot_traffic_large.csv  

requirements.txt  
README.md  

---

## 📡 IoT Sensor Data

Sensor boxes publish data using MQTT.

Example message:

{
 "road": "12345-67890",
 "speed": 30,
 "Ax": 0.2,
 "Ay": 0.1,
 "Az": 0.05,
 "Gx": 0.01,
 "Gy": 0.02,
 "Gz": 0.03,
 "front_distance": 5,
 "back_distance": 7,
 "jerk": 0.04,
 "temperature": 31,
 "humidity": 65,
 "latitude": 13.08,
 "longitude": 80.27
}

This data is used by the ML model to predict traffic intensity.

---

## 🧠 Machine Learning Model

The system uses a **Random Forest classifier** trained on IoT sensor data to classify traffic into:

- Low Traffic
- Medium Traffic
- High Traffic
- Heavy Traffic

Predicted traffic intensity is used to update the routing graph.

---

## 🗺 Traffic-Aware Routing

Routes are computed using **Dijkstra's algorithm**.

Edge weight formula:

weight = distance * (1 + traffic_factor)

Where:

distance = road segment length  
traffic_factor = predicted congestion level  

This ensures routes avoid congested roads.

---

## ⚙️ Installation

### Clone the repository

    git clone https://github.com/yourusername/smart-traffic-navigation.git

    cd smart-traffic-navigation

---

### Install dependencies

    pip install -r requirements.txt

---

### Start MQTT broker

Install Mosquitto and run:

     mosquitto

---

### Start the traffic subscriber

    python -m mqtt.subscriber

---

### Start the API server

    uvicorn api.main:app --reload

---

### Open the map interface

Open:

    frontend/map.html

in your browser.

---

    python simulation/vehicle_simulator.py

This publishes traffic data through MQTT.

---
