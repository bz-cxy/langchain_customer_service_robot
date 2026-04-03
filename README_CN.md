# 智能客服机器人 (LangChain Customer Service Robot)

基于 LangChain 构建的智能客服机器人系统，支持知识库问答、订单查询、客户信息管理等功能，提供命令行和 Web UI 两种交互方式。

## 功能特性

- **智能对话**: 基于 LangChain Agent 的智能客服对话
- **知识库问答**: 使用 RAG (检索增强生成) 技术，支持向量检索 + BM25 混合检索
- **多工具支持**: 
  - 客户信息查询
  - 订单状态查询
  - 工单创建
  - 知识库搜索
- **会话管理**: 支持多用户、多会话的对话历史存储
- **Web UI**: 现代化的 Web 界面，支持实时 WebSocket 通信

## 项目结构

```
langchain_customer_service_robot/
├── core/                       # 核心模块
│   ├── __init__.py
│   ├── config.py               # 配置管理
│   └── agent_state.py          # Agent 状态定义
├── splitters/                  # 文本分块器
│   ├── __init__.py
│   └── semantic_splitter.py    # 语义分块器
├── retrievers/                 # 检索器
│   ├── __init__.py
│   └── hybrid_retriever.py     # 混合检索器（向量 + BM25）
├── knowledge_base/             # 知识库模块
│   ├── __init__.py
│   └── knowledge_base.py       # 知识库核心类
├── tools/                      # Agent 工具
│   ├── __init__.py
│   └── customer_tools.py       # 客服工具定义
├── storage/                    # 存储模块
│   ├── __init__.py
│   ├── conversation_storage.py # 对话存储
│   └── customer_database.py    # 客户数据库（模拟）
├── bot/                        # 机器人模块
│   ├── __init__.py
│   └── customer_service_bot.py # 客服机器人核心逻辑
├── web/                        # Web 模块
│   ├── __init__.py
│   └── web_app.py              # Web API 服务
├── cli/                        # 命令行模块
│   ├── __init__.py
│   └── main.py                 # CLI 入口
├── templates/                  # Web 模板
│   └── index.html              # Web UI 界面
├── knowledge_docs/             # 知识库文档目录
│   └── 电商客服服务手册.txt
├── knowledge_index/            # 知识库索引目录
│   ├── index.faiss
│   ├── index.pkl
│   └── bm25_index.json
├── conversation/               # 对话历史存储
│   └── customer_service_history.json
├── main.py                     # CLI 入口
├── run_web.py                  # Web 服务启动脚本
├── start_web.bat               # Windows 启动脚本
├── requirements.txt            # 依赖文件
├── pyproject.toml              # 项目配置文件
├── .env.example                # 环境变量示例
└── README.md                   # 项目说明
```

## 模块说明

### 核心模块 (core/)
- **config.py**: 使用 Pydantic Settings 管理配置，支持环境变量
- **agent_state.py**: 定义 Agent 状态结构，用于 LangGraph 状态管理

### 分块器模块 (splitters/)
- **semantic_splitter.py**: 基于语义相似度的文本分块器，将语义相近的文本块合并

### 检索器模块 (retrievers/)
- **hybrid_retriever.py**: 混合检索器，结合向量检索和 BM25 检索的优势

### 知识库模块 (knowledge_base/)
- **knowledge_base.py**: 知识库管理核心类，提供索引构建、加载、检索和问答功能

### 工具模块 (tools/)
- **customer_tools.py**: Agent 工具定义，包括客户信息查询、订单查询、工单创建、知识库搜索

### 存储模块 (storage/)
- **conversation_storage.py**: 基于 JSON 的多用户、多会话对话存储
- **customer_database.py**: 模拟客户数据库，存储客户信息和订单数据

### 机器人模块 (bot/)
- **customer_service_bot.py**: 客服机器人核心逻辑，整合 LLM、工具和存储

### Web 模块 (web/)
- **web_app.py**: FastAPI Web 服务，提供 REST API 和 WebSocket 接口

### 命令行模块 (cli/)
- **main.py**: 命令行交互入口

