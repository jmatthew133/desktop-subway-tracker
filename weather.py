import requests
from datetime import datetime
from local_config import LAT, LONG # Lat and Long are in a local file that is gitignored

URL = "https://api.open-meteo.com/v1/forecast"

def print_weather(forecast):
    output_list = []
    day_string = "Today: "
    weather_string = f"{forecast['current']['desc']} — {forecast['current']['high']}° / {forecast['current']['low']}° (feels {forecast['current']['feels_like']}°)"
    print(day_string + weather_string)
    output_list.append(day_string)
    output_list.append(weather_string)
    output_list.append("")
    for d in forecast['forecast']:
        day_string = f"{d['day']}: "
        weather_string = f"{d['desc']} — {d['high']}° / {d['low']}°"
        print(day_string + weather_string)
        output_list.append(day_string)
        output_list.append(weather_string)
        output_list.append("")
    return output_list

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

    # Parse daily data
    daily = js.get("daily", {})
    
    # Parse current day's weather (with today's high/low)
    current_raw = js.get("current", {})
    today_high = round(daily.get("temperature_2m_max", [])[0]) if daily.get("temperature_2m_max", []) else 0
    today_low = round(daily.get("temperature_2m_min", [])[0]) if daily.get("temperature_2m_min", []) else 0
    
    current = {
        "temp": round(current_raw.get("temperature_2m", 0)),
        "feels_like": round(current_raw.get("apparent_temperature", 0)),
        "code": current_raw.get("weather_code", 0),
        "desc": WEATHER_CODES.get(current_raw.get("weather_code", 0), "Unknown"),
        "high": today_high,
        "low": today_low,
    }
    
    # Parse 3-day forecast (excluding today)
    days = daily.get("time", [])[1:4]
    highs = daily.get("temperature_2m_max", [])[1:4]
    lows = daily.get("temperature_2m_min", [])[1:4]
    codes = daily.get("weather_code", [])[1:4]

    forecast = []
    for day, high, low, code in zip(days, highs, lows, codes):
        dt = datetime.fromisoformat(day)
        forecast.append({
            "day": dt.strftime("%a"),
            "high": round(high),
            "low": round(low),
            "code": code,
            "desc": WEATHER_CODES.get(code, "Unknown"),
        })

    return {"current": current, "forecast": forecast}


# Weather code map (Open-Meteo standard / WMO codes)
WEATHER_CODES = {
    0: "Clear sky",
    1: "Mainly clear",
    2: "Partly cloudy",
    3: "Overcast",
    45: "Fog",
    48: "Rime fog",
    51: "Light drizzle",
    53: "Moderate drizzle",
    55: "Dense drizzle",
    61: "Slight rain",
    63: "Moderate rain",
    65: "Heavy rain",
    71: "Slight snow",
    73: "Moderate snow",
    75: "Heavy snow",
    80: "Light showers",
    81: "Moderate showers",
    82: "Heavy showers",
    85: "Light snow showers",
    86: "Heavy snow showers",
    95: "Thunderstorm",
    96: "Thunderstorm with hail",
    99: "Thunderstorm with heavy hail",
}
