# I collaborate with Jiaying He on this assignment.
# We watched the video "Constraint-Satisfaction Problems in Python" on youtube to learn the backtracking algorithm solution.
# I also watched the video: "Constraint Satisfaction the AC-3 algorithm" but not used in this assignment

from copy import deepcopy
import json
import sys
import math

#######################
### Basic functions ###
#######################

def read_json(file_path):
    with open(file_path, 'r') as file:
        return json.load(file)

def write_json(file_path, data):
    with open(file_path, 'w') as file:
        json.dump(data, file, indent=4)

def round_to_nearest_five(minutes):
    return 5 * round(minutes / 5)

def time_to_minutes(time):
    hours = time // 100
    minutes = time % 100
    return hours * 60 + minutes

def minutes_to_time(minutes_m):
    hours = minutes_m // 60
    minutes = minutes_m % 60
    return hours * 100 + minutes

class Constraint():
    def __init__(self, variables):
        self.variables = variables

    def satisfied(self, assignment):
        raise NotImplementedError("Not implemented")

class AircraftConstraint(Constraint):
    def __init__(self, aircraft, arrival_time, cargo_number, stop_time):
        super().__init__([aircraft])
        self.aircraft = aircraft
        self.arrival_time = arrival_time
        self.stop_time = stop_time
        self.cargo_number = cargo_number

    def satisfied(self, assignment):
        if self.aircraft not in assignment:
            return True
        hangar, arrival_hangar_time, departure_time = assignment[self.aircraft]

        # constraint 1: arrival time at hangar must be >= arrival time at terminal
        if arrival_hangar_time < self.arrival_time:
            return False
        # constraint 2: the duration must be no less than 20 minutes
        if departure_time - arrival_hangar_time < 20:
            return False
        # constraint 3: check hangar occupation conflict
        for other_ac in assignment:
            if other_ac == self.aircraft:
                continue
            other_hangar, other_arrival, other_departure = assignment[other_ac]
            if other_hangar == hangar and not (departure_time <= other_arrival or arrival_hangar_time >= other_departure):
                return False
        return True

class TruckConstraint(Constraint):
    def __init__(self, truck, arrival_time):
        super().__init__([truck])
        self.truck = truck
        self.arrival_time = arrival_time

    def satisfied(self, assignment):
        if self.truck not in assignment:
            return True
        hangar, truck_arrival_hangar, departure = assignment[self.truck]
        
        # constraint 1: arrival time at hangar must be >= arrival time at terminal
        if truck_arrival_hangar < self.arrival_time:
            return False
        # constraint 2: departure time must be 5 minutes after arrival time
        if departure != truck_arrival_hangar + 5:
            return False
        # constraint 3: check hangar occupation conflict
        for other_truck in assignment:
            if other_truck == self.truck:
                continue
            other_hangar, other_arrival, other_departure = assignment[other_truck]
            if other_hangar == hangar and not (departure <= other_arrival or truck_arrival_hangar >= other_departure):
                return False
        return True

class ForkliftTaskConstraint(Constraint):
    def __init__(self, task_id):
        super().__init__([task_id])
        self.task_id = task_id

    def satisfied(self, assignment):
        if self.task_id not in assignment:
            return True
        fl_name, ac_name, truck_name, task_hangar, time, job = assignment[self.task_id]

        # if the task is unloading the aircraft, then the aircraft must be assigned
        if job == "Unload":
            if ac_name not in assignment:
                return False
            ac_hangar, ac_arrival, ac_departure = assignment[ac_name]
            # the hangar must be the same
            if task_hangar != ac_hangar:
                return False
            if not (ac_arrival <= time < ac_departure):
                return False
            # Ensure there is a corresponding load task after this unload task
            load_task_id = f"{ac_name}_load_{self.task_id.split('_')[-1]}"
            if load_task_id not in assignment:
                return True
            # Ensure the load task is completed after this unload task
            _, _, _, correspond_hangar, load_time, _ = assignment[unload_task_id]
            if load_time <= time:
                return False
            if correspond_hangar != task_hangar:
                return False


        # if the task is loading, then the truck must be assigned
        if job == "Load":
            if truck_name not in assignment:
                return False
            t_hangar, t_arrival, t_departure = assignment[truck_name]
            if task_hangar != t_hangar:
                return False
            if not (t_arrival <= time < t_departure):
                return False
            # Ensure there is a corresponding unload task before this load task
            unload_task_id = f"{ac_name}_unload_{self.task_id.split('_')[-1]}"
            if unload_task_id not in assignment:
                return True
            # Ensure the unload task is completed before this load task
            _, _, _, correspond_hangar, unload_time, _ = assignment[unload_task_id]
            if unload_time >= time:
                return False
            if correspond_hangar != task_hangar:
                return False

        return True

# This class ensures that the tasks assigned to the forklifts do not conflict with each other
class ForkliftConflictConstraint(Constraint):
    def __init__(self, task1, task2):
        super().__init__([task1, task2])
        self.task1 = task1
        self.task2 = task2

    def satisfied(self, assignment):
        if self.task1 not in assignment or self.task2 not in assignment:
            return True
        
        fl_name1, _, _, _, time1, job1 = assignment[self.task1]
        fl_name2, _, _, _, time2, job2 = assignment[self.task2]

        # Only check for conflicts if the same forklift is assigned to both tasks
        if fl_name1 != fl_name2:
            return True

        
        # unload task takes 20 minutes, load task takes 5 minutes
        d1 = 20 if job1 == "Unload" else 5 if job1 == "Load" else 0
        d2 = 20 if job2 == "Unload" else 5 if job2 == "Load" else 0

        if not (time1 + d1 <= time2 or time2 + d2 <= time1):
            return False

        return True
    
