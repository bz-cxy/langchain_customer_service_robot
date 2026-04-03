"""
智能客服机器人 (LangChain Customer Service Robot)

基于 LangChain 构建的智能客服机器人系统
"""

__version__ = "1.0.0"
__author__ = "Your Name"

from langchain_customer_service_robot.bot.customer_service_bot import CustomerServiceBot
from langchain_customer_service_robot.knowledge_base.knowledge_base import KnowledgeBase

__all__ = ["CustomerServiceBot", "KnowledgeBase"]
