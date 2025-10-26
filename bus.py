import requests
from time_util import parse_bus_dt, minutes_until
from local_config import BUS_API_KEY # API key is in a local file that is gitignored

URL = "https://bustime.mta.info/api/siri/stop-monitoring.json"

def print_bus_times(upcoming_arrivals, line, stop_name):
    print(f"The next southbound {line} buses from {stop_name} are:")
    for a in upcoming_arrivals:
        at = a["arrival_dt"].astimezone().strftime("%H:%M")
        print(f"  {a['mins_away']:>3} min @ {at}")

def get_next_buses(stop_id: str, limit: int = 3):
    params = {
        "key": BUS_API_KEY,
        "MonitoringRef": stop_id,
        "OperatorRef": "MTA"
    }
    
    resp = requests.get(URL, params = params, timeout = 10)
    resp.raise_for_status()
    js = resp.json()
    
    try:
        deliveries = js["Siri"]["ServiceDelivery"]["StopMonitoringDelivery"]
    except KeyError:
        return []
    
    upcoming_arrivals = []
    for delivery in deliveries:
        visits = delivery.get("MonitoredStopVisit", [])
        for visit in visits:
            mvj = visit.get("MonitoredVehicleJourney", {})
            mc = mvj.get("MonitoredCall", {})
            expected = mc.get("ExpectedArrivalTime") or mc.get("AimedArrivalTime")
            
            arrival_dt = parse_bus_dt(expected)
            mins = minutes_until(arrival_dt)
            if mins > 0:
                upcoming_arrivals.append({
                    "mins_away": mins,
                    "arrival_dt": arrival_dt
                })
        
        return upcoming_arrivals[:limit]



