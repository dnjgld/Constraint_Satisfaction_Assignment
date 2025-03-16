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
    #       departure time - arrival time = 20 + 5*n // at least 20 minutes to unload cargo
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

def backtracking(unassign_variables, domains, assignments, aircraft_names, truck_name, forklifts_tasks):
    # if all variables are assigned, return the assignments
    if unassign_variables == []:
        return assignments
    
    # unassigned_num = len(unassign_variables)
    # total = len(domains.keys())
    # print(f"Assigned variables: {total - unassigned_num}/{total}")

    # if not, select the first unassigned variable
    var = unassign_variables[0]

    # assign possible value in the domain to the variable
    for value in domains[var]:
        # create a new assignment to avoid modifying the original assignment
        new_assignments = assignments.copy()
        new_assignments[var] = value

        # check if the new assignment satisfies the constraints 
        if check_constraints(new_assignments, aircraft_names, truck_name, forklifts_tasks):
            # if the assignment is valid, recursively assign the next variable
            result = backtracking(unassign_variables[1:], domains, new_assignments, aircraft_names, truck_name, forklifts_tasks)
            if result:
                return result
        # if the assignment is invalid, try the next value in the domain
    
    # if no assignment is valid, return None
    return None

def check_constraints(assignment, aircraft_names, truck_name, forklifts_tasks):
    aircraft_assignment = []
    truck_assignment = []
    forklift_assignment = []

    for variable in assignment.keys():
        if variable in aircraft_names:
            aircraft_assignment.append(assignment[variable])
        elif variable in truck_name:
            truck_assignment.append(assignment[variable])
        elif variable in forklifts_tasks:
            forklift_assignment.append(assignment[variable])

    # constraint1: the hanger cannot be assigned to more than one aircraft at the same time
    for i in range(len(aircraft_assignment)):
        for j in range(i + 1, len(aircraft_assignment)):
            # if two aircrafts assigned to the same hanger have overlapping time, return False
            if aircraft_assignment[i][0] == aircraft_assignment[j][0]:
                # one aircraft arrives before the other leaves
                if aircraft_assignment[i][2] > aircraft_assignment[j][1] and aircraft_assignment[i][2] <= aircraft_assignment[j][2]:
                    return False
                if aircraft_assignment[j][2] > aircraft_assignment[i][1] and aircraft_assignment[j][2] < aircraft_assignment[i][2]:
                    return False
                
    # constraint2: the hanger cannot be assigned to more than one truck at the same time
    for i in range(len(truck_assignment)):
        for j in range(i + 1, len(truck_assignment)):
            # if two trucks assigned to the same hanger have overlapping time, return False
            if truck_assignment[i][0] == truck_assignment[j][0]:
                # one truck arrives before the other leaves
                if truck_assignment[i][2] > truck_assignment[j][1] and truck_assignment[i][2] <= truck_assignment[j][2]:
                    return False
                if truck_assignment[j][2] > truck_assignment[i][1] and truck_assignment[j][2] <= truck_assignment[i][2]:
                    return False
                
    # constraint3: the forklift cannot be assigned to more than one task at the same time
    for i in range(len(forklift_assignment)):
        for j in range(i + 1, len(forklift_assignment)):
            # if two tasks uses the same forklift have overlapping time, return False
            if forklift_assignment[i][0] == forklift_assignment[j][0]:
                if forklift_assignment[i][4] == "Load":
                    duration = 5
                else:
                    duration = 20

                if forklift_assignment[i][3] <= forklift_assignment[j][3] and forklift_assignment[i][3] + duration > forklift_assignment[j][3]:
                    return False
                if forklift_assignment[j][3] <= forklift_assignment[i][3] and forklift_assignment[j][3] + duration > forklift_assignment[i][3]:
                    return False
    
    # constraint4: the forklift unload tasks should be assigned after the aircraft arrives and the load tasks should be assigned when the truck arrives
    assigned_truck = []
    for task in forklift_assignment:
        if task[4] == "Unload":
            fl, aircraft, h, time, job = task
            if aircraft in aircraft_names:
                if h != assignment[aircraft][0]:
                    return False
                if not (assignment[aircraft][1] <= time < assignment[aircraft][2]):
                    return False
            else:
                return False
        else:
            fl, truck, h, time, job = task
            if truck in truck_name:
                if truck in assigned_truck:
                    return False
                assigned_truck.append(truck)
                
                if h != assignment[truck][0]:
                    return False
                
                if not (assignment[truck][1] <= time < assignment[truck][2]):
                    return False
            else:
                return False
    
    # constraint5: ensure unload tasks are completed before load tasks
    for variable in assignment.keys():
        if re.search(r"_unload_", variable):
            fl, aircraft, hangar1, time1, job = assignment[variable]
            load_task = f"{aircraft}_load_{variable.split('_')[-1]}"
            if load_task in assignment:
                _, _, hangar2, time2, _ = assignment[load_task]
                if time1 + 20 > time2:
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