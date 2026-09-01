from datetime import datetime

from groq import Groq
from local_config import GROQ_API_KEY


MODEL = "groq/compound-mini"
MAX_WORDS = 40


def _remaining_hours(weather_data):
    hourly = weather_data.get("hourly", {})
    now = datetime.now()
    hours = []

    for timestamp, temperature, precipitation_chance, precipitation, code in zip(
        hourly.get("time", []),
        hourly.get("temperature_2m", []),
        hourly.get("precipitation_probability", []),
        hourly.get("precipitation", []),
        hourly.get("weather_code", []),
    ):
        hour = datetime.fromisoformat(timestamp)
        if hour.date() != now.date() or hour < now.replace(minute=0, second=0, microsecond=0):
            continue
        hours.append({
            "time": hour.strftime("%-I %p"),
            "temperature": round(temperature),
            "precipitation_chance": precipitation_chance,
            "precipitation": precipitation,
            "description": weather_data["weather_codes"].get(code, "Unknown"),
        })

    return hours


def _weather_summary(weather_data):
    current = weather_data["current"]
    remaining_hours = _remaining_hours(weather_data)
    hour_lines = [
        (
            f"{hour['time']}: {hour['description']}, {hour['temperature']}F, "
            f"{hour['precipitation_chance']}% precipitation chance, "
            f"{hour['precipitation']} in precipitation"
        )
        for hour in remaining_hours
    ]

    return "\n".join([
        f"Current conditions: {current['desc']}, {current['temp']}F (feels {current['feels_like']}F).",
        f"Today's high/low: {current['high']}F / {current['low']}F.",
        "Hourly forecast for the rest of today:",
        *hour_lines,
    ])


def _fallback_outlook(weather_data):
    current = weather_data["current"]
    remaining_hours = _remaining_hours(weather_data)
    rainy_hours = [hour for hour in remaining_hours if hour["precipitation_chance"] >= 50]

    if rainy_hours:
        first_rain = rainy_hours[0]
        return (
            f"{first_rain['precipitation_chance']}% chance of precipitation around "
            f"{first_rain['time']}. Bring an umbrella."
        )

    return (
        f"{current['desc']} now, with a high of {current['high']}F. "
        "No significant precipitation expected today."
    )


def get_outlook(weather_data):
    fallback = _fallback_outlook(weather_data)
    if not GROQ_API_KEY:
        print("[Outlook] GROQ_API_KEY is not configured; using fallback")
        return fallback

    try:
        client = Groq(api_key=GROQ_API_KEY)
        messages = [
            {
                "role": "system",
                "content": (
                    "Write a warm, practical weather outlook for an e-ink desktop "
                    "display. Focus on changes later today and helpful advice such "
                    "as when rain starts or ends (bring an umbrella), will it be "
                    "especially hot/chilly later (bring a jacket), etc. You may "
                    "repeat the current conditions, but not current temperature, "
                    "feels-like temperature, or daily high and low because they "
                    "are already shown on the display. Use only the supplied "
                    "weather facts. "
                    f"Write one or two sentences, at most {MAX_WORDS} words, with no markdown or emojis."
                ),
            },
            {"role": "user", "content": _weather_summary(weather_data)},
        ]
        response = client.chat.completions.create(
            model=MODEL,
            temperature=0.4,
            max_completion_tokens=200,
            messages=messages,
        )
        outlook = (response.choices[0].message.content or "").strip()
        if outlook:
            print(f"Generated weather outlook with Groq ({MODEL})")
            print(outlook)
            return outlook
        print("Groq returned no display text for weather outlook")
    except Exception as error:
        print(f"Groq request for weather outlook failed: {error}")

    print("Using fallback weather outlook")
    print(fallback)
    return fallback