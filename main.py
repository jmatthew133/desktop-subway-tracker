import time
from subway import get_next_trains, print_train_times
from bus import get_next_buses, print_bus_times

Q_STOP = "Q03S" # 72nd St Q Southbound
Q_LINE = "Q"
Q_STOP_NAME = "72nd St"

SIX_STOP = "627S" # 77th St 6 Southbound
SIX_LINE = "6"
SIX_STOP_NAME = "77th St"

M31_STOP_ID = "402349" # York Av/E 77 ST
M31_LINE = "M31"
M31_STOP_NAME = "77th St/York Ave"

while True:
    upcoming_q_trains = get_next_trains(Q_LINE, Q_STOP, 4)
    print_train_times(upcoming_q_trains, Q_LINE, Q_STOP_NAME)
    
    upcoming_6_trains = get_next_trains(SIX_LINE, SIX_STOP, 4)
    print_train_times(upcoming_6_trains, SIX_LINE, SIX_STOP_NAME)
    
    upcoming_m31_buses = get_next_buses(M31_STOP_ID, 4)
    print_bus_times(upcoming_m31_buses, M31_LINE, M31_STOP_NAME)
    
    print()
    print()
        
    time.sleep(30)

