import json
from src.scheduler import TerminalScheduler
from src.utils import load_json

def test_generate_schedule():
    for i in range(1, 5):
        meta_path = f"test{i}_passes/meta.json"
        aircraft_path = f"test{i}_passes/aircraft.json"
        trucks_path = f"test{i}_passes/trucks.json"
        expected_schedule_path = f"test{i}_passes/schedule.json"

        expected_schedule = load_json(expected_schedule_path)
        
        scheduler = TerminalScheduler(meta_path, aircraft_path, trucks_path)
    
        # 解决调度问题
        schedule = scheduler.solve()
    
        # 比较生成的调度和预期结果
        if schedule == expected_schedule:
            print("Test passed!")
        else:
            print("Test failed!")
            # print("Expected:")
            # print(json.dumps(expected_schedule, indent=4))
            # print("Got:")
            # print(json.dumps(schedule, indent=4))
    
    # meta_path = f"test5_fails/meta.json"
    # aircraft_path = f"test5_fails/aircraft.json"
    # trucks_path = f"test5_fails/trucks.json"
    # expected_schedule_path = f"test5_fails/schedule.json"

    # expected_schedule = load_json(expected_schedule_path)

    # scheduler = TerminalScheduler(meta_path, aircraft_path, trucks_path)
    
    # # 解决调度问题
    # schedule = scheduler.solve()

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