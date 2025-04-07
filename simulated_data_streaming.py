import random
import requests
import time
import json
from datetime import datetime
from azure.eventhub import EventHubProducerClient, EventData
from dotenv import load_dotenv
import os

# --- CONFIGURATION --- 
load_dotenv()

API_KEY = os.getenv("API_KEY")
WEATHER_API_BASE_URL = os.getenv("WEATHER_API_BASE_URL")

LOCATION = "Potchefstroom,ZA" 
INTERVAL_SECONDS = 60  
HOUSE_ID = "house_01"
PANEL_COUNT = 16
PANEL_WATT_RATING = 400 
PANEL_KW_RATING = PANEL_WATT_RATING / 1000.0

SOLAR_EVENT_HUB_CONN_STR = os.getenv("SOLAR_EVENT_HUB_CONN_STR")
WEATHER_EVENT_HUB_CONN_STR = os.getenv("WEATHER_EVENT_HUB_CONN_STR")
USAGE_EVENT_HUB_CONN_STR = os.getenv("USAGE_EVENT_HUB_CONN_STR")

SOLAR_EVENT_HUB_NAME = os.getenv("SOLAR_EVENT_HUB_NAME")
WEATHER_EVENT_HUB_NAME = os.getenv("WEATHER_EVENT_HUB_NAME")
USAGE_EVENT_HUB_NAME =os.getenv("USAGE_EVENT_HUB_NAME")

solar_producer = EventHubProducerClient.from_connection_string(conn_str=SOLAR_EVENT_HUB_CONN_STR, eventhub_name=SOLAR_EVENT_HUB_NAME)
weather_producer = EventHubProducerClient.from_connection_string(conn_str=WEATHER_EVENT_HUB_CONN_STR, eventhub_name=WEATHER_EVENT_HUB_NAME)
usage_producer = EventHubProducerClient.from_connection_string(conn_str=USAGE_EVENT_HUB_CONN_STR, eventhub_name=USAGE_EVENT_HUB_NAME)

def send_to_solar_event_hub(payload):
    event_data_batch = solar_producer.create_batch()
    event_data_batch.add(EventData(json.dumps(payload)))
    solar_producer.send_batch(event_data_batch)

def send_to_weather_event_hub(payload):
    event_data_batch = weather_producer.create_batch()
    event_data_batch.add(EventData(json.dumps(payload)))
    weather_producer.send_batch(event_data_batch)

def send_to_usage_event_hub(payload):
    event_data_batch = usage_producer.create_batch()
    event_data_batch.add(EventData(json.dumps(payload)))
    usage_producer.send_batch(event_data_batch)

def get_time():
    now = datetime.now()
    return now.hour, now.minute

def is_between(start_hour, end_hour):
    hour, _ = get_time()
    return start_hour <= hour < end_hour

def simulate_constant(min_kw, max_kw):
    return round((min_kw + max_kw) / 2, 3)

rooms = {
    "bedroom_1": {
        "light": {"range": (0.05, 0.1), "pattern": "Evenings & early morning", "usage": lambda: is_between(19, 23) or is_between(5, 7)},
        "phone_charger": {"range": (0.005, 0.015), "pattern": "Night 22:00–00:00", "usage": lambda: is_between(22, 0)},
        "laptop": {"range": (0.05, 0.1), "pattern": "Evenings", "usage": lambda: is_between(20, 23)},
        "heater": {"range": (0.5, 1.5), "pattern": "Early morning & evenings", "usage": lambda: is_between(5, 7) or is_between(20, 23)},
        "electric_blanket": {"range": (0.06, 0.15), "pattern": "Nighttime", "usage": lambda: is_between(21, 23)}
    },
    "bedroom_2": {
        "light": {"range": (0.05, 0.1), "pattern": "Evenings & early morning", "usage": lambda: is_between(19, 23) or is_between(5, 7)},
        "phone_charger": {"range": (0.005, 0.015), "pattern": "Night 22:00–00:00", "usage": lambda: is_between(22, 0)},
        "laptop": {"range": (0.05, 0.1), "pattern": "Evenings", "usage": lambda: is_between(20, 23)},
        "fan": {"range": (0.3, 0.6), "pattern": "Afternoon", "usage": lambda: is_between(14, 17)},
        "electric_blanket": {"range": (0.06, 0.15), "pattern": "Nighttime", "usage": lambda: is_between(21, 23)}
    },
    "kitchen": {
        "fridge": {"range": (0.08, 0.12), "pattern": "Always on", "usage": lambda: True},
        "microwave": {"range": (1.0, 1.5), "pattern": "Morning & evening meals", "usage": lambda: is_between(7, 8) or is_between(18, 19)},
        "kettle": {"range": (2.0, 2.5), "pattern": "Morning & evening", "usage": lambda: is_between(6, 8) or is_between(19, 20)},
        "toaster": {"range": (0.8, 1.2), "pattern": "Breakfast hours", "usage": lambda: is_between(6, 8)},
        "oven": {"range": (2.0, 3.5), "pattern": "Evening dinner time", "usage": lambda: is_between(17, 19)},
        "stove_plate": {"range": (1.0, 2.0), "pattern": "Lunch & dinner", "usage": lambda: is_between(12, 13) or is_between(17, 18)},
        "light": {"range": (0.05, 0.1), "pattern": "Early morning & night", "usage": lambda: is_between(5, 7) or is_between(18, 22)}
    },
    "tv_room": {
        "tv": {"range": (0.05, 0.2), "pattern": "Evenings", "usage": lambda: is_between(18, 22)},
        "decoder": {"range": (0.01, 0.02), "pattern": "Afternoon & night", "usage": lambda: is_between(17, 23)},
        "sound_system": {"range": (0.05, 0.1), "pattern": "Evenings", "usage": lambda: is_between(18, 22)},
        "light": {"range": (0.05, 0.1), "pattern": "Evenings", "usage": lambda: is_between(18, 23)},
        "gaming_console": {"range": (0.07, 0.2), "pattern": "Afternoons", "usage": lambda: is_between(15, 18)},
        "heater": {"range": (1.0, 2.0), "pattern": "Morning & night", "usage": lambda: is_between(5, 7) or is_between(19, 22)}
    },
    "bathroom": {
        "geyser": {"range": (2.0, 3.0), "pattern": "6–8AM & 6–9PM", "usage": lambda: is_between(6, 8) or is_between(18, 21)},
        "hair_dryer": {"range": (1.2, 2.0), "pattern": "Morning 6:30–7AM", "usage": lambda: is_between(6, 7)},
        "toothbrush": {"range": (0.005, 0.01), "pattern": "6–7AM & 8–10PM", "usage": lambda: is_between(6, 7) or is_between(20, 22)},
        "light": {"range": (0.05, 0.1), "pattern": "Morning & night", "usage": lambda: is_between(5, 7) or is_between(19, 22)},
        "towel_rail": {"range": (0.3, 0.5), "pattern": "6–9AM", "usage": lambda: is_between(6, 9)}
    },
    "washing_area": {
        "washing_machine": {"range": (0.5, 1.2), "pattern": "9AM–5PM (random)", "usage": lambda: is_between(9, 17) and random.random() < 0.3},
        "tumble_dryer": {"range": (2.0, 3.0), "pattern": "10AM–6PM (random)", "usage": lambda: is_between(10, 18) and random.random() < 0.2},
        "iron": {"range": (1.0, 2.5), "pattern": "2–4PM (random)", "usage": lambda: is_between(14, 16) and random.random() < 0.2},
        "light": {"range": (0.05, 0.1), "pattern": "Morning & early evening", "usage": lambda: is_between(6, 8) or is_between(17, 19)}
    },
    "shared": {
        "air_conditioner": {"range": (1.5, 3.5), "pattern": "Midday 12–4PM", "usage": lambda: is_between(12, 16)},
        "wifi_router": {"range": (0.01, 0.02), "pattern": "Always on", "usage": lambda: True},
        "inverter_charger": {"range": (0.5, 1.5), "pattern": "10AM–1PM & 9–11PM", "usage": lambda: is_between(10, 13) or is_between(21, 23)}
    }
}

