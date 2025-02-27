# Air Cargo Terminal Scheduler

## 项目结构
- src/: 源代码
- tests/: 测试代码
- data/: 输入数据文件

## 使用方法
1. 运行测试:
```bash
python -m tests.test_scheduler
```

2. 运行调度器:
```bash
python terminalScheduler.py data/meta.json data/aircraft.json data/trucks.json output/schedule.json
```

## Overview
This project implements a scheduler that runs from `terminalScheduler.py`. The scheduler processes input data from JSON files and generates a schedule, which is also saved as a JSON file.

## Requirements
- Python 3.x
- Required libraries: `json`, `sys`

## Usage
The `terminalScheduler.py` script requires four command-line arguments in the following order:
1. `meta_path` - Path to the `meta.json` file
2. `aircraft_path` - Path to the `aircraft.json` file
3. `trucks_path` - Path to the `trucks.json` file
4. `schedule_path` - Path for the output `schedule.json` file

### Command
```sh
python terminalScheduler.py META_PATH AIRCRAFT_PATH TRUCKS_PATH SCHEDULE_PATH