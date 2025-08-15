# Ibtikar Community RAG Chatbot

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)](https://fastapi.tiangolo.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

An intelligent Arabic-first RAG (Retrieval-Augmented Generation) chatbot system designed specifically for the Ibtikar community - a network of Arabic-speaking university students passionate about innovation, technology, research, and development.

## 📁 Project Structure

```
ibtikar-chatbot/
├── 📄 README.md              # This file - Project overview and quick start
├── 📄 LICENSE                # MIT License
├── 📁 scrapper/              # Main application code
│   ├── 🎯 core/              # Core application configuration
│   ├── 🗃️ models/            # Database models
│   ├── 📋 schemas/           # API schemas  
│   ├── 🔄 crud/              # Database operations
│   ├── 🌐 endpoints/         # API endpoints
│   ├── ⚙️ services/          # Business logic services
│   ├── 🗃️ alembic/           # Database migrations
│   ├── 📄 main.py            # Original application entry point
│   ├── 📄 main_new.py        # Refactored application entry point
│   ├── 📄 pyproject.toml     # Project dependencies
│   ├── 📄 requirements.txt   # Requirements file
│   ├── 📄 .env.example       # Environment configuration template
│   ├── 📄 docker-compose.yml # Docker composition
│   ├── 📄 Dockerfile         # Docker container
│   └── 📚 STRUCTURE_GUIDE.md # Detailed structure documentation
└── 📁 .git/                 # Git repository
```

## 🎯 Features

- **Arabic-First NLP**: Native Arabic language understanding with dialect support
- **RAG Pipeline**: Advanced retrieval-augmented generation for accurate responses
- **Web Scraping**: Automated content extraction from websites and documents
- **Vector Search**: Semantic search using embeddings and vector databases
- **Knowledge Management**: Automated ingestion and processing of community documents
- **API-First Design**: RESTful API with automatic documentation
- **Modular Architecture**: Clean, maintainable code structure
- **Production Ready**: Proper logging, error handling, and configuration management

## 🏗 Architecture

```
├── Frontend (Web App)
├── Backend (FastAPI)
│   ├── Web Scraper (Requests/Selenium/Playwright)
│   ├── Data Processing (Arabic Text Processing)
│   ├── Vector Store (FAISS/Upstash)
│   ├── Embedding Service (BGE-M3)
│   └── Database (PostgreSQL - Optional)
└── Storage (Local/Azure Blob)
```

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- Git

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/ibtikar-org-tr/ibtikar-chatbot.git
   cd ibtikar-chatbot
   ```

2. **Navigate to the scrapper directory**
   ```bash
   cd scrapper
   ```

3. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

4. **Install dependencies**
   ```bash
   pip install -e .
   ```

5. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

6. **Run the application**
   ```bash
   # Use the new refactored version
   python main_new.py
   
   # Or use uvicorn directly
   uvicorn main_new:app --reload
   ```

The API will be available at `http://localhost:8000`

## 📚 Documentation

- **API Documentation**: Visit `http://localhost:8000/docs` when running
- **Structure Guide**: See `scrapper/STRUCTURE_GUIDE.md` for detailed architecture
- **Configuration**: Check `scrapper/.env.example` for all available settings

## 🔧 Configuration

The application supports multiple backends:

### Storage Backends
- **local**: Store files locally (default)
- **azure**: Use Azure Blob Storage

### Vector Store Backends  
- **faiss**: Local FAISS index (default)
- **upstash**: Upstash Vector Database

### Scraping Backends
- **requests**: Simple HTTP requests (default)
- **selenium**: Browser automation
- **playwright**: Async browser automation

## 🧪 Testing

```bash
cd scrapper
python test_structure.py
```

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## � License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🏢 About Ibtikar

Ibtikar is a thriving community of Arabic-speaking university students united by their passion for innovation, technology, research, and development. We foster collaboration, knowledge sharing, and academic excellence among our members.

---

**Note**: All application code is contained within the `scrapper/` directory. The root directory contains only documentation and project metadata.

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


