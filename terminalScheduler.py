# I collaborate with Jiaying He on this assignment.
# I watched the video "Constraint-Satisfaction Problems in Python" on youtube to learn the backtracking algorithm solution.
# I learned the implementation of backtracking algorithm from https://github.com/KGB33/ClassicComputerScienceProblems/tree/c054e8fef1bcb99731f84d675368191caff086e1/CCSP/c3_ConstraintStatisfactionProblems
# I removed the CSP library code and rewrote it

import sys
import json
import re

#######################
### Basic functions ###
#######################

def read_json(file_path):
    with open(file_path, 'r') as file:
        return json.load(file)

def write_json(file_path, data):
    with open(file_path, 'w') as file:
        json.dump(data, file, indent=4)

def time_to_minutes(time):
    # convert time in minutes after midnight
    hours = time // 100
    minutes = time % 100
    return hours * 60 + minutes

def minutes_to_time(minutes_m):
    # convert minutes after midnight to time
    hours = minutes_m // 60
    minutes = minutes_m % 60
    return hours * 100 + minutes

def check_overlap(start_time1, end_time1, start_time2, end_time2):
    # function to check if two time intervals overlap
    if end_time1 > start_time2 and end_time1 <= end_time2:
        return True
    elif start_time1 < end_time2 and start_time1 >= start_time2:
        return True
    elif start_time1 < start_time2 and end_time1 > end_time2:
        return True
    elif start_time1 > start_time2 and end_time1 < end_time2:
        return True
    else:
        return False
    

#######################
#### SCP functions ####
#######################

def create_variables_and_domains(meta, aircraft, trucks):
    start_time = time_to_minutes(meta['Start Time'])
    stop_time = time_to_minutes(meta['Stop Time'])
    hangars = meta['Hangars']
    forklifts = meta['Forklifts']
 
    variables = []
    aircraft_names = []
    truck_names = []
    forklifts_tasks = []

    # variables: 
    # aircrafts (hangar, arrival time, departure time)
    for aircraft_name, _ in aircraft.items():
        variables.append(aircraft_name)
        aircraft_names.append(aircraft_name)

    # trucks (hangar, arrival time, departure time)
    for truck_name, _ in trucks.items():
        variables.append(truck_name)
        truck_names.append(truck_name)

    # forklift_tasks (forklift, hangar, arrival time, job) // each cargo has an unload and a load task for forklift
    for aircraft_name, aircraft_info in aircraft.items():
        # calculate the number of cargo for forklift to unload and load
        cargo_num = aircraft_info['Cargo']
        # for each cargo, create an unload and a load task
        for i in range(cargo_num):
            variables.append(f"{aircraft_name}_unload_{i}")
            forklifts_tasks.append(f"{aircraft_name}_unload_{i}")
            variables.append(f"{aircraft_name}_load_{i}")
            forklifts_tasks.append(f"{aircraft_name}_load_{i}")

    domains = {}

    # create the domains for aircrafts:
    #   aircrafts: 
    #       hangar ∈ hangars, 
    #       arrival time > aircraft['Time'], // Time of the aircraft arrives hanger is after the aircraft arrives the terminal
    #       start_time < arrival time < departure time < stop_time, 
    #       departure time - arrival time = 20 + 5*n // at least 20 minutes to unload cargo, 
    for aircraft_name, aircraft_info in aircraft.items():
        domains[aircraft_name] = []
        aircraft_time = time_to_minutes(aircraft_info['Time'])
        earliest_arrival = max(aircraft_time, start_time)

        for hangar in hangars:
            for arrival_time in range(earliest_arrival, stop_time - 20 + 1, 5):
                for departure_time in range(arrival_time + 20, stop_time + 1, 5):
                    domains[aircraft_name].append((hangar, arrival_time, departure_time))

    # create the domains for trucks:
    #   trucks:
    #       hangar ∈ hangars, 
    #       arrival time > truck['Time'], // Time of the truck arrives hanger is after the truck arrives the terminal
    #       arrival time ∈ [start_time, stop_time - 5], 
    #       departure time = arrival time + 5 // assume the truck always starts loading immediately after arrival
    for truck_name, truck_time in trucks.items():
        domains[truck_name] = []
        truck_time = time_to_minutes(truck_time)
        earliest_arrival = max(truck_time, start_time)

        for hangar in hangars:
            for arrival_time in range(earliest_arrival, stop_time - 5 + 1, 5):
                domains[truck_name].append((hangar, arrival_time, arrival_time + 5))
    
    # create the domains for forklift tasks:
    
    #   forklift_unload_tasks:
    #       forklift ∈ forklifts,
    #       aircraft ∈ aircrafts,
    #       hangar ∈ hangars,
    #       arrival time ∈ [start_time, stop_time - 20] for unload jobs or arrival time ∈ [start_time, stop_time - 5] for load jobs
    #       job = 'Unload'

    #   forklift_load_tasks:
    #       forklift ∈ forklifts,
    #       truck ∈ trucks,
    #       hangar ∈ hangars,
    #       arrival time ∈ [start_time, stop_time - 20] for unload jobs or arrival time ∈ [start_time, stop_time - 5] for load jobs
    #       job = 'Load'

    for aircraft_name in aircraft:
        cargo_num = aircraft[aircraft_name]['Cargo']
        # create the domains for unload and load tasks
        for i in range(cargo_num):
            unload_task = f"{aircraft_name}_unload_{i}"
            # unload tasks take 20 minutes
            domains[unload_task] = [
                (fl, aircraft_name, h, time, 'Unload') 
                for fl in forklifts
                for h in hangars
                for time in range(start_time, stop_time - 20 + 1, 5)
            ]

            load_task = f"{aircraft_name}_load_{i}"
            # load tasks take 5 minutes
            domains[load_task] = [
                (fl, t, h, time, 'Load')
                for fl in forklifts
                for t in truck_names
                for h in hangars
                for time in range(start_time, stop_time - 5 + 1, 5)
            ]

    return variables, domains, aircraft_names, truck_names, forklifts_tasks

