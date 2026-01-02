from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import MarkdownHeaderTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from src.config import Config


class KnowledgeBaseService:
    def __init__(self):
        self.vector_store = None
        self.embeddings = HuggingFaceEmbeddings(model_name=Config.EMBEDDING_MODEL)
        self._init_kb()

    def _init_kb(self):
        """加载 Markdown 数据并向量化"""
        # 1. 加载 Markdown
        file_path = Config.DATA_DIR / "standards" / "concrete_jgj23.md"
        if not file_path.exists():
            return

        with open(file_path, "r", encoding="utf-8") as f:
            text = f.read()

        # 2. 按标题切分 Markdown (保留表格结构的完整性)
        headers_to_split_on = [
            ("#", "Header 1"),
            ("##", "Header 2"),
        ]
        markdown_splitter = MarkdownHeaderTextSplitter(
            headers_to_split_on=headers_to_split_on
        )
        docs = markdown_splitter.split_text(text)

        # 3. 存入向量库
        self.vector_store = Chroma.from_documents(
            documents=docs,
            embedding=self.embeddings,
            persist_directory=str(Config.VECTOR_DB_DIR),
        )

    def query(self, query: str):
        if not self.vector_store:
            return "知识库未初始化"

        # 检索 top 2，确保包含表格上下文
        results = self.vector_store.similarity_search(query, k=2)
        return "\n\n".join([doc.page_content for doc in results])
