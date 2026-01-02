import os
from pathlib import Path
from dotenv import load_dotenv

# 加载 .env 文件
load_dotenv()

class Config:
    # 路径配置
    BASE_DIR = Path(__file__).parent.parent.parent
    DATA_DIR = BASE_DIR / "data"
    DOCS_DIR = DATA_DIR / "docs"
    VECTOR_DB_DIR = DATA_DIR / "vector_db"
    
    # 模型配置 (这里适配 Qwen/DashScope)
    # 建议申请阿里云 DashScope API Key (免费额度高)
    DASHSCOPE_API_KEY = os.getenv("DASHSCOPE_API_KEY")
    
    # 也可以用 OpenAI 格式调用本地 Ollama
    MODEL_NAME = "qwen-turbo"  # 或 qwen-plus, qwen-max
    
    # 向量模型配置 (使用中文效果好的轻量模型)
    EMBEDDING_MODEL = "BAAI/bge-small-zh-v1.5"
    
    # RAG 参数
    CHUNK_SIZE = 500    # 每个切片的大小
    CHUNK_OVERLAP = 50  # 切片重叠部分
    TOP_K = 3           # 检索最相关的3个片段

# 自动创建目录
Config.DOCS_DIR.mkdir(parents=True, exist_ok=True)
Config.VECTOR_DB_DIR.mkdir(parents=True, exist_ok=True)