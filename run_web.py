import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.chdir(os.path.dirname(os.path.abspath(__file__)))

from langchain_customer_service_robot.web.web_app import app
import uvicorn

print("=" * 50)
print("智能客服机器人 Web 服务启动中...")
print("=" * 50)
print(f"请在浏览器中访问: http://127.0.0.1:8000")
print(f"或者访问: http://localhost:8000")
print("=" * 50)
uvicorn.run(app, host="127.0.0.1", port=8000)
