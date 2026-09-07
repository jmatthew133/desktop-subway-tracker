import time
import traceback
import signal
import sys
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from PIL import Image
from display import init_display, draw_weather_and_transit_lines
from display import draw_right_half_only
from subway import get_next_trains, print_train_times
from bus import get_next_buses, print_bus_times
from weather import get_weather, print_weather
from outlook import get_outlook

Q_STOP = "Q03S" # 72nd St Q Southbound
Q_LINE = "Q"
Q_STOP_NAME = "72 St"

SIX_STOP = "627S" # 77th St 6 Southbound
SIX_LINE = "6"
SIX_STOP_NAME = "77 St"

M31_STOP_ID = "402349" # York Av/E 77 St
M31_LINE = "M31"
M31_STOP_NAME = "York Av/E 77 St"

TRANSIT_REFRESH_INTERVAL = 60  # Fast: 60s
WEATHER_REFRESH_INTERVAL = 3600  # Slow: 60m (3600s)
NYC_TIMEZONE = ZoneInfo("America/New_York")

WIDTH, HEIGHT = 800, 480


def next_minute_boundary(now):
    return now.replace(second=0, microsecond=0) + timedelta(minutes=1)


def next_hour_boundary(now):
    return now.replace(minute=0, second=0, microsecond=0) + timedelta(hours=1)


def _handle_sigterm(signum, frame):
    # systemctl stop/restart and reboot send SIGTERM. Python only auto-converts SIGINT into
    # KeyboardInterrupt, so without this, SIGTERM would kill the process before the finally
    # block below could clear/sleep the e-ink display.
    raise KeyboardInterrupt()


def fetch_transit_data():
    upcoming_q_trains = get_next_trains(Q_LINE, Q_STOP, 3)
    q_group = print_train_times(upcoming_q_trains, Q_LINE, Q_STOP_NAME)

    upcoming_6_trains = get_next_trains(SIX_LINE, SIX_STOP, 3)
    six_group = print_train_times(upcoming_6_trains, SIX_LINE, SIX_STOP_NAME)

    upcoming_m31_buses = get_next_buses(M31_STOP_ID, 3)
    bus_group = print_bus_times(upcoming_m31_buses, M31_LINE, M31_STOP_NAME)

    return [q_group, six_group, bus_group]


def fetch_weather_data():
    weather_json = get_weather()
    weather_data = print_weather(weather_json)
    outlook = get_outlook(weather_json)
    return weather_data, outlook


def main():
    """
    Tiered refresh system:
    - Transit: partial refresh every TRANSIT_REFRESH_INTERVAL seconds
    - Weather + fact: full refresh every WEATHER_REFRESH_INTERVAL seconds
    """
    signal.signal(signal.SIGTERM, _handle_sigterm)
    epd = init_display()
    exit_code = 0
    
    # Shared background image (persistent across refreshes)
    background = Image.new("1", (WIDTH, HEIGHT), 255)
    
    # State tracking
    transit_lines = []
    weather_data = {}
    outlook = ""
    
    # Schedule refreshes against wall-clock boundaries, not startup time.
    next_transit_refresh = None
    next_weather_refresh = None
    first_run = True
    
    try:
        print("Starting tiered refresh display...")
        print(f"Transit: every {TRANSIT_REFRESH_INTERVAL}s | Weather: every {WEATHER_REFRESH_INTERVAL}s")
        print()
        
        while first_run:
            try:
                transit_lines = fetch_transit_data()
            except Exception as e:
                print(f"  ✗ Transit fetch failed: {e}")

            try:
                weather_data, outlook = fetch_weather_data()
            except Exception as e:
                print(f"  ✗ Weather fetch failed: {e}")

            print(f"[{time.strftime('%H:%M:%S')}] Initial full render...")
            draw_weather_and_transit_lines(
                epd, background, weather_data, transit_lines, outlook
            )
            print("  ✓ Display initialized")
            print()
            now = datetime.now(NYC_TIMEZONE)
            next_transit_refresh = next_minute_boundary(now)
            next_weather_refresh = next_hour_boundary(now)
            first_run = False

        while True:
            now = datetime.now(NYC_TIMEZONE)
            full_refresh_completed = False

            if now >= next_weather_refresh:
                print(f"[{time.strftime('%H:%M:%S')}] Updating weather, outlook, and transit...")
                try:
                    weather_data, outlook = fetch_weather_data()
                    transit_lines = fetch_transit_data()
                    draw_weather_and_transit_lines(
                        epd, background, weather_data, transit_lines, outlook
                    )
                    next_weather_refresh = next_hour_boundary(now)
                    next_transit_refresh = next_minute_boundary(now)
                    full_refresh_completed = True
                    print("  ✓ Weather, outlook, and transit fetched and full display refreshed")
                    print()
                except Exception as e:
                    print(f"  ✗ Hourly full refresh failed: {e}")
                    print()

            if (
                not full_refresh_completed
                and now >= next_transit_refresh
            ):
                print(f"[{time.strftime('%H:%M:%S')}] Updating transit...")
                try:
                    transit_lines = fetch_transit_data()
                    draw_right_half_only(epd, background, transit_lines)
                    next_transit_refresh = next_minute_boundary(now)
                    print("  ✓ Transit data fetched and displayed")
                    print()
                except Exception as e:
                    print(f"  ✗ Transit fetch failed: {e}")
                    print()

            time.sleep(1)
            
    except KeyboardInterrupt:
        print("\n\nInterrupted by user")
        exit_code = 0
    except Exception as e:
        print(f"\nEncountered error during execution")
        print(f"Error: {e}")
        traceback.print_exc()
        exit_code = 1
    finally:
        print("Clearing display before shutdown...")
        try:
            epd.clear()
            epd.sleep()
        except Exception as e:
            print(f"  ✗ Display cleanup failed: {e}")
        print("Display stopped")

    sys.exit(exit_code)

if __name__ == "__main__":
    main()
