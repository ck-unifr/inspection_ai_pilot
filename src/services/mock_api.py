import time
import random

class InstrumentMockAPI:
    """模拟智能检测仪器的后端接口"""
    
    @staticmethod
    def fetch_latest_record(device_id: str):
        """
        模拟网络请求，获取最新一条检测记录
        """
        # 模拟网络延迟
        time.sleep(1)
        
        # 模拟数据库返回的 JSON 数据
        # 场景：一根梁的检测数据
        return {
            "status": "success",
            "timestamp": "2026-05-20T10:30:00",
            "device_id": device_id,
            "data": {
                "project_name": "宁波轨道交通X号线",
                "component_id": "KL-3-15 (框架梁)",
                "design_strength": "C35",      # 设计强度
                "is_pumped": True,             # 是否泵送
                "avg_rebound_value": 36.2,     # 平均回弹值
                "carbonation_depth": 1.0       # 碳化深度
            }
        }