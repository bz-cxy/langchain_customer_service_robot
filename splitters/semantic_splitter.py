import logging
from typing import List

import numpy as np
from langchain_core.documents import Document
from langchain_openai import OpenAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter

logger = logging.getLogger(__name__)


class SemanticTextSplitter:
    """语义文本分块器
    
    基于语义相似度进行文本分块，将语义相近的文本块合并
    """
    
    def __init__(self, embeddings: OpenAIEmbeddings, chunk_size: int = 500, 
                 similarity_threshold: float = 0.75):
        self.embeddings = embeddings
        self.chunk_size = chunk_size
        self.similarity_threshold = similarity_threshold
        self.base_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_size // 10,
            separators=["\n\n", "\n", "。", "！", "？", "；", "  ", ""]
        )
    
    def split_documents(self, documents: List[Document]) -> List[Document]:
        logger.info("开始语义分块...")
        
        initial_chunks = self.base_splitter.split_documents(documents)
        logger.info(f"初始分块数量: {len(initial_chunks)}")
        
        if len(initial_chunks) <= 1:
            return initial_chunks
        
        semantic_chunks = self._merge_by_semantics(initial_chunks)
        logger.info(f"语义分块后数量: {len(semantic_chunks)}")
        
        return semantic_chunks
    
    def _merge_by_semantics(self, chunks: List[Document]) -> List[Document]:
        if not chunks:
            return []
        
        merged_chunks = []
        current_chunk = chunks[0]
        
        for i in range(1, len(chunks)):
            next_chunk = chunks[i]
            
            similarity = self._calculate_similarity(
                current_chunk.page_content,
                next_chunk.page_content
            )
            
            combined_length = len(current_chunk.page_content) + len(next_chunk.page_content)
            
            if similarity > self.similarity_threshold and combined_length < self.chunk_size * 1.5:
                current_chunk = Document(
                    page_content=current_chunk.page_content + "\n" + next_chunk.page_content,
                    metadata={**current_chunk.metadata, **next_chunk.metadata}
                )
            else:
                merged_chunks.append(current_chunk)
                current_chunk = next_chunk
        
        merged_chunks.append(current_chunk)
        
        return merged_chunks
    
    def _calculate_similarity(self, text1: str, text2: str) -> float:
        try:
            embeddings = self.embeddings.embed_documents([text1, text2])
            
            vec1 = np.array(embeddings[0])
            vec2 = np.array(embeddings[1])
            
            similarity = np.dot(vec1, vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2))
            return float(similarity)
        except Exception as e:
            logger.warning(f"计算相似度失败: {e}, 返回默认值0.5")
            return 0.5
