# Intelligent Customer Service Robot (LangChain Customer Service Robot)

An intelligent customer service robot system built with LangChain, supporting knowledge base Q&A, order queries, customer information management, and more. Provides both CLI and Web UI interaction modes.

## Features

- **Intelligent Conversation**: Smart customer service dialogue based on LangChain Agent
- **Knowledge Base Q&A**: Uses RAG (Retrieval-Augmented Generation) technology with hybrid retrieval (Vector + BM25)
- **Multi-Tool Support**:
  - Customer information query
  - Order status query
  - Ticket creation
  - Knowledge base search
- **Session Management**: Supports multi-user, multi-session conversation history storage
- **Web UI**: Modern web interface with real-time WebSocket communication

## Project Structure

```
langchain_customer_service_robot/
├── core/                       # Core modules
│   ├── __init__.py
│   ├── config.py               # Configuration management
│   └── agent_state.py          # Agent state definition
├── splitters/                  # Text splitters
│   ├── __init__.py
│   └── semantic_splitter.py    # Semantic text splitter
├── retrievers/                 # Retrievers
│   ├── __init__.py
│   └── hybrid_retriever.py     # Hybrid retriever (Vector + BM25)
├── knowledge_base/             # Knowledge base module
│   ├── __init__.py
│   └── knowledge_base.py       # Knowledge base core class
├── tools/                      # Agent tools
│   ├── __init__.py
│   └── customer_tools.py       # Customer service tool definitions
├── storage/                    # Storage module
│   ├── __init__.py
│   ├── conversation_storage.py # Conversation storage
│   └── customer_database.py    # Customer database (mock)
├── bot/                        # Bot module
│   ├── __init__.py
│   └── customer_service_bot.py # Customer service bot core logic
├── web/                        # Web module
│   ├── __init__.py
│   └── web_app.py              # Web API service
├── cli/                        # CLI module
│   ├── __init__.py
│   └── main.py                 # CLI entry point
├── templates/                  # Web templates
│   └── index.html              # Web UI interface
├── knowledge_docs/             # Knowledge base documents directory
├── knowledge_index/            # Knowledge base index directory
│   ├── index.faiss
│   ├── index.pkl
│   └── bm25_index.json
├── conversation/               # Conversation history storage
├── main.py                     # CLI entry point
├── run_web.py                  # Web service startup script
├── start_web.bat               # Windows startup script
├── requirements.txt            # Dependencies
├── pyproject.toml              # Project configuration
├── .env.example                # Environment variables example
└── README.md                   # Project documentation
```

## Module Description

### Core Module (core/)
- **config.py**: Configuration management using Pydantic Settings with environment variable support
- **agent_state.py**: Defines Agent state structure for LangGraph state management

### Splitters Module (splitters/)
- **semantic_splitter.py**: Semantic-based text splitter that merges semantically similar text chunks

### Retrievers Module (retrievers/)
- **hybrid_retriever.py**: Hybrid retriever combining vector retrieval and BM25 retrieval

### Knowledge Base Module (knowledge_base/)
- **knowledge_base.py**: Core knowledge base management class providing index building, loading, retrieval, and Q&A functionality

### Tools Module (tools/)
- **customer_tools.py**: Agent tool definitions including customer info query, order query, ticket creation, and knowledge base search

### Storage Module (storage/)
- **conversation_storage.py**: JSON-based multi-user, multi-session conversation storage
- **customer_database.py**: Mock customer database storing customer information and order data

### Bot Module (bot/)
- **customer_service_bot.py**: Customer service bot core logic integrating LLM, tools, and storage

### Web Module (web/)
- **web_app.py**: FastAPI web service providing REST API and WebSocket interfaces

### CLI Module (cli/)
- **main.py**: Command-line interaction entry point

## Requirements

- Python 3.11+
- See `requirements.txt` for dependencies

## Installation

### 1. Clone the Project

```bash
git clone <repository-url>
cd langchain_customer_service_robot
```

### 2. Create Virtual Environment (Recommended)

```bash
python -m venv .venv

# Windows
.venv\Scripts\activate

# Linux/macOS
source .venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
pip install -e .
```

> **Note**: `pip install -e .` installs the project in editable mode, allowing proper module imports.

### 4. Configure Environment Variables

Copy the environment variables example file:

```bash
copy .env.example .env   # Windows
# or
cp .env.example .env     # Linux/macOS
```

Edit the `.env` file and fill in your API keys:

```env
# DeepSeek API Configuration (for LLM conversation, required)
DEEPSEEK_API_KEY=your_deepseek_api_key_here
DEEPSEEK_BASE_URL=https://api.deepseek.com
DEEPSEEK_MODEL=deepseek-chat

# SiliconFlow Embedding API Configuration (for knowledge base vectorization, required)
SILICONFLOW_API_KEY=your_siliconflow_api_key_here
```

> **Note**:
> - You need to apply for DeepSeek API Key: https://platform.deepseek.com/
> - SiliconFlow API Key is used for Embedding vectorization: https://siliconflow.cn/

## Usage

### Method 1: CLI Mode

```bash
python main.py
```

After running, enter a user ID as prompted to start a conversation:
- Enter questions to chat with the customer service bot
- Enter `quit` to end the conversation and save the session

### Method 2: Web UI Mode

1. Start the web service:

```bash
python run_web.py
```

Or use the Windows batch script:
```bash
start_web.bat
```

2. Open your browser and visit: `http://localhost:8003`

#### Web UI Features

