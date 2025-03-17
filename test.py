import json
import time
from terminalScheduler import generate_schedule, read_json

def test_generate_schedule():
    for i in range(1, 5):
        meta_path = f"test{i}_passes/meta.json"
        aircraft_path = f"test{i}_passes/aircraft.json"
        trucks_path = f"test{i}_passes/trucks.json"
        expected_schedule_path = f"test{i}_passes/schedule.json"
        meta = read_json(meta_path)
        aircraft = read_json(aircraft_path)
        trucks = read_json(trucks_path)
        expected_schedule = read_json(expected_schedule_path)

        start_time = time.time()  # Start time
        schedule = generate_schedule(meta, aircraft, trucks)
        end_time = time.time()  # End time
        elapsed_time = end_time - start_time  # Elapsed time

        if schedule == expected_schedule:
            print(f"Test {i} passed! Time taken: {elapsed_time:.2f} seconds")
        else:
            print(f"Test {i} failed! Time taken: {elapsed_time:.2f} seconds")
            print("Expected:")
            print(json.dumps(expected_schedule, indent=4))
            print("Got:")
            print(json.dumps(schedule, indent=4))
    
    # meta_path = f"test5_fails/meta.json"
    # aircraft_path = f"test5_fails/aircraft.json"
    # trucks_path = f"test5_fails/trucks.json"
    # expected_schedule_path = f"test5_fails/schedule.json"
    # meta = read_json(meta_path)
    # aircraft = read_json(aircraft_path)
    # trucks = read_json(trucks_path)
    # expected_schedule = read_json(expected_schedule_path)

    # schedule = generate_schedule(meta, aircraft, trucks)

    # if schedule == expected_schedule:
    #     print("Test passed!")
    # else:
    #     print("Test failed!")
    #     print("Expected:")
    #     print(json.dumps(expected_schedule, indent=4))
    #     print("Got:")
    #     print(json.dumps(schedule, indent=4))


if __name__ == "__main__":
    test_generate_schedule()