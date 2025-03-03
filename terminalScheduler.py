# I collaborate with Jiaying He on this assignment.
# We watched the video "Constraint-Satisfaction Problems in Python" on youtube to learn the backtracking algorithm solution.
# I also watched the video: "Constraint Satisfaction the AC-3 algorithm" but not used in this assignment

from copy import deepcopy
import json
import sys

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
    """Convert time in HHMM format to minutes since midnight."""
    hours = time // 100
    minutes = time % 100
    return hours * 60 + minutes

def minutes_to_time(minutes):
    """Convert minutes since midnight to time in HHMM format."""
    hours = minutes // 60
    minutes = minutes % 60
    return hours * 100 + minutes

# a class to store the schedule information
class Schedule:
    def __init__(self, aircraft=None, hangars=None, forklifts=None):
        self.aircraft = aircraft
        self.aircraft_schedule = {}
        self.truck_schedule = {}
        self.forklift_assignments = {fl: [] for fl in (forklifts or [])}
        self.hangar_planes = {hangar: [] for hangar in (hangars or [])}
        self.hangar_trucks = {hangar: [] for hangar in (hangars or [])}
        self.cargo_count = {hangar: 0 for hangar in (hangars or [])}

    def clone(self):
        copy_schedule = Schedule()
        copy_schedule.aircraft = deepcopy(self.aircraft)
        copy_schedule.aircraft_schedule = deepcopy(self.aircraft_schedule)
        copy_schedule.truck_schedule = deepcopy(self.truck_schedule)
        copy_schedule.forklift_assignments = deepcopy(self.forklift_assignments)
        copy_schedule.hangar_planes = deepcopy(self.hangar_planes)
        copy_schedule.hangar_trucks = deepcopy(self.hangar_trucks)
        copy_schedule.cargo_count = deepcopy(self.cargo_count)
        return copy_schedule
    
#######################
## Schedule functions #
#######################

# first schedule the aircrafts, 
# if successful, schedule the trucks
def schedule_aircraft(schedule, aircraft_idx, aircraft, trucks, hangars, forklifts, stop_time):
    if aircraft_idx >= len(aircraft):
        return schedule_trucks(schedule, 0, trucks, hangars, forklifts, stop_time)
    ac_name, ac_info = aircraft[aircraft_idx]
    ac_time = time_to_minutes(ac_info['Time'])
    ac_cargo = ac_info['Cargo']

    for hangar in hangars:
        planes = schedule.hangar_planes[hangar]
        last_departure = planes[-1]['Departure Time'] if planes else 0
        last_departure = time_to_minutes(last_departure)
        for arrival_time in range(max(ac_time, last_departure), time_to_minutes(stop_time) + 1, 5):
            arrival_time = round_to_nearest_five(arrival_time)
            new_schedule = schedule.clone()
            duration = 20 * ac_cargo
            required_time = duration
            departure_time = arrival_time + required_time
            if departure_time > time_to_minutes(stop_time):
                continue
            new_schedule.hangar_planes[hangar].append({
                'Arrival Time': minutes_to_time(arrival_time),
                'Departure Time': minutes_to_time(departure_time),
                'Cargo': ac_cargo
            })
            new_schedule.aircraft_schedule[ac_name] = {
                'Hangar': hangar,
                'Arrival Time': minutes_to_time(arrival_time),
                'Departure Time': minutes_to_time(departure_time)
            }
            new_schedule.cargo_count[hangar] += ac_cargo
            result = schedule_aircraft(new_schedule, aircraft_idx + 1, aircraft, trucks, hangars, forklifts, stop_time)
            if result:
                return result
    return None

# then schedule the trucks
# if successful, check and assign forklifts
def schedule_trucks(schedule, truck_idx, trucks, hangars, forklifts, stop_time):
    if truck_idx >= len(trucks):
        return check_and_assign_forklifts(schedule, hangars, forklifts)
    truck_name, truck_arrival = trucks[truck_idx]
    truck_arrival = time_to_minutes(truck_arrival)

    for hangar in hangars:
        required_cargo = schedule.cargo_count[hangar]
        current_trucks = len([t for t in schedule.truck_schedule.values() if t['Hangar'] == hangar])
        if current_trucks >= required_cargo:
            continue
        new_schedule = schedule.clone()
        trucks_in_hangar = new_schedule.hangar_trucks[hangar]
        last_departure = trucks_in_hangar[-1]['Departure Time'] if trucks_in_hangar else 0
        last_departure = time_to_minutes(last_departure)
        earliest_start = max(truck_arrival, last_departure)
        arrival_time = round_to_nearest_five(earliest_start)
        departure_time = arrival_time + 5
        if departure_time > time_to_minutes(stop_time):
            continue
        new_schedule.hangar_trucks[hangar].append({
            'Arrival Time': minutes_to_time(arrival_time),
            'Departure Time': minutes_to_time(departure_time)
        })
        new_schedule.truck_schedule[truck_name] = {
            'Hangar': hangar,
            'Arrival Time': minutes_to_time(arrival_time),
            'Departure Time': minutes_to_time(departure_time)
        }
        result = schedule_trucks(new_schedule, truck_idx + 1, trucks, hangars, forklifts, stop_time)
        if result:
            return result
    return None

