import requests
from local_config import LAT, LONG # Lat and Long are in a local file that is gitignored

URL = "https://api.open-meteo.com/v1/forecast"

def get_weather():
    params = {
        "latitude": LAT,
        "longitude": LONG,
        "current": ["temperature_2m", "apparent_temperature", "weather_code"],
        "daily": ["temperature_2m_max", "temperature_2m_min", "weather_code"],
        "temperature_unit": "fahrenheit",
        "forecast_days": 4,
        "timezone": "America/New_York"
    }
    
    resp = requests.get(URL, params = params, timeout = 10)
    resp.raise_for_status()
    js = resp.json()
    
    current_raw = js.get("current", {})
    current = {
        "temp": round(current_raw.get("tamperature_2m", 0)),
        "feels_like": round(current_raw.get("apparent_temperature", 0)),
        "code": current_raw.get("weather_code", 0),
        "desc": WEATHER_CODES.get(current_raw.get("weather_code", 0), "Unknown")
    }
    
    
    print(current)
        
WEATHER_CODES = {
    0: "Clear Sky"
}