from nyct_gtfs import NYCTFeed
from time_util import minutes_until

def print_train_times(upcoming_arrivals, line, stop_name):
    print(f"The next southbound {line} trains from {stop_name} are:")
    for a in upcoming_arrivals:
        at = a["arrival_dt"].astimezone().strftime("%H:%M")
        print(f"  {a['mins_away']:>3} min @ {at}")
    

def get_next_trains(line: str, stop_id: str, limit: int = 3):
    feed = NYCTFeed(line)
    trips = feed.filter_trips(line_id=[line], headed_for_stop_id=[stop_id])

    upcoming_arrivals = []
    for trip in trips:
        stu = trip.stop_time_updates
        my_stops = [s for s in stu if s.stop_id == stop_id]
        for stop in my_stops:
            mins = minutes_until(stop.arrival)
            if mins > 0:
                upcoming_arrivals.append({
                    "mins_away": mins,
                    "arrival_dt": stop.arrival
                })

    return upcoming_arrivals[:limit]