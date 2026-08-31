import time
import traceback
from PIL import Image
from display import init_display, draw_weather_and_transit_lines
from display import draw_right_half_only, draw_left_half_only
from time_util import current_time_string
from subway import get_next_trains, print_train_times
from bus import get_next_buses, print_bus_times
from weather import get_weather, print_weather
from daily_fact import get_daily_fact

Q_STOP = "Q03S" # 72nd St Q Southbound
Q_LINE = "Q"
Q_STOP_NAME = "72 St"

SIX_STOP = "627S" # 77th St 6 Southbound
SIX_LINE = "6"
SIX_STOP_NAME = "77 St"

M31_STOP_ID = "402349" # York Av/E 77 St
M31_LINE = "M31"
M31_STOP_NAME = "York Av/E 77 St"

TRANSIT_REFRESH_INTERVAL = 30  # Fast: 30s
WEATHER_REFRESH_INTERVAL = 3600  # Slow: 60m (3600s)

WIDTH, HEIGHT = 800, 480


def fetch_transit_data():
    transit_lines = []
    
    upcoming_q_trains = get_next_trains(Q_LINE, Q_STOP, 3)
    q_times = print_train_times(upcoming_q_trains, Q_LINE, Q_STOP_NAME)
    transit_lines += q_times
    
    upcoming_6_trains = get_next_trains(SIX_LINE, SIX_STOP, 3)
    six_times = print_train_times(upcoming_6_trains, SIX_LINE, SIX_STOP_NAME)
    transit_lines += six_times
    
    upcoming_m31_buses = get_next_buses(M31_STOP_ID, 3)
    bus_times = print_bus_times(upcoming_m31_buses, M31_LINE, M31_STOP_NAME)
    transit_lines += bus_times
    
    return transit_lines


def fetch_weather_data():
    weather_data = get_weather()
    weather_lines = print_weather(weather_data)
    daily_fact = get_daily_fact()
    return weather_lines, daily_fact


def main():
    """
    Tiered refresh system:
    - Right half (transit): updates every TRANSIT_REFRESH_INTERVAL seconds
    - Left half (weather + fact): updates every WEATHER_REFRESH_INTERVAL seconds
    
    Shared background image is maintained and updated partially.
    """
    epd = init_display()
    
    # Shared background image (persistent across refreshes)
    background = Image.new("1", (WIDTH, HEIGHT), 255)
    
    # State tracking
    transit_lines = []
    weather_lines = []
    daily_fact = ""
    
    # Track last update times
    last_transit_update_time = 0
    last_weather_update_time = 0
    first_run = True
    
    try:
        print("Starting tiered refresh display...")
        print(f"Transit: every {TRANSIT_REFRESH_INTERVAL}s | Weather: every {WEATHER_REFRESH_INTERVAL}s")
        print()
        
        while first_run:
            now = time.time()
            try:
                transit_lines = fetch_transit_data()
                last_transit_update_time = now
            except Exception as e:
                print(f"  ✗ Transit fetch failed: {e}")

            try:
                weather_lines, daily_fact = fetch_weather_data()
                last_weather_update_time = now
            except Exception as e:
                print(f"  ✗ Weather fetch failed: {e}")

            print(f"[{time.strftime('%H:%M:%S')}] Initial full render...")
            draw_weather_and_transit_lines(
                epd, background, weather_lines, transit_lines, daily_fact
            )
            print("  ✓ Display initialized")
            first_run = False

        with epd.display_bilevel_partial_refresh() as partial_display:
            print("  ✓ Partial refresh mode ready")
            print()
            while True:
                now = time.time()

                if now - last_transit_update_time >= TRANSIT_REFRESH_INTERVAL:
                    print(f"[{time.strftime('%H:%M:%S')}] Updating transit...")
                    try:
                        transit_lines = fetch_transit_data()
                        draw_right_half_only(partial_display, background, transit_lines)
                        last_transit_update_time = now
                        print("  ✓ Transit data fetched and displayed")
                        print()
                    except Exception as e:
                        print(f"  ✗ Transit fetch failed: {e}")
                        print()

                if now - last_weather_update_time >= WEATHER_REFRESH_INTERVAL:
                    print(f"[{time.strftime('%H:%M:%S')}] Updating weather and fact...")
                    try:
                        weather_lines, daily_fact = fetch_weather_data()
                        draw_left_half_only(partial_display, background, weather_lines, daily_fact)
                        last_weather_update_time = now
                        print("  ✓ Weather + fact data fetched and displayed")
                        print()
                    except Exception as e:
                        print(f"  ✗ Weather fetch failed: {e}")
                        print()

                time.sleep(1)
            
    except KeyboardInterrupt:
        print("\n\nInterrupted by user")
    except Exception as e:
        print(f"\nEncountered error during execution")
        print(f"Error: {e}")
        traceback.print_exc()
    finally:
        print("Display stopped")
            
if __name__ == "__main__":
    main()
