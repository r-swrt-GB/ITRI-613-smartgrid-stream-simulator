# 🔌 SmartGrid Stream Simulator

A Python-based simulation tool designed to emulate real-time energy data streams from a household. This project is part of the **ITRI613 - Modern Stream Processing** module at North-West University.

It generates and streams three types of data into **Azure Event Hubs**:

- ☀️ **Solar Panel Output**
- 🌦️ **Weather Conditions** (via OpenWeatherMap API)
- 💡 **Household Electricity Usage** (per device, per room)

The goal is to build a complete streaming data pipeline that can later be processed with **Azure Stream Analytics**, stored in **Cosmos DB**, and visualized using **Power BI**.

---

## 📦 Features

- Realistic simulation of solar, weather, and power usage patterns.
- Streams data continuously at defined intervals.
- Modular design for easy integration and expansion.
- Secure config management via `.env` file.

---

## ⚙️ Setup Instructions

### 1. Clone the repository

```bash
git clone https://github.com/your-username/smartgrid-stream-simulator.git
cd smartgrid-stream-simulator
```

### 2. Create a virtual environment

```bash
python3 -m venv venv
```

### 3. Activate the environment

#### Windows

```bash
venv\Scripts\activate
```

#### mac/Linux

```bash
source venv/bin/activate
```

### 4. Install dependencies

```bash
pipx install -r requirements.txt
```

### 5. Create a .env file

```bash
API_KEY=""
SOLAR_EVENT_HUB_CONN_STR=""
WEATHER_EVENT_HUB_CONN_STR=""
USAGE_EVENT_HUB_CONN_STR=""

SOLAR_EVENT_HUB_NAME=""
WEATHER_EVENT_HUB_NAME=""
USAGE_EVENT_HUB_NAME=""

WEATHER_API_BASE_URL="https://api.openweathermap.org/data/2.5/weather"
```

### 6. Run the simulator

```bash
python3 simulated_data_streaming.py
```
