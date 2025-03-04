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

def schedule_aircraft(schedule, aircraft_idx, aircraft, trucks, hangars, forklifts, stop_time):
    if aircraft_idx >= len(aircraft):
        return schedule_trucks(schedule, 0, trucks, hangars, forklifts, stop_time)
    
    ac_name, ac_info = aircraft[aircraft_idx]
    ac_time_m = time_to_minutes(ac_info['Time'])
    ac_cargo = ac_info['Cargo']

    # Find the hangar with the earliest available slot
    hangar_options = []
    for hangar in hangars:
        planes = schedule.hangar_planes[hangar]
        last_departure_m = time_to_minutes(planes[-1]['Departure Time']) if planes else 0
        earliest_start_m = max(ac_time_m, last_departure_m)
        hangar_options.append((earliest_start_m, hangar))
    
    # Sort the hangars by earliest available slot
    hangar_options.sort(key=lambda x: x[0])
    for earliest_start_m, hangar in hangar_options:
        max_possible_duration = 20 * ac_cargo
        # My previous solution was fixing the duration to 20 minutes*ac_cargo, but this is not correct
        # Try all possible arrival times and durations
        for arrival_time_m in range(earliest_start_m, time_to_minutes(stop_time) + 1, 5):
            arrival_time_m = round_to_nearest_five(arrival_time_m)
            for duration_m in range(20, max_possible_duration + 1, 5):
                duration_m = round_to_nearest_five(duration_m)
                if duration_m < 20:
                    continue
                departure_time_m = arrival_time_m + duration_m
                if departure_time_m > time_to_minutes(stop_time):
                    continue
                new_schedule = schedule.clone()
                new_schedule.hangar_planes[hangar].append({
                    'Arrival Time': minutes_to_time(arrival_time_m),
                    'Departure Time': minutes_to_time(departure_time_m),
                    'Cargo': ac_cargo
                })
                new_schedule.aircraft_schedule[ac_name] = {
                    'Hangar': hangar,
                    'Arrival Time': minutes_to_time(arrival_time_m),
                    'Departure Time': minutes_to_time(departure_time_m)
                }
                new_schedule.cargo_count[hangar] += ac_cargo
                result = schedule_aircraft(new_schedule, aircraft_idx + 1, aircraft, trucks, hangars, forklifts, stop_time)
                if result:
                    return result
    return None

def schedule_trucks(schedule, truck_idx, trucks, hangars, forklifts, stop_time):
    if truck_idx >= len(trucks):
        return check_and_assign_forklifts(schedule, hangars, forklifts)
    
    truck_name, truck_arrival = trucks[truck_idx]
    truck_arrival_m = time_to_minutes(truck_arrival)

    for hangar in hangars:
        required = schedule.cargo_count[hangar]
        current_trucks = len([t for t in schedule.truck_schedule.values() if t['Hangar'] == hangar])
        if current_trucks >= required:
            continue
        new_schedule = schedule.clone()
        trucks_in_hangar = new_schedule.hangar_trucks[hangar]

        planes_in_hangar = new_schedule.hangar_planes[hangar]
        last_plane_departure_m = max([time_to_minutes(p['Departure Time']) for p in schedule.hangar_planes[hangar]], default=0)
        last_truck_departure_m = max([time_to_minutes(t['Departure Time']) for t in schedule.hangar_trucks[hangar]], default=0)
       
        earliest_start_m = max(truck_arrival_m, last_plane_departure_m, last_truck_departure_m)
        arrival_time_m = round_to_nearest_five(earliest_start_m)
        departure_time_m = arrival_time_m + 5

        if departure_time_m > time_to_minutes(stop_time):
            continue
        new_schedule.hangar_trucks[hangar].append({
            'Arrival Time': minutes_to_time(arrival_time_m),
            'Departure Time': minutes_to_time(departure_time_m)
        })
        new_schedule.truck_schedule[truck_name] = {
            'Hangar': hangar,
            'Arrival Time': minutes_to_time(arrival_time_m),
            'Departure Time': minutes_to_time(departure_time_m)
        }
        result = schedule_trucks(new_schedule, truck_idx + 1, trucks, hangars, forklifts, stop_time)
        if result:
            return result
    return None

def check_and_assign_forklifts(schedule, hangars, forklifts):
    for hangar in hangars:
        required = schedule.cargo_count[hangar]
        scheduled = len([t for t in schedule.truck_schedule.values() if t['Hangar'] == hangar])
        if required != scheduled:
            return None

    forklift_tasks = {fl: [] for fl in forklifts}
    for ac_name, ac in schedule.aircraft_schedule.items():
        hangar = ac['Hangar']
        start_ac_m = time_to_minutes(ac['Arrival Time'])
        end_ac_m = time_to_minutes(ac['Departure Time'])
        cargo = schedule.aircraft[ac_name]['Cargo']
        for _ in range(cargo):
            scheduled = False
            for s in range(start_ac_m, end_ac_m - 20 + 1, 5):
                s = round_to_nearest_five(s)
                e = s + 20
                if e > end_ac_m:
                    continue
                for fl in forklifts:
                    if can_schedule_forklift(forklift_tasks[fl], s, e):
                        forklift_tasks[fl].append({'Start': s, 'End': e, 'Hangar': hangar, 'Type': 'unload'})
                        scheduled = True
                        break
                if scheduled:
                    break
            if not scheduled:
                return None

    for truck_name, truck in schedule.truck_schedule.items():
        hangar = truck['Hangar']
        start_m = time_to_minutes(truck['Arrival Time'])
        end_m = start_m + 5
        scheduled = False
        for fl in forklifts:
            if can_schedule_forklift(forklift_tasks[fl], start_m, end_m):
                forklift_tasks[fl].append({'Start': start_m, 'End': end_m, 'Hangar': hangar, 'Type': 'load'})
                scheduled = True
                break
        if not scheduled:
            return None

    final_schedule = schedule.clone()
    for fl in forklifts:
        final_schedule.forklift_assignments[fl] = sorted(forklift_tasks[fl], key=lambda x: x['Start'])
    return final_schedule

def can_schedule_forklift(assignments, start_m, end_m):
    for task in assignments:
        if not (end_m <= task['Start'] or start_m >= task['End']):
            return False
    return True

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
        for ac_name in aircraft.keys():
            if ac_name in solution.aircraft_schedule:
                details = solution.aircraft_schedule[ac_name]
                output['aircraft'][ac_name] = {
                    'Hangar': details['Hangar'],
                    'Arrival': details['Arrival Time'],
                    'Departure': details['Departure Time']
                }
        for truck_name in trucks.keys():
            if truck_name in solution.truck_schedule:
                details = solution.truck_schedule[truck_name]
                output['trucks'][truck_name] = {
                    'Hangar': details['Hangar'],
                    'Arrival': details['Arrival Time'],
                    'Departure': details['Departure Time']
                }
        for fl, tasks in solution.forklift_assignments.items():
            output['forklifts'][fl] = []
            for task in tasks:
                output['forklifts'][fl].append({
                    'Hangar': task['Hangar'],
                    'Time': minutes_to_time(task['Start']),
                    'Job': 'Unload' if task['Type'] == 'unload' else 'Load'
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