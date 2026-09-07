from concurrent.futures import ThreadPoolExecutor, TimeoutError as FutureTimeoutError
from nyct_gtfs import NYCTFeed
from time_util import format_arrival_time, minutes_until

FEED_TIMEOUT = 15  # seconds; nyct_gtfs calls requests.get() with no timeout of its own

def print_train_times(upcoming_arrivals, line, stop_name):
    print(f"{line} trains from {stop_name}:")
    times = []
    for a in upcoming_arrivals:
        at = format_arrival_time(a["arrival_dt"])
        time_string = f"{a['mins_away']:>3} min @ {at}"
        print(f"  {time_string}")
        times.append(time_string)
    return {"label": line, "kind": "bullet", "times": times}
    

def _load_feed(line: str):
    # NYCTFeed(line) fetches immediately in the constructor with no timeout support,
    # so a stalled connection would otherwise hang the whole single-threaded main loop.
    # shutdown(wait=False) on timeout so we don't block waiting for a hung thread to finish.
    executor = ThreadPoolExecutor(max_workers=1)
    future = executor.submit(NYCTFeed, line)
    try:
        return future.result(timeout=FEED_TIMEOUT)
    except FutureTimeoutError:
        executor.shutdown(wait=False)
        raise TimeoutError(f"NYCTFeed({line!r}) did not respond within {FEED_TIMEOUT}s")
    else:
        executor.shutdown(wait=False)


def get_next_trains(line: str, stop_id: str, limit: int = 3):
    feed = _load_feed(line)
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

    upcoming_arrivals.sort(key=lambda arrival: arrival["arrival_dt"])
    return upcoming_arrivals[:limit]