## 环境要求

- Python 3.11+
- 依赖包见 `requirements.txt`

## 安装

### 1. 克隆项目

```bash
git clone <repository-url>
cd langchain_customer_service_robot
```

### 2. 创建虚拟环境（推荐）

```bash
python -m venv .venv

# Windows
.venv\Scripts\activate

# Linux/macOS
source .venv/bin/activate
```

### 3. 安装依赖

**方式一：使用 pip 默认源安装**

```bash
pip install -r requirements.txt
pip install -e .
```

**方式二：使用清华源安装（推荐国内用户）**

如果默认源安装失败或速度较慢，可以使用清华源镜像：

```bash
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
pip install -e . -i https://pypi.tuna.tsinghua.edu.cn/simple
```

或者设置永久使用清华源：

```bash
pip config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple
pip install -r requirements.txt
pip install -e .
```

> **注意**: `pip install -e .` 用于以可编辑模式安装本项目包，使得项目内的模块可以正确导入。

### 4. 配置环境变量

复制环境变量示例文件：

```bash
copy .env.example .env   # Windows
# 或
cp .env.example .env     # Linux/macOS
```

编辑 `.env` 文件，填入您的 API 密钥：

```env
# DeepSeek API 配置（用于 LLM 对话，必填）
DEEPSEEK_API_KEY=your_deepseek_api_key_here
DEEPSEEK_BASE_URL=https://api.deepseek.com
DEEPSEEK_MODEL=deepseek-chat

# SiliconFlow Embedding API 配置（用于知识库向量化，必填）
SILICONFLOW_API_KEY=your_siliconflow_api_key_here
```

> **注意**: 
> - 您需要自行申请 DeepSeek API Key: https://platform.deepseek.com/
> - SiliconFlow API Key 用于 Embedding 向量化: https://siliconflow.cn/

## 使用方法

### 方式一：命令行模式

```bash
python main.py
```

运行后按提示输入用户ID，即可开始对话：
- 输入问题与客服机器人对话
- 输入 `quit` 结束对话并保存会话

### 方式二：Web UI 模式

1. 启动 Web 服务：

```bash
python run_web.py
```

或使用 Windows 批处理脚本：
```bash
start_web.bat
```

2. 打开浏览器访问：`http://localhost:8003`

#### Web UI 功能说明

- **用户ID**: 输入用户标识（如 user001、user002）
- **加载历史会话**: 查看并继续之前的对话
- **新建会话**: 开始一个新的对话会话
- **实时对话**: 通过 WebSocket 实现低延迟实时通信

## API 接口

### REST API

| 接口 | 方法 | 说明 |
|------|------|------|
| `/` | GET | Web UI 页面 |
| `/api/sessions/{user_id}` | GET | 获取用户历史会话列表 |
| `/api/chat` | POST | 发送消息并获取回复 |
| `/api/session/new` | POST | 创建新会话 |

### WebSocket API

连接地址：`/ws/chat`

消息格式：
```json
// 初始化会话
{"type": "init", "user_id": "user001", "session_id": "optional_session_id"}

// 发送消息
{"type": "message", "content": "你好"}

// 新建会话
{"type": "new_session", "user_id": "user001"}
```

## Agent 工具说明

| 工具名称 | 功能 | 参数 |
|----------|------|------|
| `get_customer_info` | 获取客户信息 | `user_id`: 客户ID |
| `get_order_status` | 查询订单状态 | `order_id`: 订单号 |
| `query_orders` | 查询客户订单 | `user_id`: 客户ID |
| `create_ticket` | 创建客服工单 | `user_id`, `problem` |
| `search_knowledge_base` | 搜索知识库 | `keyword`: 关键词 |

## 配置说明

`core/config.py` 支持以下配置项：

| 配置项 | 默认值 | 说明 |
|--------|--------|------|
| `chunk_size` | 500 | 文本分块大小 |
| `chunk_overlap` | 50 | 分块重叠大小 |
| `retrieval_k` | 5 | 检索返回文档数 |
| `rerank_top_k` | 3 | 重排序后保留数 |
| `similarity_threshold` | 0.5 | 相似度阈值 |
| `temperature` | 0.7 | 模型温度 |
| `embedding_base_url` | - | Embedding API 地址 |
| `embedding_model` | BAAI/bge-m3 | Embedding 模型 |

