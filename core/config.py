import os
from pathlib import Path
from pydantic_settings import BaseSettings

_MODULE_DIR = Path(__file__).parent.parent


class Settings(BaseSettings):
    chunk_size: int = 500
    chunk_overlap: int = 50
    retrieval_k: int = 5
    rerank_top_k: int = 3
    similarity_threshold: float = 0.5
    temperature: float = 0.7
    
    embedding_base_url: str = "https://api.siliconflow.cn/v1"
    embedding_model: str = "BAAI/bge-m3"
    
    doc_directory: str = str(_MODULE_DIR / "knowledge_docs")
    index_directory: str = str(_MODULE_DIR / "knowledge_index")
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"


settings = Settings()