# check and assign forklifts
def check_and_assign_forklifts(schedule, hangars, forklifts):
    for hangar in hangars:
        required = schedule.cargo_count[hangar]
        scheduled = len([t for t in schedule.truck_schedule.values() if t['Hangar'] == hangar])
        if required != scheduled:
            return None

    forklift_tasks = {fl: [] for fl in forklifts}
    for ac_name, ac in schedule.aircraft_schedule.items():
        hangar = ac['Hangar']
        start = time_to_minutes(ac['Arrival Time'])
        end = time_to_minutes(ac['Departure Time'])
        cargo = schedule.aircraft[ac_name]['Cargo']
        for _ in range(cargo):
            scheduled = False
            for fl in forklifts:
                if can_schedule_forklift(forklift_tasks[fl], start, start + 20):
                    forklift_tasks[fl].append({'Start': start, 'End': start + 20, 'Hangar': hangar, 'Type': 'unload'})
                    scheduled = True
                    break
            if not scheduled:
                return None

    for truck_name, truck in schedule.truck_schedule.items():
        hangar = truck['Hangar']
        start = time_to_minutes(truck['Arrival Time'])
        end = start + 5
        for fl in forklifts:
            if can_schedule_forklift(forklift_tasks[fl], start, end):
                forklift_tasks[fl].append({'Start': start, 'End': end, 'Hangar': hangar, 'Type': 'load'})
                break
        else:
            return None

    final_schedule = schedule.clone()
    for fl in forklifts:
        final_schedule.forklift_assignments[fl] = sorted(forklift_tasks[fl], key=lambda x: x['Start'])
    return final_schedule

# check if a forklift can be scheduled
def can_schedule_forklift(assignments, start, end):
    for task in assignments:
        task_start = task['Start']
        task_end = task['End']
        if not (end <= task_start or start >= task_end):
            return False
    return True

# main function to generate the schedule
def generate_schedule(meta, aircraft, trucks):
    start_time = meta['Start Time']
    stop_time = meta['Stop Time']
    hangars = meta['Hangars']
    forklifts = meta['Forklifts']

    sorted_aircraft = sorted(aircraft.items(), key=lambda x: x[1]['Time'])
    sorted_trucks = sorted(trucks.items(), key=lambda x: x[1])

    initial_schedule = Schedule(aircraft, hangars, forklifts)
    
    solution = schedule_aircraft(initial_schedule, 0, sorted_aircraft, sorted_trucks, hangars, forklifts, stop_time)
    if solution:
        output = {
            'aircraft': {},
            'trucks': {},
            'forklifts': {}
        }
        for ac, details in solution.aircraft_schedule.items():
            output['aircraft'][ac] = {
                'Hangar': details['Hangar'],
                'Arrival Time': details['Arrival Time'],
                'Departure Time': details['Departure Time']
            }
        for truck, details in solution.truck_schedule.items():
            output['trucks'][truck] = {
                'Hangar': details['Hangar'],
                'Arrival Time': details['Arrival Time'],
                'Departure Time': details['Departure Time']
            }
        for fl, tasks in solution.forklift_assignments.items():
            output['forklifts'][fl] = []
            for task in tasks:
                output['forklifts'][fl].append({
                    'Hangar': task['Hangar'],
                    'Start': minutes_to_time(task['Start']),
                    'End': minutes_to_time(task['End']),
                    'Type': task['Type']
                })
        return output
    else:
        return {
            "aircraft": None,
            "trucks": None,
            "forklifts": None
        }

#######################
### Main functions ####
#######################

def main():
    if len(sys.argv) != 5:
        print("5 arguments are required: meta_path, aircraft_path, trucks_path, schedule_path")
        return

    meta_path = sys.argv[1]
    aircraft_path = sys.argv[2]
    trucks_path = sys.argv[3]
    schedule_path = sys.argv[4]

    meta = read_json(meta_path)
    aircraft = read_json(aircraft_path)
    trucks = read_json(trucks_path)
    
    schedule = generate_schedule(meta, aircraft, trucks)
    if schedule is None:
        print("Failed to generate a valid schedule.")
    else:
        write_json(schedule_path, schedule)

if __name__ == "__main__":
    main()