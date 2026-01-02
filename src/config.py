# src/config.py
import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()


class Config:
    # --- 1. 基础路径配置 ---
    BASE_DIR = Path(__file__).parent.parent
    DATA_DIR = BASE_DIR / "data"
    DOCS_DIR = DATA_DIR / "docs"
    VECTOR_DB_DIR = DATA_DIR / "vector_db"
    MODEL_DIR = DATA_DIR / "models"  # 新增模型目录

    # --- 2. LLM 模型配置 (修复报错的关键) ---
    # 这里适配 Qwen/DashScope
    DASHSCOPE_API_KEY = os.getenv("DASHSCOPE_API_KEY")
    MODEL_NAME = "qwen-turbo"  

    # --- 3. Embedding 与 向量库配置 ---
    # 原始模型 ID
    EMBEDDING_MODEL_ID = "BAAI/bge-small-zh-v1.5"
    # 本地模型绝对路径
    LOCAL_MODEL_PATH = MODEL_DIR / "bge-small-zh-v1.5"

    # 待向量化的目标文件 (示例)
    SOURCE_FILE = DATA_DIR / "standards" / "concrete_jgj23.md"

    # RAG 参数
    CHUNK_SIZE = 500
    CHUNK_OVERLAP = 50
    TOP_K = 3

    # --- 4. 自动初始化 ---
    # 自动创建必要目录
    DOCS_DIR.mkdir(parents=True, exist_ok=True)
    VECTOR_DB_DIR.mkdir(parents=True, exist_ok=True)
    MODEL_DIR.mkdir(parents=True, exist_ok=True)
