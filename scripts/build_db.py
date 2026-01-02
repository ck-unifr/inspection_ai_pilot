# src/scripts/build_db.py
import shutil
from langchain_text_splitters import MarkdownHeaderTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from src.config import Config


def build_database():
    if not Config.SOURCE_FILE.exists():
        print(f"❌ 文件不存在: {Config.SOURCE_FILE}")
        return

    # 1. 清理旧库 (可选，确保完全重建)
    if Config.VECTOR_DB_DIR.exists():
        shutil.rmtree(Config.VECTOR_DB_DIR)

    # 2. 加载并切分
    print("📖 读取并切分文档...")
    with open(Config.SOURCE_FILE, "r", encoding="utf-8") as f:
        text = f.read()

    splitter = MarkdownHeaderTextSplitter(
        headers_to_split_on=[("#", "H1"), ("##", "H2")]
    )
    docs = splitter.split_text(text)

    # 3. 初始化本地 Embedding 模型
    print(f"🧠 加载本地模型: {Config.LOCAL_MODEL_PATH}")
    embeddings = HuggingFaceEmbeddings(model_name=str(Config.LOCAL_MODEL_PATH))

    # 4. 向量化并持久化
    print("💾 正在写入向量库...")
    Chroma.from_documents(
        documents=docs,
        embedding=embeddings,
        persist_directory=str(Config.VECTOR_DB_DIR),
    )
    print(f"✅ 向量库构建完成: {Config.VECTOR_DB_DIR}")


if __name__ == "__main__":
    """
    uv run python -m scripts.build_db
    """
    build_database()
    print("🎉 向量库构建完成！")
