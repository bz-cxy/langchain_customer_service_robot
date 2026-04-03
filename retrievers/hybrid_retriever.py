import logging
from typing import List, Optional

from langchain_core.documents import Document
from langchain_community.vectorstores import FAISS
from langchain_community.retrievers import BM25Retriever

logger = logging.getLogger(__name__)


class HybridRetriever:
    """混合检索器
    
    结合向量检索和BM25检索的优势，提供更准确的文档检索
    """
    
    def __init__(self, vectorstore: FAISS, bm25_retriever: Optional[BM25Retriever] = None, k: int = 5):
        self.vectorstore = vectorstore
        self.bm25_retriever = bm25_retriever
        self.k = k
    
    def retrieve(self, question: str) -> List[Document]:
        """执行混合检索"""
        vector_retriever = self.vectorstore.as_retriever(
            search_type="similarity",
            search_kwargs={"k": self.k}
        )
        
        vector_docs = vector_retriever.invoke(question)
        bm25_docs = self.bm25_retriever.invoke(question) if self.bm25_retriever else []
        
        return self._merge_results(vector_docs, bm25_docs)
    
    def _merge_results(self, vector_docs: List[Document], bm25_docs: List[Document]) -> List[Document]:
        """合并向量检索和BM25检索结果，去重"""
        seen = set()
        combined_docs = []
        
        for doc in vector_docs:
            doc_id = doc.page_content[:100]
            if doc_id not in seen:
                seen.add(doc_id)
                combined_docs.append(doc)
        
        for doc in bm25_docs:
            doc_id = doc.page_content[:100]
            if doc_id not in seen:
                seen.add(doc_id)
                combined_docs.append(doc)
        
        return combined_docs[:self.k]
