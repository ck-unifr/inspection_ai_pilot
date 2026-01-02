from langchain.tools import tool
from src.services.mock_api import InstrumentMockAPI
from src.services.rag_service import KnowledgeBaseService

# 初始化 RAG 服务 (单例模式建议)
kb_service = KnowledgeBaseService()

@tool
def get_instrument_data(device_id: str):
    """
    连接现场智能回弹仪，获取最新的检测数据。
    参数 device_id: 仪器编号 (例如: 'DEV-001')
    """
    api = InstrumentMockAPI()
    return api.fetch_latest_record(device_id)

@tool
def search_standard_knowledge(query: str):
    """
    查阅《混凝土检测技术规程》等标准知识库。
    当需要查询具体的换算表格、强度计算规则、合规性判断依据时使用此工具。
    参数 query: 具体的查询问题 (例如: '回弹值36.0碳化1.0对应的强度是多少')
    """
    # 这里复用 RAG 检索逻辑
    return kb_service.query(query)