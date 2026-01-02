import time


class InstrumentMockAPI:
    """模拟智能检测仪器的后端接口 (Mock Service)"""

    # 预定义数据场景
    _DATA_STORE = {
        "DEV-2026-A": {
            "component_id": "KL-3-15 (框架梁)",
            "design_strength": "C35",
            "avg_rebound_value": 36.0,
            "carbonation_depth": 1.0,
            "description": "场景：刚好合格",
        },
        "DEV-2026-B": {
            "component_id": "KZ-1-02 (框架柱)",
            "design_strength": "C35",
            "avg_rebound_value": 30.0,
            "carbonation_depth": 0.0,
            "description": "场景：严重不合格",
        },
        "DEV-2026-C": {
            "component_id": "Q-2-05 (剪力墙)",
            "design_strength": "C30",
            "avg_rebound_value": 38.0,
            "carbonation_depth": 1.5,
            "description": "场景：高强且合格",
        },
    }

    @classmethod
    def fetch_latest_record(cls, device_id: str):
        """模拟网络请求，获取单条记录"""
        time.sleep(0.5)
        record = cls._DATA_STORE.get(device_id)
        if not record:
            return {"status": "error", "message": "Device not found"}

        return {
            "status": "success",
            "timestamp": "2026-05-20T10:30:00",
            "device_id": device_id,
            "data": {"project_name": "宁波轨道交通X号线", "is_pumped": True, **record},
        }

    @classmethod
    def get_all_scenarios(cls):
        """[新增] 获取所有模拟场景数据"""
        return cls._DATA_STORE
