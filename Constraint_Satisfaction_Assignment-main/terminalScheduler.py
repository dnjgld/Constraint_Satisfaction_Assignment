"""
Terminal Scheduler for Air Cargo Operations
Main entry point for the scheduling system
"""

import sys
import json
from src.scheduler import TerminalScheduler

def main():
    if len(sys.argv) != 5:
        print("Usage: python terminalScheduler.py META_PATH AIRCRAFT_PATH TRUCKS_PATH SCHEDULE_PATH")
        sys.exit(1)
        
    meta_path = sys.argv[1]
    aircraft_path = sys.argv[2]
    trucks_path = sys.argv[3]
    schedule_path = sys.argv[4]
    
    # 创建调度器实例
    scheduler = TerminalScheduler(meta_path, aircraft_path, trucks_path)
    
    # 解决调度问题
    solution = scheduler.solve()
    
    # 输出结果
    with open(schedule_path, 'w') as f:
        json.dump(solution, f, indent=4)

if __name__ == "__main__":
    if len(sys.argv) == 2 and sys.argv[1] == "--test":
        from tests.test_scheduler import run_all_tests
        run_all_tests()
    else:
        main()