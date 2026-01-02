#src/services/rag_service.py
from langchain_community.vectorstores import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from src.config import Config


class KnowledgeBaseService:
    def __init__(self):
        # 1. 加载本地 Embedding 模型 (用于将 Query 转向量)
        self.embeddings = HuggingFaceEmbeddings(model_name=str(Config.LOCAL_MODEL_PATH))

        # 2. 直接加载已存在的向量库
        self.vector_store = Chroma(
            persist_directory=str(Config.VECTOR_DB_DIR),
            embedding_function=self.embeddings,
        )

    def query(self, question: str) -> str:
        """检索相关上下文"""
        if not self.vector_store:
            return ""

        # 执行相似度搜索
        results = self.vector_store.similarity_search(question, k=Config.TOP_K)

        # 拼接结果
        return "\n\n".join([doc.page_content for doc in results])
