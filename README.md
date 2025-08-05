# Ibtikar Community RAG Chatbot

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)](https://fastapi.tiangolo.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

An intelligent Arabic-first RAG (Retrieval-Augmented Generation) chatbot system designed specifically for the Ibtikar community - a network of Arabic-speaking university students passionate about innovation, technology, research, and development.

## 🎯 Features

- **Arabic-First NLP**: Native Arabic language understanding with dialect support
- **RAG Pipeline**: Advanced retrieval-augmented generation for accurate responses
- **Real-time Chat**: WebSocket-based conversational interface
- **Knowledge Management**: Automated ingestion and processing of community documents
- **User Management**: Secure authentication and user profiling
- **Analytics Dashboard**: Usage tracking and performance monitoring
- **Multilingual Support**: Arabic primary, English secondary language support

## 🏗 Architecture

```
├── Frontend (Web App)
├── Backend (FastAPI)
│   ├── RAG Pipeline (LangChain)
│   ├── Vector Store (ChromaDB/FAISS)
│   └── Database (PostgreSQL)
└── Monitoring & Analytics
```

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- PostgreSQL 15+
- Redis 7+
- Git

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/ibtikar-org-tr/ibtikar-chatbot.git
   cd ibtikar-chatbot
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

5. **Initialize database**
   ```bash
   alembic upgrade head
   ```

6. **Run the application**
   ```bash
   uvicorn main:app --reload
   ```

The API will be available at `http://localhost:8000`

## 📁 Project Structure

```
ibtikar-chatbot/
├── alembic/                 # Database migrations
├── core/                    # Core configuration and utilities
├── crud/                    # Database CRUD operations
├── endpoints/               # FastAPI route handlers
├── models/                  # SQLAlchemy database models
├── schemas/                 # Pydantic request/response schemas
├── services/                # Business logic services
├── tests/                   # Test files
├── docs/                    # Documentation
├── scripts/                 # Utility scripts
├── main.py                  # FastAPI application entry point
├── requirements.txt         # Python dependencies
├── pyproject.toml          # Project configuration
├── Dockerfile              # Docker configuration
├── docker-compose.yml      # Docker Compose setup
└── README.md               # This file
```


## 🙏 Acknowledgments

- [FastAPI](https://fastapi.tiangolo.com/) - Modern web framework
- [LangChain](https://python.langchain.com/) - LLM application framework
- [Sentence Transformers](https://www.sbert.net/) - Multilingual embeddings
- [ChromaDB](https://www.trychroma.com/) - Vector database
- The Ibtikar community for inspiration and requirements


