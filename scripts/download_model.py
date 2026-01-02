# src/scripts/download_model.py
from huggingface_hub import snapshot_download
from src.config import Config

def download():
    print(f"⬇️ 正在下载模型: {Config.EMBEDDING_MODEL_ID} ...")
    
    # 下载到 config 中定义的本地目录
    snapshot_download(
        repo_id=Config.EMBEDDING_MODEL_ID,
        local_dir=Config.LOCAL_MODEL_PATH,
        local_dir_use_symlinks=False  # 确保下载真实文件而非软链接
    )
    
    print(f"✅ 模型已保存至: {Config.LOCAL_MODEL_PATH}")

if __name__ == "__main__":
    """ 
    uv run python -m scripts.download_model
    """
    download()
    print("🎉 模型下载完成！")