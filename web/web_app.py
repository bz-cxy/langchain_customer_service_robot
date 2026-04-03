import os
import uuid
from datetime import datetime
from typing import Optional

from fastapi import FastAPI, Request, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from jinja2 import Environment, FileSystemLoader

from langchain_customer_service_robot.bot.customer_service_bot import CustomerServiceBot


app = FastAPI(title="智能客服机器人")

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
jinja_env = Environment(loader=FileSystemLoader(os.path.join(BASE_DIR, "templates")))

bot_instances: dict[str, CustomerServiceBot] = {}


def get_or_create_bot(user_id: str, session_id: Optional[str] = None) -> CustomerServiceBot:
    """获取或创建机器人实例"""
    key = f"{user_id}_{session_id}" if session_id else user_id
    if key not in bot_instances:
        bot_instances[key] = CustomerServiceBot()
        bot_instances[key].start_session(user_id, session_id)
    return bot_instances[key]


def render_template(name: str, **context) -> str:
    template = jinja_env.get_template(name)
    return template.render(**context)


@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return HTMLResponse(content=render_template("index.html"))


@app.get("/api/sessions/{user_id}")
async def get_sessions(user_id: str):
    """获取用户历史会话列表"""
    bot = CustomerServiceBot()
    sessions = bot.storage.get_all_sessions(user_id)
    return {"sessions": sessions[-5:] if sessions else []}


@app.post("/api/chat")
async def chat(request: Request):
    """发送消息并获取回复"""
    data = await request.json()
    user_id = data.get("user_id", "user001")
    session_id = data.get("session_id")
    message = data.get("message", "")
    
    if not message.strip():
        return {"error": "消息不能为空"}
    
    bot = get_or_create_bot(user_id, session_id)
    response = bot.chat(message)
    
    return {
        "response": response,
        "session_id": bot.current_session,
        "user_id": bot.current_user
    }


@app.post("/api/session/new")
async def new_session(request: Request):
    """创建新会话"""
    data = await request.json()
    user_id = data.get("user_id", "user001")
    
    bot = CustomerServiceBot()
    session_id = f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    bot.start_session(user_id, session_id)
    
    key = f"{user_id}_{session_id}"
    bot_instances[key] = bot
    
    welcome_message = bot.messages[-1].content if bot.messages else "您好！我是智能客服助手。请问有什么可以帮您？"
    
    return {
        "session_id": session_id,
        "user_id": user_id,
        "welcome_message": welcome_message
    }


@app.websocket("/ws/chat")
async def websocket_chat(websocket: WebSocket):
    """WebSocket 实时通信"""
    await websocket.accept()
    
    user_id = "user001"
    session_id = None
    bot = None
    
    try:
        while True:
            data = await websocket.receive_json()
            
            if data.get("type") == "init":
                user_id = data.get("user_id", "user001")
                session_id = data.get("session_id")
                bot = get_or_create_bot(user_id, session_id)
                
                welcome = bot.messages[-1].content if bot.messages else "您好！我是智能客服助手。请问有什么可以帮您？"
                await websocket.send_json({
                    "type": "welcome",
                    "message": welcome,
                    "session_id": bot.current_session,
                    "user_id": bot.current_user
                })
            
            elif data.get("type") == "message":
                if bot is None:
                    bot = get_or_create_bot(user_id, session_id)
                
                user_message = data.get("content", "")
                if user_message.strip():
                    response = bot.chat(user_message)
                    await websocket.send_json({
                        "type": "response",
                        "message": response,
                        "session_id": bot.current_session
                    })
            
            elif data.get("type") == "new_session":
                user_id = data.get("user_id", user_id)
                session_id = f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                bot = CustomerServiceBot()
                bot.start_session(user_id, session_id)
                
                key = f"{user_id}_{session_id}"
                bot_instances[key] = bot
                
                welcome = bot.messages[-1].content if bot.messages else "您好！我是智能客服助手。请问有什么可以帮您？"
                await websocket.send_json({
                    "type": "welcome",
                    "message": welcome,
                    "session_id": bot.current_session,
                    "user_id": bot.current_user
                })
    
    except WebSocketDisconnect:
        if bot:
            bot.end_session()
