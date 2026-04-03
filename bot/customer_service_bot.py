import os
from datetime import datetime

from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain.chat_models import init_chat_model
from langchain_core.messages import AIMessage, HumanMessage

from langchain_customer_service_robot.storage.conversation_storage import ConversationStorage
from langchain_customer_service_robot.tools.customer_tools import (
    get_customer_info,
    get_order_status,
    query_orders,
    create_ticket,
    search_knowledge_base
)

load_dotenv(override=True)

api_key = os.getenv('DEEPSEEK_API_KEY')
base_url = os.getenv('DEEPSEEK_BASE_URL')


class CustomerServiceBot:
    """智能客服机器人"""
    
    def __init__(self):
        self.model = init_chat_model(
            api_key=api_key,
            base_url=base_url,
            model=os.getenv('DEEPSEEK_MODEL'),
            temperature=0.7
        )
        
        self.tools = [
            get_customer_info,
            get_order_status,
            query_orders,
            create_ticket,
            search_knowledge_base,
        ]
        
        self.agent = create_agent(
            model=self.model,
            tools=self.tools,
            system_prompt=self._get_system_prompt()
        )
        
        self.storage = ConversationStorage()
        self.current_user = None
        self.current_session = None
        self.messages = []
    
    def _get_system_prompt(self) -> str:
        """获取系统提示词"""
        return """你是一个专业的电商客服助手，你的职责是帮助客户解决问题。

你可以使用以下工具：
1. get_customer_info: 获取客户信息
2. get_order_status: 查询订单状态
3. query_orders: 查询客户订单
4. create_ticket: 创建客服工单
5. search_knowledge_base: 搜索知识库

请根据用户的问题选择合适的工具来帮助他们。回答要礼貌、专业、简洁。"""
    
    def start_session(self, user_id: str, session_id: str = None):
        """开始会话"""
        self.current_user = user_id
        self.current_session = session_id or f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        self.messages = self.storage.get_conversation_by_ids(user_id, self.current_session)
        
        if not self.messages:
            welcome = "您好！我是智能客服助手。请问有什么可以帮您？"
            self.messages.append(AIMessage(content=welcome))
    
    def chat(self, user_input: str) -> str:
        """对话"""
        self.messages.append(HumanMessage(content=user_input))
        
        result = self.agent.invoke({"messages": self.messages})
        self.messages = result["messages"]
        
        self.storage.save_conversation(self.current_user, self.current_session, self.messages)
        
        for msg in reversed(self.messages):
            if msg.type == "ai" and msg.content:
                return msg.content
        
        return "抱歉，我暂时无法处理您的请求。"
    
    def end_session(self):
        """结束会话"""
        self.storage.save_conversation(self.current_user, self.current_session, self.messages)