# CSP class to store the variables, domains and constraints
class CSP():
    def __init__(self, variables, domains, aircraft_arrival):
        self.variables = variables
        self.domains = domains
        self.constraints = {}
        self.aircraft_arrival = aircraft_arrival

        for variable in self.variables:
            self.constraints[variable] = []
            # Check if every variable has a domain assigned to it
            if variable not in self.domains:
                raise LookupError("Every variable should have a domain assigned to it.")

    def add_constraint(self, constraint):
        # Add constraint to all variables in the constraint
        for variable in constraint.variables:
            if variable not in self.variables:
                raise LookupError("Variable in constraint not in CSP")
            else:
                self.constraints[variable].append(constraint)

    def consistent(self, variable, assignment):
        # Check if all constraints of a variable are satisfied
        for constraint in self.constraints[variable]:
            if not constraint.satisfied(assignment):
                return False
        return True

    def backtracking_search(self, assignment={}):

        # check if it is running
        # print(assignment)

        # if assignment is complete then return assignment
        if len(assignment) == len(self.variables):
            return assignment

        # Select the first unassigned variable
        unassigned = [v for v in self.variables if v not in assignment]

        # arrange aircraft by arrival time
        unassigned.sort(key=lambda v: self.aircraft_arrival[v] if v in self.aircraft_arrival else float('inf'))

        first = unassigned[0]
        # Select the first value from the domain of the variable
        for value in self.domains[first]:
            local_assignment = assignment.copy()
            local_assignment[first] = value
            if self.consistent(first, local_assignment):
                result = self.backtracking_search(local_assignment)
                if result is not None:
                    return result
        return None
    

def generate_schedule(meta, aircraft, trucks):
    start_time = time_to_minutes(meta['Start Time'])
    stop_time = time_to_minutes(meta['Stop Time'])
    hangars = meta['Hangars']
    forklifts = meta['Forklifts']

    variables = []
    tasks = []
    domains = {}

    aircraft_arrival = {}
    for ac_name, ac_info in aircraft.items():
        aircraft_arrival[ac_name] = time_to_minutes(ac_info['Time'])

    # Define variables and domains for aircraft
    for ac_name, ac_info in aircraft.items():
        variables.append(ac_name)
        domains[ac_name] = []
        for hangar in hangars:
            for arrival in range(start_time, stop_time - 19, 5):
                for departure in range(arrival + 20, stop_time + 1, 5):
                    domains[ac_name].append((hangar, arrival, departure))

    # Define variables and domains for trucks
    for truck_name, truck_time in trucks.items():
        variables.append(truck_name)
        domains[truck_name] = []
        for hangar in hangars:
            for time in range(start_time, stop_time - 4, 5):
                domains[truck_name].append((hangar, time, time + 5))

    # Define variables and domains for forklift_tasks

    for ac_name, ac_info in aircraft.items():
        for i in range(ac_info['Cargo']):
            task_id1 = f"{ac_name}_unload_{i+1}"
            task_id2 = f"{ac_name}_load_{i+1}"
            variables.append(task_id1)
            variables.append(task_id2)
            tasks.append(task_id1)
            tasks.append(task_id2)

            domains[task_id1] = []
            domains[task_id2] = []
            for hangar in hangars:
                for fl_name in forklifts:
                    for truck_name in trucks:
                        for time in range(start_time, stop_time + 1, 5):
                            domains[task_id1].append((fl_name, ac_name, truck_name, hangar, time, 'Unload'))
                            domains[task_id2].append((fl_name, ac_name, truck_name, hangar, time, 'Load'))

    csp = CSP(variables, domains, aircraft_arrival)

    # Add constraints for aircraft
    for ac_name, ac_info in aircraft.items():
        csp.add_constraint(AircraftConstraint(ac_name, time_to_minutes(ac_info['Time']), ac_info['Cargo'], stop_time))

    # Add constraints for trucks
    for truck_name, truck_time in trucks.items():
        csp.add_constraint(TruckConstraint(truck_name, time_to_minutes(truck_time)))

    # Add constraints for forklifts
    for task_id in tasks:
        csp.add_constraint(ForkliftTaskConstraint(task_id))

    # Add conflict constraints for forklifts
    for i in range(len(tasks)):
        for j in range(i + 1, len(tasks)):
            csp.add_constraint(ForkliftConflictConstraint(tasks[i], tasks[j]))

    solution = csp.backtracking_search()

    if solution:
        output = {
            'aircraft': {},
            'trucks': {},
            'forklifts': {}
        }
        for ac_name in aircraft.keys():
            if ac_name in solution:
                hangar, arrival, departure = solution[ac_name]
                output['aircraft'][ac_name] = {
                    'Hangar': hangar,
                    'Arrival': minutes_to_time(arrival),
                    'Departure': minutes_to_time(departure)
                }
        for truck_name in trucks.keys():
            if truck_name in solution:
                hangar, arrival, departure = solution[truck_name]
                output['trucks'][truck_name] = {
                    'Hangar': hangar,
                    'Arrival': minutes_to_time(arrival),
                    'Departure': minutes_to_time(departure)
                }
        for task_id in tasks:
            if task_id in solution:
                fl_name, ac_name, truck_name, hangar, time, job = solution[task_id]
                if fl_name not in output['forklifts']:
                    output['forklifts'][fl_name] = []
                output['forklifts'][fl_name].append({
                    'Hangar': hangar,
                    'Time': minutes_to_time(time),
                    'Job': job
                })
                
        # Sort forklift tasks by time
        for fl_name in output['forklifts']:
            output['forklifts'][fl_name] = sorted(output['forklifts'][fl_name], key=lambda x: x['Time'])
        
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