- **User ID**: Enter a user identifier (e.g., user001, user002)
- **Load History**: View and continue previous conversations
- **New Session**: Start a new conversation session
- **Real-time Chat**: Low-latency real-time communication via WebSocket

## API Reference

### REST API

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Web UI page |
| `/api/sessions/{user_id}` | GET | Get user's historical session list |
| `/api/chat` | POST | Send message and get response |
| `/api/session/new` | POST | Create new session |

### WebSocket API

Connection endpoint: `/ws/chat`

Message format:
```json
// Initialize session
{"type": "init", "user_id": "user001", "session_id": "optional_session_id"}

// Send message
{"type": "message", "content": "Hello"}

// New session
{"type": "new_session", "user_id": "user001"}
```

## Agent Tools

| Tool Name | Function | Parameters |
|-----------|----------|------------|
| `get_customer_info` | Get customer information | `user_id`: Customer ID |
| `get_order_status` | Query order status | `order_id`: Order number |
| `query_orders` | Query customer orders | `user_id`: Customer ID |
| `create_ticket` | Create service ticket | `user_id`, `problem` |
| `search_knowledge_base` | Search knowledge base | `keyword`: Keyword |

## Configuration

`core/config.py` supports the following configuration items:

| Config Item | Default | Description |
|-------------|---------|-------------|
| `chunk_size` | 500 | Text chunk size |
| `chunk_overlap` | 50 | Chunk overlap size |
| `retrieval_k` | 5 | Number of documents to retrieve |
| `rerank_top_k` | 3 | Number to keep after reranking |
| `similarity_threshold` | 0.5 | Similarity threshold |
| `temperature` | 0.7 | Model temperature |
| `embedding_base_url` | - | Embedding API URL |
| `embedding_model` | BAAI/bge-m3 | Embedding model |

## Knowledge Base Management

### Customizing Service Manual

The project provides a sample e-commerce customer service manual by default. You can customize the knowledge base according to your business needs:

1. **Delete or Replace Existing Documents**
   - Delete sample documents in the `knowledge_docs/` directory
   - Add your own service manuals, FAQs, product descriptions, etc.

2. **Supported Document Formats**
   - `.txt` text files (recommended, UTF-8 encoding)
   - `.pdf` PDF documents
   - `.docx` Word documents

3. **Document Organization Tips**
   - Each document should focus on one topic (e.g., return policy, product description)
   - Keep document content clear and structured
   - Avoid overly large documents (recommended under 1MB)

### Rebuilding Knowledge Base Index

After adding, modifying, or deleting knowledge documents, rebuild the index:

```bash
# Delete existing index
rm -rf knowledge_index/      # Linux/macOS
rmdir /s knowledge_index     # Windows

# Restart the program, the system will automatically rebuild the index
python main.py
```

> **Note**: When running for the first time or rebuilding the index, the system needs to call the Embedding API to vectorize documents, which may take some time and incur API costs.

## Example Conversation

```
User: Hello, I'm user001, I want to check my orders
Bot: Hello! I'm the intelligent customer service assistant. Let me check your order information.
     [Calling query_orders tool]
     You have the following orders:
     1. Order: order00101, Product: Premium Membership Package, Status: Completed
     2. Order: order00102, Product: Exclusive Service Package, Status: Completed
     Is there anything else I can help you with?

User: What is the return process?
Bot: [Calling search_knowledge_base tool]
     The return process is as follows:
     1. Log in to the member center and go to "My Orders"
     2. Select the corresponding order and click "Apply for Return"
     3. Fill in the reason for return and upload evidence
     4. Customer service will review within 1-2 business days
     5. Send back the item within 48 hours after approval
     ...
```

## Tech Stack

- **LangChain**: LLM application framework
- **LangGraph**: Agent state management
- **FAISS**: Vector database
- **BM25**: Keyword retrieval
- **FastAPI**: Web framework
- **Uvicorn**: ASGI server
- **WebSocket**: Real-time communication
- **Jinja2**: Template engine

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    User Interaction Layer                   │
│  ┌─────────────┐              ┌─────────────────────────┐   │
│  │  CLI Mode   │              │      Web UI Mode        │   │
│  │   (cli/)    │              │  (web/ + templates/)    │   │
│  └─────────────┘              └─────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                    Business Logic Layer                     │
│  ┌─────────────────────────────────────────────────────┐    │
│  │              CustomerServiceBot (bot/)               │    │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  │    │
│  │  │  LLM Model  │  │Agent Logic  │  │Tool Calling │  │    │
│  │  └─────────────┘  └─────────────┘  └─────────────┘  │    │
│  └─────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                   Tools & Services Layer                    │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐  │
│  │Tools Module │  │Knowledge Base│  │  Storage Module    │  │
│  │  (tools/)   │  │(knowledge_   │  │    (storage/)      │  │
│  │             │  │   base/)    │  │                     │  │
│  └─────────────┘  └─────────────┘  └─────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                   Infrastructure Layer                      │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐  │
│  │  Retrievers │  │  Splitters  │  │  Configuration     │  │
│  │(retrievers/)│  │(splitters/) │  │      (core/)       │  │
│  └─────────────┘  └─────────────┘  └─────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

## Notes

1. First-time run requires internet connection to download the Embedding model
2. Knowledge base index building may take some time
3. Ensure the API Key in the `.env` file is valid
4. Conversation history is saved in the `conversation/` directory
5. Do not commit the `.env` file to the repository

## License

MIT License
