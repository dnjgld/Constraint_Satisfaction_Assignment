"""
Core scheduler implementation
"""

import json
import logging
from typing import Dict
from .utils import round_to_5, load_json

# 设置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TerminalScheduler:
    def __init__(self, meta_path: str, aircraft_path: str, trucks_path: str):
        # 读取输入文件
        self.meta_data = load_json(meta_path)
        self.aircraft_data = load_json(aircraft_path) 
        self.trucks_data = load_json(trucks_path)
        
        # 初始化时间范围
        self.start_time = self.meta_data["Start Time"]
        self.stop_time = self.meta_data["Stop Time"]
        
        # 获取可用资源
        self.hangars = self.meta_data["Hangars"]
        self.forklifts = self.meta_data["Forklifts"]
        
        # 初始化调度结果
        self.schedule = {
            "aircraft": {},
            "trucks": {},
            "forklifts": {forklift: [] for forklift in self.forklifts}
        }
        
        # 初始化机库货物跟踪
        self.hangar_cargo = {hangar: [] for hangar in self.hangars}

    def _is_hangar_available(self, hangar: str, start_time: int, end_time: int) -> bool:
        """检查机库在指定时间段是否可用"""
        # 检查飞机占用
        for aircraft in self.schedule["aircraft"].values():
            if aircraft["Hangar"] == hangar:
                if not (end_time <= aircraft["Arrival"] or start_time >= aircraft["Departure"]):
                    return False
        
        # 检查卡车占用
        for truck in self.schedule["trucks"].values():
            if truck["Hangar"] == hangar:
                if not (end_time <= truck["Arrival"] or start_time >= truck["Departure"]):
                    return False
        
        return True

    def _track_cargo(self):
        """跟踪每个机库的货物情况"""
        self.hangar_cargo = {hangar: [] for hangar in self.hangars}
        
        # 记录卸货产生的货物
        for aircraft_id, aircraft in self.schedule["aircraft"].items():
            cargo_count = self.aircraft_data[aircraft_id]["Cargo"]
            hangar = aircraft["Hangar"]
            self.hangar_cargo[hangar].extend([aircraft["Departure"]] * cargo_count)
        
        # 按时间排序
        for cargo_list in self.hangar_cargo.values():
            cargo_list.sort()

    def _schedule_aircraft(self) -> bool:
        """安排飞机调度"""
        sorted_aircraft = sorted(self.aircraft_data.items(), key=lambda x: x[1]["Time"])
        
        for aircraft_id, aircraft_info in sorted_aircraft:
            logger.info(f"Scheduling aircraft {aircraft_id}")
            arrival_time = aircraft_info["Time"]
            cargo_count = aircraft_info["Cargo"]
            
            # 计算卸货时间(每个货物20分钟)
            unload_duration = cargo_count * 20
            
            scheduled = False
            for hangar in self.hangars:
                current_time = round_to_5(arrival_time)
                
                while current_time + unload_duration <= self.stop_time:
                    if self._is_hangar_available(hangar, current_time, current_time + unload_duration):
                        if self._schedule_forklifts(hangar, current_time, "Unload", unload_duration):
                            self.schedule["aircraft"][aircraft_id] = {
                                "Hangar": hangar,
                                "Arrival": current_time,
                                "Departure": current_time + unload_duration
                            }
                            scheduled = True
                            break
                    current_time += 5
                
                if scheduled:
                    break
                    
            if not scheduled:
                return False
                
        return True

    def _schedule_trucks(self) -> bool:
        """安排卡车调度"""
        self._track_cargo()
        sorted_trucks = sorted(self.trucks_data.items(), key=lambda x: x[1])
        total_cargo = sum(aircraft["Cargo"] for aircraft in self.aircraft_data.values())
        scheduled_cargo = 0
        
        for truck_id, arrival_time in sorted_trucks:
            logger.info(f"Scheduling truck {truck_id}")
            scheduled = False
            
            for hangar in self.hangars:
                current_time = max(round_to_5(arrival_time), 
                                 self._get_earliest_cargo_available_time(hangar))
                
                while current_time + 5 <= self.stop_time:
                    if (self._is_hangar_available(hangar, current_time, current_time + 5) and 
                        self._get_available_cargo(hangar, current_time)):
                        if self._schedule_forklifts(hangar, current_time, "Load", 5):
                            self.schedule["trucks"][truck_id] = {
                                "Hangar": hangar,
                                "Arrival": current_time,
                                "Departure": current_time + 5
                            }
                            self.hangar_cargo[hangar].pop(0)
                            scheduled = True
                            scheduled_cargo += 1
                            break
                    current_time += 5
                    
                if scheduled:
                    break
                    
            if not scheduled:
                return False
                
        return scheduled_cargo == total_cargo

    def solve(self) -> Dict:
        """解决调度问题"""
        if not self._schedule_aircraft():
            return {
                "aircraft": None,
                "trucks": None,
                "forklifts": None
            }
            
        if not self._schedule_trucks():
            return {
                "aircraft": None,
                "trucks": None,
                "forklifts": None
            }
            
        return self.schedule

    def _get_earliest_cargo_available_time(self, hangar: str) -> int:
        """获取指定机库最早可用的货物时间"""
        earliest_time = self.stop_time
        
        for aircraft in self.schedule["aircraft"].values():
            if aircraft["Hangar"] == hangar:
                earliest_time = min(earliest_time, aircraft["Arrival"])
            
        return earliest_time

    def _get_available_cargo(self, hangar: str, time: int) -> bool:
        """检查指定时间点是否有可用货物"""
        if hangar not in self.hangar_cargo:
            return False
        return any(cargo_time <= time for cargo_time in self.hangar_cargo[hangar])

    def _schedule_forklifts(self, hangar: str, start_time: int, job_type: str, duration: int) -> bool:
        """安排叉车调度"""
        # 计算需要的叉车数量
        forklifts_needed = 1 if job_type == "Load" else (duration // 20)
        available_forklifts = []
        
        # 检查每个叉车的可用性
        for forklift_id in self.forklifts:
            if self._is_forklift_available(forklift_id, hangar, start_time, 
                                         start_time + (20 if job_type == "Unload" else 5)):
                available_forklifts.append(forklift_id)
            
        if len(available_forklifts) < forklifts_needed:
            return False
        
        # 分配任务给叉车
        for i in range(forklifts_needed):
            self.schedule["forklifts"][available_forklifts[i]].append({
                "Hangar": hangar,
                "Time": start_time,
                "Job": job_type
            })
        
        return True

    def _is_forklift_available(self, forklift_id: str, hangar: str, 
                              start_time: int, end_time: int) -> bool:
        """检查叉车在指定时间段是否可用"""
        for task in self.schedule["forklifts"][forklift_id]:
            task_duration = 20 if task["Job"] == "Unload" else 5
            task_end = task["Time"] + task_duration
            
            if not (end_time <= task["Time"] or start_time >= task_end):
                return False
        return True

    def _round_to_5(self, time: int) -> int:
        """将时间舍入到最近的5分钟"""
        return ((time + 2) // 5) * 5

    # ... (其他方法保持不变) ... 