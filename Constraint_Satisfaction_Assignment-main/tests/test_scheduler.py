"""
Test cases for the scheduler
"""

import json
import os
from src.scheduler import TerminalScheduler

def test_simple_case():
    """测试简单情况"""
    meta = {
        "Start Time": 730,
        "Stop Time": 1100,
        "Hangars": ["H1"],
        "Forklifts": ["F1"]
    }
    aircraft = {
        "A1": {"Time": 800, "Cargo": 1}
    }
    trucks = {
        "T1": 830
    }
    
    # 创建测试文件
    with open("test_meta.json", "w") as f:
        json.dump(meta, f)
    with open("test_aircraft.json", "w") as f:
        json.dump(aircraft, f)
    with open("test_trucks.json", "w") as f:
        json.dump(trucks, f)
        
    scheduler = TerminalScheduler("test_meta.json", "test_aircraft.json", "test_trucks.json")
    solution = scheduler.solve()
    
    # 验证结果
    assert solution["aircraft"] is not None
    assert solution["trucks"] is not None
    assert solution["forklifts"] is not None
    
    print("简单情况测试通过！")

def test_multiple_aircraft_trucks():
    """测试多飞机多卡车情况"""
    # ... (原来的测试代码) ...

def test_edge_cases():
    """测试边界情况"""
    # ... (原来的测试代码) ...

def run_all_tests():
    """运行所有测试"""
    test_simple_case()
    test_multiple_aircraft_trucks()
    test_edge_cases()
    print("所有测试通过！")

if __name__ == "__main__":
    run_all_tests() 