## 知识库管理

### 自定义客服手册

项目默认提供了一个电商客服服务手册示例。您可以根据自己的业务需求自定义知识库：

1. **删除或替换现有文档**
   - 删除 `knowledge_docs/` 目录中的示例文档
   - 添加您自己的客服手册、FAQ、产品说明等文档

2. **支持的文档格式**
   - `.txt` 文本文件（推荐，UTF-8 编码）
   - `.pdf` PDF 文档
   - `.docx` Word 文档

3. **文档组织建议**
   - 每个文档聚焦一个主题（如退货政策、产品说明等）
   - 文档内容清晰、结构化
   - 避免单个文档过大（建议不超过 1MB）

### 重建知识库索引

当您添加、修改或删除知识文档后，需要重建索引：

```bash
# 删除现有索引
rm -rf knowledge_index/      # Linux/macOS
rmdir /s knowledge_index     # Windows

# 重新启动程序，系统会自动重建索引
python main.py
```

> **注意**: 首次运行或重建索引时，系统需要调用 Embedding API 对文档进行向量化，可能需要较长时间和一定的 API 费用。

## 示例对话

```
用户: 你好，我是user001，想查询一下我的订单
客服: 您好！我是智能客服助手。我帮您查询一下您的订单信息。
      [调用 query_orders 工具]
      您有以下订单：
      1. 订单号：order00101，商品：高端会员套餐，状态：已完成
      2. 订单号：order00102，商品：专属服务包，状态：已完成
      请问还有什么可以帮您的吗？

用户: 退货流程是什么？
客服: [调用 search_knowledge_base 工具]
      退货流程如下：
      1. 登录会员中心，进入"我的订单"
      2. 选择对应订单，点击"申请退货"
      3. 填写退货原因并上传凭证
      4. 客服将在1-2个工作日内审核
      5. 审核通过后48小时内寄回商品
      ...
```

## 技术栈

- **LangChain**: LLM 应用框架
- **LangGraph**: Agent 状态管理
- **FAISS**: 向量数据库
- **BM25**: 关键词检索
- **FastAPI**: Web 框架
- **Uvicorn**: ASGI 服务器
- **WebSocket**: 实时通信
- **Jinja2**: 模板引擎

## 架构设计

```
┌─────────────────────────────────────────────────────────────┐
│                      用户交互层                              │
│  ┌─────────────┐              ┌─────────────────────────┐   │
│  │   CLI 模式   │              │       Web UI 模式        │   │
│  │   (cli/)    │              │    (web/ + templates/)  │   │
│  └─────────────┘              └─────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                      业务逻辑层                              │
│  ┌─────────────────────────────────────────────────────┐    │
│  │              CustomerServiceBot (bot/)               │    │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  │    │
│  │  │   LLM 模型   │  │  Agent 逻辑  │  │  工具调用   │  │    │
│  │  └─────────────┘  └─────────────┘  └─────────────┘  │    │
│  └─────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                      工具与服务层                            │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐  │
│  │   工具模块   │  │  知识库模块  │  │      存储模块        │  │
│  │  (tools/)   │  │(knowledge_  │  │     (storage/)      │  │
│  │             │  │   base/)    │  │                     │  │
│  └─────────────┘  └─────────────┘  └─────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                      基础设施层                              │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐  │
│  │  检索器模块  │  │  分块器模块  │  │      配置模块        │  │
│  │(retrievers/)│  │(splitters/) │  │      (core/)        │  │
│  └─────────────┘  └─────────────┘  └─────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

## 注意事项

1. 首次运行需要联网下载 Embedding 模型
2. 知识库索引构建可能需要较长时间
3. 确保 `.env` 文件中的 API Key 有效
4. 对话历史保存在 `conversation/` 目录下
5. 请勿将 `.env` 文件提交到代码仓库

## License

MIT License
