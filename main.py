# Main code for computing the adaptative shared headways for the toy problem (January 2019)

import numpy as np
#import random


################################################################################
###########################   PARAMETERS   #####################################
################################################################################

L = 2 # number of different bus lines
route_lengths = np.array([10,10]) # lengths of the routes before MP (km)
stop_numbers = np.array([30,30])
v_max = 50 # (km/h)
v_min = 40 # (km/h)
b = 2.5 # passengers boarding rate (s/passenger)
dt = 30 # time increments (s)
p = 5 # number of buses before MP for which optimal possible headways are computed
q = 5 # number of previous buses used as references in computing the desired new headways
arrival_rates = np.array([1,1]) # mean passengers arrival rates at stops (passengers/minute)
input_headways = np.array([7,5]) # average headways between buses at the start of the route for each line (minutes)
input_deviations = np.array([1,0.5]) # std of the input normal distribution for buses (minutes)
time_limit = 120 # time at which the simulation stops (minutes)


################################################################################
#########################   INITIALIZATION   ###################################
################################################################################


t = 0 # current time
waiting_passengers = [] # number of passengers currently waiting at a given stop
for l in range(L):
    waiting_passengers.append(np.random.poisson(arrival_rates[l]*input_headways[l],stop_numbers[l])) # generate an average distribution before the first bus shows up
#waiting_passengers = np.zeros([L,max(stop_numbers)]) # number of passengers currently waiting at a given stop
#bus_positions = -np.ones([L,100]) # current positions of all the buses in the merging zone (less than 100)
bus_positions = [[0],[0]] # current positions of all the buses in the merging zone (m)
inter_stop_distances = 1000*route_lengths/stop_numbers # distance between two consecutive stops (m)
#stop_positions = np.array()
next_bus_events = [[0],[0]] # delays in which corresponding bus will arrive to the next stop/leave the stop it is at
is_at_stop = [[0],[0]] # indicate at which stop the corresponding bus is. 0 if the bus is not currently at a stop
command_speeds = [[v_max],[v_max]] # speed at which each bus should be going according to the controller

#total_arrival_rate = np.tensordot(stop_numbers,arrival_rates,axes=1)


################################################################################
###########################   SIMULATION   #####################################
################################################################################


while t < time_limit*60:

    next_bus_event = min([min(x) for x in next_bus_events])

    #if next_bus_event < dt - t%dt: # the next event is a bus arriving at/leaving a stop

    for l in range(L):
        if next_bus_event in next_bus_events[l]: # OBS ! Ignores simultaneous events
            bus_line = l
            bus_nb = np.argmin(next_bus_events[l])
            break

    if is_at_stop[bus_line][bus_nb] != 0:

        print('The next event is bus number ' + str(bus_nb) + ' from bus line ' + str(bus_line) + ' leaving stop ' + str(is_at_stop[bus_line][bus_nb]))

        is_at_stop[bus_line][bus_nb] = 0

    else:

        next_stop = bus_positions[bus_line][bus_nb]//inter_stop_distances[bus_line] + 1

        if next_stop == stop_numbers[bus_line]: # OBS ! Watch out for mismatch int and double

            print('A bus from line ' + str(bus_line) + ' arrives at the MP.')


        else:

            is_at_stop[bus_line][bus_nb] = next_stop

            print('The next event is bus number ' + str(bus_nb) + ' from bus line ' + str(bus_line) + ' arriving at stop ' + str(next_stop))

            for l in range(L):
                waiting_passengers[l] += np.random.poisson(arrival_rates[l]*next_bus_event,stop_numbers[l]) # Generate passengers arrivals during this delay


    for l in range(L):
        next_bus_events[l] = [x - next_bus_event for x in next_bus_events[l]]

    # Check if everything in next_bus_events is > 0




    else:






    while H_previous == 0:
