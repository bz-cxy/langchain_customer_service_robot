from typing import TypedDict, List, Annotated
from langchain_core.messages import BaseMessage
from langgraph.graph import add_messages


class AgentState(TypedDict):
    """Agent 状态定义

    这是 Agent 在执行过程中所维护的所有数据
    """

    messages: Annotated[List[BaseMessage], add_messages]
    user_name: str
    session_id: str
