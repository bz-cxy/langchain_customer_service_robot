import json
import os
import logging
import pickle
from datetime import datetime
from typing import List, Dict, Optional

from dotenv import load_dotenv
from langchain_community.vectorstores import FAISS
from langchain_community.retrievers import BM25Retriever
from langchain_community.document_loaders import DirectoryLoader, TextLoader
from langchain_openai import OpenAIEmbeddings
from langchain.chat_models import init_chat_model
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from langchain_core.documents import Document

from langchain_customer_service_robot.core.config import settings
from langchain_customer_service_robot.splitters.semantic_splitter import SemanticTextSplitter
from langchain_customer_service_robot.retrievers.hybrid_retriever import HybridRetriever

load_dotenv(override=True)

logger = logging.getLogger(__name__)

api_key = os.getenv("DEEPSEEK_API_KEY")
base_url = os.getenv("DEEPSEEK_BASE_URL")


class KnowledgeBase:
    """知识库管理类
    
    提供知识库的构建、加载、检索和问答功能
    支持向量检索和BM25混合检索
    """
    
    def __init__(
        self,
        doc_directory: str = None,
        index_directory: str = None,
        embedding_model: str = None
    ):
        self.doc_directory = doc_directory or settings.doc_directory
        self.index_directory = index_directory or settings.index_directory
        
        siliconflow_api_key = os.getenv("SILICONFLOW_API_KEY")
        if not siliconflow_api_key:
            raise ValueError(
                "SILICONFLOW_API_KEY 环境变量未设置。请在 .env 文件中配置 SILICONFLOW_API_KEY。"
            )
        
        self.embeddings = OpenAIEmbeddings(
            base_url=settings.embedding_base_url,
            api_key=siliconflow_api_key,
            model=embedding_model or settings.embedding_model
        )
        
        self.semantic_splitter = SemanticTextSplitter(
            embeddings=self.embeddings,
            chunk_size=settings.chunk_size,
            similarity_threshold=0.75
        )
        
        self.vectorstore: Optional[FAISS] = None
        self.bm25_retriever: Optional[BM25Retriever] = None
        self.hybrid_retriever: Optional[HybridRetriever] = None
        
        self.model = init_chat_model(
            api_key=api_key,
            base_url=base_url,
            model=os.getenv('DEEPSEEK_MODEL'),
            temperature=settings.temperature
        )
        
        self.query_log: List[Dict] = []
    
    def build_index(self) -> bool:
        """构建知识库索引"""
        logger.info("开始构建知识库索引...")
        
        loader = DirectoryLoader(
            self.doc_directory,
            glob="**/*.txt",
            loader_cls=TextLoader,
            loader_kwargs={"encoding": "utf-8"},
            show_progress=True
        )
        
        try:
            docs = loader.load()
            logger.info(f"成功加载 {len(docs)} 个文档")
        except Exception as e:
            logger.error(f"加载文档失败: {e}")
            return False
        
        if not docs:
            logger.error("未找到任何文档")
            return False
        
        logger.info("正在进行语义分块...")
        split_docs = self.semantic_splitter.split_documents(docs)
        logger.info(f"分块完成，共 {len(split_docs)} 个文本块")
        
        logger.info("正在创建向量索引...")
        self.vectorstore = FAISS.from_documents(split_docs, self.embeddings)
        logger.info("向量数据库创建成功")
        
        logger.info("正在创建 BM25 索引...")
        self.bm25_retriever = BM25Retriever.from_documents(split_docs)
        self.bm25_retriever.k = settings.retrieval_k
        logger.info("BM25 索引创建成功")
        
        self._init_hybrid_retriever()
        
        os.makedirs(self.index_directory, exist_ok=True)
        self.vectorstore.save_local(self.index_directory)
        
        bm25_index_path = os.path.join(self.index_directory, "bm25_index.json")
        self._save_bm25_index(bm25_index_path, split_docs)
        
        logger.info(f"索引已保存到 {self.index_directory}")
        return True
    
    def _init_hybrid_retriever(self):
        """初始化混合检索器"""
        if self.vectorstore:
            self.hybrid_retriever = HybridRetriever(
                vectorstore=self.vectorstore,
                bm25_retriever=self.bm25_retriever,
                k=settings.retrieval_k
            )
    
    def _save_bm25_index(self, filepath: str, documents: List[Document]):
        try:
            with open(filepath, 'wb') as f:
                pickle.dump({
                    'documents': [
                        {'page_content': doc.page_content, 'metadata': doc.metadata}
                        for doc in documents
                    ]
                }, f)
            logger.info(f"BM25 索引已保存到 {filepath}")
        except Exception as e:
            logger.warning(f"保存 BM25 索引失败: {e}")
    
    def _load_bm25_index(self, filepath: str) -> Optional[List[Document]]:
        try:
            with open(filepath, 'rb') as f:
                data = pickle.load(f)
                documents = [
                    Document(
                        page_content=doc['page_content'],
                        metadata=doc['metadata']
                    )
                    for doc in data['documents']
                ]
                logger.info(f"BM25 索引加载成功，共 {len(documents)} 个文档")
                return documents
        except Exception as e:
            logger.warning(f"加载 BM25 索引失败: {e}")
            return None
    
    def load_index(self) -> bool:
        """加载已有索引"""
        logger.info("正在加载索引...")
        
        try:
            self.vectorstore = FAISS.load_local(
                self.index_directory,
                self.embeddings,
                allow_dangerous_deserialization=True
            )
            logger.info("向量索引加载成功")
            
            bm25_index_path = os.path.join(self.index_directory, "bm25_index.json")
            documents = self._load_bm25_index(bm25_index_path)
            
            if documents:
                self.bm25_retriever = BM25Retriever.from_documents(documents)
                self.bm25_retriever.k = settings.retrieval_k
                logger.info("BM25 索引加载成功")
            else:
                logger.warning("BM25 索引加载失败，将仅使用向量检索")
            
            self._init_hybrid_retriever()
            return True
        except Exception as e:
            logger.error(f"索引加载失败: {e}")
            return False
    
    def query(self, question: str, k: int = None) -> dict:
        """查询知识库"""
        if not self.vectorstore:
            return {"error": "知识库未初始化"}
        
        k = k or settings.retrieval_k
        
        try:
            logger.info("使用混合检索 (向量 + BM25)")
            docs = self.hybrid_retriever.retrieve(question) if self.hybrid_retriever else []
            logger.info(f"检索到 {len(docs)} 个文档")
            
            prompt = ChatPromptTemplate.from_template(
                """你是一个企业知识问答系统。请基于以下上下文回答问题。

上下文：
{context}

问题是：{question}

要求：
1. 仅基于上下文回答，最好回答原话，不要编造信息
2. 如果上下文中没有相关信息，明确告知用户
3. 回答要准确、简洁
4. 如果引用了具体内容，请标注来源

答案："""
            )
            
            def format_docs(docs):
                return "\n\n---\n\n".join([
                    f"【文档 {i+1}】\n来源：{doc.metadata.get('source', '未知')}\n内容：{doc.page_content}"
                    for i, doc in enumerate(docs)
                ])
            
            rag_chain = (
                {"context": lambda x: format_docs(docs), "question": RunnablePassthrough()}
                | prompt
                | self.model
                | StrOutputParser()
            )
            
            answer = rag_chain.invoke(question)
            
            self.query_log.append({
                "question": question,
                "answer": answer,
                "source": [doc.metadata.get('source', '未知') for doc in docs],
                "timestamp": datetime.now().isoformat(),
                "retrieval_method": "hybrid"
            })
            
            return {
                "question": question,
                "answer": answer,
                "source": docs,
                "source_count": len(docs),
                "retrieval_method": "hybrid"
            }
            
        except Exception as e:
            logger.error(f"查询失败: {e}", exc_info=True)
            return {"error": str(e)}
    
    def export_logs(self, filename: str = "query_log.json"):
        """导出查询日志"""
        try:
            with open(filename, "w", encoding="utf-8") as f:
                json.dump(self.query_log, f, ensure_ascii=False, indent=2)
            logger.info(f"查询日志已导出到 {filename}")
        except Exception as e:
            logger.error(f"导出日志失败: {e}")
