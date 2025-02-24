"""
Utility functions for the scheduler
"""

import json
import sys
import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

def load_json(path: str) -> dict:
    """加载JSON文件"""
    try:
        with open(path, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        logger.error(f"找不到文件: {path}")
        sys.exit(1)
    except json.JSONDecodeError:
        logger.error(f"JSON文件格式错误: {path}")
        sys.exit(1)

def round_to_5(time: int) -> int:
    """将时间舍入到最近的5分钟"""
    return ((time + 2) // 5) * 5

def validate_schedule(schedule: Dict[str, Any], meta_data: Dict[str, Any]) -> bool:
    """验证调度结果是否有效"""
    # TODO: 实现调度验证逻辑
    return True 