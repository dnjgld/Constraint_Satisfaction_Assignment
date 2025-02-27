# indicate any help or reference here

# code starts here
import json
import sys

#######################
### Basic functions ###
#######################

# function to read json file
def read_json(file_path):
    with open(file_path, 'r') as file:
        return json.load(file)

# function to write json file
def write_json(file_path, data):
    with open(file_path, 'w') as file:
        json.dump(data, file, indent=4)

# dict = read_json('data_Format/meta.json')
# write_json('data/test.json', dict)


#######################
## Schedule functions #
#######################
# Variables:
# - Aircraft
# - Truck
# - Forklift
# Domains:
# - Each aircraft, truck, and forklift is assigned a hangar
# - Arrival time and departure time for each aircraft and truck
# - Start time and job for each forklift
# Constraints:
# - Aircraft and trucks must be scheduled within the start and stop times
# - Hangars and forklifts can only be assigned to one aircraft or truck at a time


def generate_schedule(meta, aircraft, trucks):
    # read meta data
    start_time = meta["Start Time"]
    stop_time = meta["Stop Time"]
    hangars = meta["Hangars"]
    forklifts = meta["Forklifts"]

    # initialize schedule
    schedule = {
        "aircraft": {},
        "trucks": {},
        "forklifts": {},
    }

    # code to generate schedule

    return schedule


#######################
### Main functions ####
#######################

def main():
    # check if the number of arguments is correct
    if len(sys.argv) != 5:
        print("5 arguments are required: meta_path, aircraft_path, trucks_path, schedule_path")
        return

    meta_path = sys.argv[1]
    aircraft_path = sys.argv[2]
    trucks_path = sys.argv[3]
    schedule_path = sys.argv[4]

    # read input json files
    meta = read_json(meta_path)
    aircraft = read_json(aircraft_path)
    trucks = read_json(trucks_path)
    
    # automatically generate schedule
    schedule = generate_schedule(meta, aircraft, trucks)

    # store schedule in json file
    write_json(schedule_path, schedule)

if __name__ == "__main__":
    main()
