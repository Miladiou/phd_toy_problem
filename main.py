# Main code for computing the adaptative shared headways for the toy problem (January 2019)

import numpy as np


################################################################################
###########################   PARAMETERS   #####################################
################################################################################

L = 2 # number of different bus lines
route_lengths = np.array([10,10]) # lengths of the routes before MP (km)
stop_numbers = np.array([10,4])
v_max = 50 # (km/h)
v_min = 40 # (km/h)
b = 2.5 # passengers boarding rate (s/passenger)
dt = 30 # time increments (s)
p = 5 # number of buses before MP for which optimal possible headways are computed
q = 5 # number of previous buses used as references in computing the desired new headways
arrival_rates = np.array([1,1]) # mean passengers arrival rates at stops (passengers/minute)
input_headways = np.array([7,5]) # average headways between buses at the start of the route for each line (minutes)
input_deviations = np.array([1,0.5]) # std of the input normal distribution for buses (minutes)
time_limit = 120000 # time at which the simulation stops (minutes)


################################################################################
#########################   INITIALIZATION   ###################################
################################################################################


t = 0 # current time
v_max = v_max*1000/3600 # convert speed in m/s
v_min = v_min*1000/3600
arrival_rates = arrival_rates/60 # convert arrival rates in passengers/s
last_time_visited = [] # time at which the last bus left a given stop
for l in range(L):
    last_time_visited.append(np.zeros(stop_numbers[l]))
#bus_positions = -np.ones([L,100]) # current positions of all the buses in the merging zone (less than 100)
bus_positions = [[0],[0]] # current positions of all the buses in the merging zone (m)
inter_stop_distances = 1000*route_lengths/stop_numbers # distance between two consecutive stops (m)
#stop_positions = np.array()
next_bus_events = [[0],[0]] # delays in which corresponding bus will arrive to the next stop/leave the stop it is at
is_at_stop = [[0],[0]] # indicate at which stop the corresponding bus is. 0 if the bus is not currently at a stop
command_speeds = [[v_max],[v_max]] # speed at which each bus should be going according to the controller
next_bus_inputs = np.random.normal(input_headways, input_deviations)*60 # delays in which new buses from each line will join the network

next_bus_events = [[inter_stop_distances[l]/command_speeds[l][0]] for l in range(L)]

################################################################################
###########################   SIMULATION   #####################################
################################################################################


counter = 0

while t < time_limit*60:

    counter += 1

    next_bus_event = min([min(x) for x in next_bus_events])
    next_bus_input = min(next_bus_inputs)
    next_event = min(next_bus_event, next_bus_input)

    t += next_event # update simulation time

    print(next_event)

    if next_bus_event == next_bus_input:

        print('OBS ! Two events are happening simultaneously.')

        break

    elif next_bus_event < next_bus_input:

    #if next_bus_event < dt - t%dt: # the next event is a bus arriving at/leaving a stop

        next_event_bus_lines = []
        next_event_bus_numbers = [] # Include all the buses that will take part in the next event

        for l in range(L):

            occurences_nb = next_bus_events[l].count(next_bus_event)

            if occurences_nb != 0:

                indexes = [i for i,x in enumerate(next_bus_events[l]) if x == next_bus_event]

                next_event_bus_lines += [l for i in range(len(indexes))]
                next_event_bus_numbers += indexes

                #next_event_bus_numbers.append(np.argmin(next_bus_events[l]))


        for i in range(len(next_event_bus_lines)):

            bus_line = next_event_bus_lines[i]
            bus_nb = next_event_bus_numbers[i]

            current_stop = is_at_stop[bus_line][bus_nb]

            if current_stop != 0:

                print('The next event is bus number ' + str(bus_nb + 1) + ' from bus line ' + str(bus_line + 1) + ' leaving stop ' + str(current_stop))

                is_at_stop[bus_line][bus_nb] = 0

                next_bus_events[bus_line][bus_nb] += inter_stop_distances[bus_line]/command_speeds[bus_line][bus_nb]
                bus_positions[bus_line][bus_nb] -= next_event*command_speeds[bus_line][bus_nb] # Update distance since the bus has not moved

                last_time_visited[bus_line][current_stop-1] = t

            else:

                next_stop = int((bus_positions[bus_line][bus_nb]+0.00001)//inter_stop_distances[bus_line]) + 1 # Take into account the slight deviations on the position

                if next_stop == stop_numbers[bus_line]: # OBS ! Watch out for mismatch int and double

                    print('A bus from line ' + str(bus_line + 1) + ' arrives at the MP.')

                    bus_positions[bus_line].pop(0) # remove the bus from the system
                    next_bus_events[bus_line].pop(0)
                    is_at_stop[bus_line].pop(0)
                    command_speeds[bus_line].pop(0)

                    same_line_buses_nb = next_event_bus_lines[i+1:].count(bus_line) # In case an event occurs at the same time for a bus of the same line

                    if same_line_buses_nb != 0:

                        next_event_bus_numbers[i+1:i+1+same_line_buses_nb] = [x-1 for x in next_event_bus_numbers[i+1:i+1+same_line_buses_nb]]

                else:

                    is_at_stop[bus_line][bus_nb] = next_stop

                    print('The next event is bus number ' + str(bus_nb + 1) + ' from bus line ' + str(bus_line + 1) + ' arriving at stop ' + str(next_stop))

                    bus_positions[bus_line][bus_nb] += next_event*command_speeds[bus_line][bus_nb] # Update the bus distance

                    waiting_passengers = np.random.poisson(arrival_rates[l]*(t - last_time_visited[bus_line][next_stop - 1])) # generate the passengers that have arrived since last bus
                    waiting_passengers += np.random.poisson(b*waiting_passengers*arrival_rates[l]) # add any other additional passengers that might arrive meanwhile

                    next_bus_events[bus_line][bus_nb] += waiting_passengers*b


    else:

        bus_line = np.argmin(next_bus_inputs)

        print('The next event is a bus from line ' + str(bus_line + 1) + ' joining the network.')

        bus_positions[bus_line].append(0)
        next_bus_events[bus_line].append(inter_stop_distances[bus_line]/v_max)
        is_at_stop[bus_line].append(0)
        command_speeds[bus_line].append(v_max)

        next_bus_inputs[bus_line] += np.random.normal(input_headways[bus_line], input_deviations[bus_line])*60

    for l in range(L):

        next_bus_events[l] = [x - next_event for x in next_bus_events[l]] # update delays # OBS ! Check if everything in next_bus_events is > 0

        bus_positions[l] = [x + next_event*v*(1 - min(y,1)) for x, v, y in zip(bus_positions[l], command_speeds[l], is_at_stop[l])] # update positions for relevant buses

    next_bus_inputs -= next_event # update delays

    print(bus_positions)
    print(next_bus_events)

    #if counter == 50:

        #break
