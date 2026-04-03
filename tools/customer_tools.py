import os
import time
import uuid
from langchain_core.tools import tool

from langchain_customer_service_robot.storage.customer_database import CustomerDataBase
from langchain_customer_service_robot.knowledge_base.knowledge_base import KnowledgeBase


db = CustomerDataBase()
_kb_instance = None


def _get_kb() -> KnowledgeBase:
    """获取知识库单例"""
    global _kb_instance
    if _kb_instance is None:
        _kb_instance = KnowledgeBase()
        index_faiss_path = os.path.join(_kb_instance.index_directory, "index.faiss")
        if os.path.exists(index_faiss_path):
            _kb_instance.load_index()
        else:
            _kb_instance.build_index()
    return _kb_instance


@tool
def get_customer_info(user_id: str) -> str:
    """
    获取客户信息
    :param user_id: 客户ID，如 user001, user002
    :return: 客户信息
    """
    customer_info = db.get_customer_info(user_id)
    if customer_info is None:
        return f"未找到客户 {user_id} 的信息"
    else:
        return f"""
        客户信息：
        姓名：{customer_info['name']}
        会员等级：{customer_info['level']}
        电话：{customer_info['phone']}
        邮箱：{customer_info['email']}
        """


@tool
def query_orders(user_id: str) -> str:
    """
    查询客户订单
    :param user_id: 客户ID，如 user001, user002
    :return: 客户订单信息
    """
    orders = db.get_customer_orders(user_id)
    if not orders:
        return f"未找到客户 {user_id} 的订单信息"
    else:
        order_info = ""
        for order in orders:
            order_info += f"""{user_id}订单信息：
                订单号：{order['order_id']}
                商品：{order['product']}
                状态：{order['status']}
                下单时间：{order['date']}\n"""
        return order_info


@tool
def get_order_status(order_id: str) -> str:
    """
    查询订单状态
    :param order_id: 订单号，如 ORD001
    :return: 订单状态
    """
    for user_id, user_orders in db.orders.items():
        for order in user_orders:
            if order["order_id"] == order_id:
                return f"订单{order_id}的状态为：{order['status']}"
    
    return f"未查询到订单号为{order_id}的订单信息"


@tool
def create_ticket(user_id: str, problem: str) -> str:
    """
    创建客服工单
    当客户问题无法理解解决时，创建工单记录
    
    :param user_id: 客户ID，如 user001, user002
    :param problem: 问题描述
    :return: 工单创建结果
    """
    timestamp = str(int(time.time()))
    random_suffix = str(uuid.uuid4()).split("-")[-1]
    ticket_id = f"TICKET_{timestamp}_{random_suffix}"
    
    return f"工单创建成功！工单号：{ticket_id}，客户ID：{user_id}，问题描述：{problem}"


@tool
def search_knowledge_base(keyword: str) -> str:
    """
    搜索知识库（使用RAG混合检索：向量检索 + BM25检索）
    
    :param keyword: 搜索关键词或问题（如"退货""换货流程""退款"等）
    :return: 搜索结果（基于知识库文档的智能回答）
    """
    if not keyword or not isinstance(keyword, str):
        return "搜索失败：关键词不能为空且必须为字符串格式"
    
    clean_keyword = keyword.strip()
    if not clean_keyword:
        return "搜索失败：关键词不能仅包含空格"
    
    kb = _get_kb()
    result = kb.query(clean_keyword)
    
    if "error" in result:
        return f"搜索失败：{result['error']}"
    
    answer = result.get("answer", "")
    source_count = result.get("source_count", 0)
    
    return f"{answer}\n\n[基于 {source_count} 个知识库文档检索]"