# --- FUNCTION TO FETCH DATA ---
def get_weather_data():
    
    params = {
        "q": LOCATION,
        "appid": API_KEY,
        "units": "metric" 
    }

    response = requests.get(WEATHER_API_BASE_URL, params=params)
    if response.status_code == 200:
        weather = response.json()

        cloud_cover = weather["clouds"]["all"]
        rain_mm = weather.get("rain", {}).get("1h", 0)

        sunlight_intensity = max(0, 100 - cloud_cover)

        if rain_mm > 0:
            sunlight_intensity *= 0.8 

        scaled_intensity = int(sunlight_intensity * 10)


        data = {
            "timestamp": datetime.now().isoformat() + "Z",
            "house_id": HOUSE_ID,
            "location": LOCATION,
            "temperature_c": weather["main"]["temp"],
            "humidity_pct": weather["main"]["humidity"],
            "cloud_cover_pct": weather["clouds"]["all"],
            "wind_speed_mps": weather["wind"]["speed"],
            "sunlight_intensity": scaled_intensity
        }

        print(json.dumps(data))
        send_to_weather_event_hub(data)

        return data
    else:
        print(f"❌ Error fetching weather data: {response.status_code} {response.text}")
        return None
    
def get_panel_data(scaled_intensity):
    panels = [f"panel_{str(i+1).zfill(2)}" for i in range(PANEL_COUNT)]
    timestamp = datetime.now().isoformat() + "Z"
    

    sunlight_intensity = scaled_intensity
    efficiency = sunlight_intensity / 1000.0

    for panel_id in panels:

        variation = random.uniform(0.95, 1.05)
        actual_efficiency = min(1.0, efficiency * variation)

        power_output_kw = round(PANEL_KW_RATING * actual_efficiency, 3)

        panel_data = {
            "timestamp": timestamp,
            "house_id": HOUSE_ID,
            "panel_id": panel_id,
            "rated_output_kw": PANEL_KW_RATING,
            "sunlight_intensity": sunlight_intensity,
            "efficiency": round(actual_efficiency, 2),
            "power_output_kw": power_output_kw
        }

        print(json.dumps(panel_data))
        send_to_solar_event_hub(panel_data)

def get_usage_data():
    timestamp = datetime.now().isoformat() + "Z"
    
    for room, devices in rooms.items():
        for device, props in devices.items():
            usage_check = props["usage"]
            min_kw, max_kw = props["range"]
            
            if usage_check():
                if device in ["wifi_router", "fridge", "phone_charger", "hair_dryer", "toothbrush"]:
                    power_usage_kw = simulate_constant(min_kw, max_kw)
                else:
                    power_usage_kw = round(random.uniform(min_kw, max_kw), 3)
                
                data = {
                    "timestamp": timestamp,
                    "house_id": HOUSE_ID,
                    "room": room,
                    "device": device,
                    "power_usage_kw": power_usage_kw
                }

                print(json.dumps(data))
                send_to_usage_event_hub(data)


# --- SIMULATION LOOP ---
print("🌤️ Starting weather, solar and usage data stream...\n")

while True:
    weather_data = get_weather_data()
    
    if weather_data:
        scaled_intensity = weather_data["sunlight_intensity"]

        get_panel_data(scaled_intensity)
        get_usage_data()

    time.sleep(INTERVAL_SECONDS)

