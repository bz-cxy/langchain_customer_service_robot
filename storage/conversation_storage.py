import json
import os
from datetime import datetime
from typing import List, Optional

from langchain_core.messages import HumanMessage, SystemMessage, AIMessage


class ConversationStorage:
    """对话存储管理类
    
    基于JSON文件实现多用户、多会话的对话记录存储
    """
    
    def __init__(self, file_path: str = None):
        if file_path is None:
            module_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            file_path = os.path.join(module_dir, "conversation", "customer_service_history.json")
        self.file_path = file_path
        self._ensure_dir_exists()
    
    def _ensure_dir_exists(self):
        """确保存储文件的目录存在"""
        dir_path = os.path.dirname(self.file_path)
        if dir_path and not os.path.exists(dir_path):
            os.makedirs(dir_path)
    
    def load_all_conversations(self, file_path: Optional[str] = None) -> dict:
        """加载指定文件中保存的完整对话数据"""
        target_path = file_path or self.file_path
        if not os.path.exists(target_path):
            return {}
        
        try:
            with open(target_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except json.JSONDecodeError:
            print(f"警告：{target_path} 文件格式错误，返回空对话数据")
            return {}
        except Exception as e:
            print(f"加载对话失败：{str(e)}")
            return {}
    
    def save_conversation(self, user_id: str, session_id: str, messages: list):
        """保存对话到JSON文件"""
        data = self.load_all_conversations()
        
        if user_id not in data:
            data[user_id] = {}
        
        serialized = []
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        for msg in messages:
            serialized.append({
                "type": msg.type,
                "content": msg.content,
                "timestamp": current_time
            })
        data[user_id][session_id] = {
            "messages": serialized,
            "updated_at": current_time
        }
        
        try:
            with open(self.file_path, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"保存对话失败：{str(e)}")
    
    def get_all_sessions(self, user_id: str) -> List[str]:
        """获取指定用户下的所有会话ID列表"""
        data = self.load_all_conversations()
        if user_id not in data:
            return []
        return list(data[user_id].keys())
    
    def get_conversation_by_ids(self, user_id: str, session_id: str) -> list:
        """通过user_id和session_id获取对话记录"""
        data = self.load_all_conversations()
        if user_id not in data or session_id not in data[user_id]:
            return []
        
        messages = []
        for msg_data in data[user_id][session_id]["messages"]:
            if msg_data["type"] == "human":
                messages.append(HumanMessage(content=msg_data["content"]))
            elif msg_data["type"] == "ai":
                messages.append(AIMessage(content=msg_data["content"]))
            elif msg_data["type"] == "system":
                messages.append(SystemMessage(content=msg_data["content"]))
        return messages