def backtracking(unassign_variables, domains, assignments, aircraft_names, truck_names, forklifts_tasks):
    # if all variables are assigned, return the assignments
    if unassign_variables == []:
        return assignments
    
    unassigned_num = len(unassign_variables)
    total = len(domains.keys())
    print(f"Assigned variables: {total - unassigned_num}/{total}")

    # if not, select the first unassigned variable
    var = unassign_variables[0]

    # assign possible value in the domain to the variable
    for value in domains[var]:
        # create a new assignment to avoid modifying the original assignment
        new_assignments = assignments.copy()
        new_assignments[var] = value

        # check if the new assignment satisfies the constraints 
        if check_constraints(new_assignments, aircraft_names, truck_names, forklifts_tasks, var):
            # if the assignment is valid, recursively assign the next variable
            result = backtracking(unassign_variables[1:], domains, new_assignments, aircraft_names, truck_names, forklifts_tasks)
            if result:
                return result
        # if the assignment is invalid, try the next value in the domain
    
    # if no assignment is valid, return None
    return None

def check_constraints(assignment, aircraft_names, truck_names, forklifts_tasks, var):
    if var in aircraft_names:
        # check aircraft constraints
        new_aircraft = assignment[var]

        # constraint1: the hanger cannot be assigned to more than one aircraft at the same time
        for variable in assignment.keys():
            if variable in aircraft_names:
                if variable == var:
                    continue
                # if two aircraft assigned to the same hanger have overlapping time, return False
                if assignment[variable][0] == new_aircraft[0]:
                    if check_overlap(new_aircraft[1], new_aircraft[2], assignment[variable][1], assignment[variable][2]):
                        return False
        
                    
    elif var in truck_names:
        # check truck constraints

        new_truck = assignment[var]
        # constraint2: the hanger cannot be assigned to more than one truck at the same time
        for variable in assignment.keys():
            if variable in truck_names:
                if variable == var:
                    continue
                # if two aircraft assigned to the same hanger have overlapping time, return False
                if assignment[variable][0] == new_truck[0]:
                    if check_overlap(new_truck[1], new_truck[2], assignment[variable][1], assignment[variable][2]):
                        return False
    else:
        # aircraft and truck check can be skipped
        new_forklift_task = assignment[var]

        # constraint3: the forklift cannot be assigned to more than one task at the same time
        for variable in assignment.keys():
            if variable in forklifts_tasks:
                if variable == var:
                    continue
                # if two tasks uses the same forklift have overlapping time, return False
                if assignment[variable][0] == new_forklift_task[0]:
                    time1 = new_forklift_task[3]
                    time2 = assignment[variable][3]

                    if new_forklift_task[4] == "Unload":
                        duration1 = 20
                    else:
                        duration1 = 5

                    if assignment[variable][4] == "Unload":
                        duration2 = 20
                    else:
                        duration2 = 5
                    
                    if check_overlap(time1, time1 + duration1, time2, time2 + duration2):
                        return False

                    
        # constraint4: the forklift unload tasks should be assigned after the aircraft arrives and the load tasks should be assigned when the truck arrives
        if new_forklift_task[4] == "Unload":
            _, aircraft, h, time, _ = new_forklift_task
            if aircraft in aircraft_names:
                if h != assignment[aircraft][0]:
                    return False
                if not (assignment[aircraft][1] <= time < assignment[aircraft][2]):
                    return False
            else:
                return False
        else:
            # get the list of trucks that have been assigned to the forklifts
            assigned_trucks = []
            for variable in assignment:
                if variable in forklifts_tasks:
                    if variable == var:
                        continue
                    else:
                        if assignment[variable][4] == "Load":
                            assigned_trucks.append(assignment[variable][1])

            _, truck, h, time, _ = new_forklift_task
            if truck in truck_names:
                if truck in assigned_trucks:
                    return False
                if h != assignment[truck][0]:
                    return False
                if (assignment[truck][1] != time):
                    return False
            else:
                return False
                
        # constraint5: ensure unload tasks are completed before load tasks
        if re.search(r"_unload_", var):
            _, _, hangar1, time1, job = assignment[var]
            load_task = f"{var.split('_unload_')[0]}_load_{var.split('_load_')[-1]}"
            if load_task in assignment:
                _, _, hangar2, time2, _ = assignment[load_task]
                if time1 + 20 > time2:
                    return False
                if hangar1 != hangar2:
                    return False
                
        elif re.search(r"_load_", var):
            _, _, hangar1, time1, job = assignment[var]
            unload_task = f"{var.split('_load_')[0]}_unload_{var.split('_load_')[-1]}"
            if unload_task in assignment:
                _, _, hangar2, time2, _ = assignment[unload_task]
                if time1 < time2 + 20:
                    return False
                if hangar1 != hangar2:
                    return False

    return True

