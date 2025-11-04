import time
from display import init_display, draw_lines, clear_and_sleep
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
            lines = []
            
            upcoming_q_trains = get_next_trains(Q_LINE, Q_STOP, 3)
            q_times = print_train_times(upcoming_q_trains, Q_LINE, Q_STOP_NAME)
            lines += q_times
            
            upcoming_6_trains = get_next_trains(SIX_LINE, SIX_STOP, 3)
            six_times = print_train_times(upcoming_6_trains, SIX_LINE, SIX_STOP_NAME)
            lines += six_times
            
            upcoming_m31_buses = get_next_buses(M31_STOP_ID, 3)
            bus_times = print_bus_times(upcoming_m31_buses, M31_LINE, M31_STOP_NAME)
            lines += bus_times
            
            print()
            
            # Weather
            forecast = get_weather()
            weather_lines = print_weather(forecast)
            lines += weather_lines
            
            print()
            
            # Last Updated
            current_time = current_time_string()
            lines.append("")
            lines.append("Last updated at: " + current_time)
            
            draw_lines(epd, lines)
                
            print("Refresh cycle complete! " + current_time)   
            print("_____________________")
            print()
            
            time.sleep(REFRESH_INTERVAL)
    except KeyboardInterrupt:
        print()
        print("Interrupted by User")
    except Exception as e:
        print("Encountered error during execution")
        print(f"Error: {e}")
    finally:
        clear_and_sleep(epd)
            
if __name__ == "__main__":
    main()
