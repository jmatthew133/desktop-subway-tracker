import time
import traceback
from display import init_display, clear_and_sleep, draw_weather_and_transit_lines
from time_util import current_time_string
from subway import get_next_trains, print_train_times
from bus import get_next_buses, print_bus_times
from weather import get_weather, print_weather

Q_STOP = "Q03S" # 72nd St Q Southbound
Q_LINE = "Q"
Q_STOP_NAME = "72 St"

SIX_STOP = "627S" # 77th St 6 Southbound
SIX_LINE = "6"
SIX_STOP_NAME = "77 St"

M31_STOP_ID = "402349" # York Av/E 77 St
M31_LINE = "M31"
M31_STOP_NAME = "York Av/E 77 St"

REFRESH_INTERVAL = 30 # seconds


def main(): 
    epd = init_display()
    
    try: 
        while True:
            # Subway Times
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
            
            print()
            
            # Weather
            weather_lines = []
            
            weather_data = get_weather()
            forecast = print_weather(weather_data)
            weather_lines += forecast
            
            print()
            
            # Main draw function
            draw_weather_and_transit_lines(epd, weather_lines, transit_lines)
                
            print("Refresh cycle complete! " + current_time_string())   
            print("_____________________")
            print()
            
            time.sleep(REFRESH_INTERVAL)
    except KeyboardInterrupt:
        print()
        print("Interrupted by User")
    except Exception as e:
        print("Encountered error during execution")
        print(f"Error: {e}")
        traceback.print_exc()
    finally:
        clear_and_sleep(epd)
            
if __name__ == "__main__":
    main()
