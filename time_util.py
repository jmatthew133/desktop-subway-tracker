import math
from datetime import datetime
from zoneinfo import ZoneInfo

def parse_bus_dt(dt):
    if dt is None:
        return None
    formatted_dt = datetime.fromisoformat(dt)
    return formatted_dt.replace(tzinfo = None)

def minutes_until(dt):
    now = datetime.now()
    return math.floor((dt - now).total_seconds() / 60)

def current_time_string():
    now = datetime.now()
    return now.strftime("%H:%M:%S")

def current_date_time_string():
    now = datetime.now()
    return now.strftime("%-I:%M %p\n%a, %b %-d")

def format_arrival_time(dt):
    return dt.astimezone().strftime("%-I:%M %p")

def minutes_ago_string(reference_dt):
    if reference_dt is None:
        return "Not yet updated"
    now = datetime.now(reference_dt.tzinfo) if reference_dt.tzinfo else datetime.now()
    elapsed_minutes = int((now - reference_dt).total_seconds() // 60)
    if elapsed_minutes <= 0:
        return "Updated just now"
    if elapsed_minutes == 1:
        return "Updated 1 min ago"
    return f"Updated {elapsed_minutes} min ago"