def generate_schedule(meta, aircraft, trucks):
    # create variables and domains
    variables, domains, aircraft_names, truck_names, forklifts_tasks = create_variables_and_domains(meta, aircraft, trucks)

    # initialize assignments
    assignments = {}

    # assign variables and check constraints using backtracking
    solution = backtracking(variables, domains, assignments, aircraft_names, truck_names, forklifts_tasks)

    # format the solution
    if solution:
        output = {
            'aircraft': {},
            'trucks': {},
            'forklifts': {}
        }
        for aircraft_name in aircraft_names:
            output['aircraft'][aircraft_name] = {
                'Hangar': solution[aircraft_name][0],
                'Arrival': minutes_to_time(solution[aircraft_name][1]),
                'Departure': minutes_to_time(solution[aircraft_name][2])
            }
        for truck_name in truck_names:
            output['trucks'][truck_name] = {
                'Hangar': solution[truck_name][0],
                'Arrival': minutes_to_time(solution[truck_name][1]),
                'Departure': minutes_to_time(solution[truck_name][2])
            }
        for forklift_task in forklifts_tasks:
            fork_lift_name, _, _, _, _ = solution[forklift_task]
            output['forklifts'][fork_lift_name] = []
        
        for forklift_task in forklifts_tasks:
            fork_lift_name, _, hangar, arrival_time, job = solution[forklift_task]
            output['forklifts'][fork_lift_name].append({
                    'Hangar': hangar,
                    'Time': minutes_to_time(arrival_time),
                    'Job': job
                })
        return output
    else:
        return {
            "aircraft": None,
            "trucks": None,
            "forklifts": None
        }

def main():
    if len(sys.argv) != 5:
        print("Usage: python scheduler.py <meta.json> <aircraft.json> <trucks.json> <schedule.json>")
        return

    meta_path = sys.argv[1]
    aircraft_path = sys.argv[2]
    trucks_path = sys.argv[3]
    schedule_path = sys.argv[4]

    meta = read_json(meta_path)
    aircraft = read_json(aircraft_path)
    trucks = read_json(trucks_path)
    
    schedule = generate_schedule(meta, aircraft, trucks)
    write_json(schedule_path, schedule)

if __name__ == "__main__":
    main()