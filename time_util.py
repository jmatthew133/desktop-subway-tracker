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