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

## 🔧 Configuration

### Environment Variables

Create a `.env` file with the following variables:

```env
# Database
DATABASE_URL=postgresql://user:password@localhost/ibtikar_chatbot
REDIS_URL=redis://localhost:6379

# Authentication
SECRET_KEY=your-secret-key-here
ACCESS_TOKEN_EXPIRE_MINUTES=30

# LLM Configuration
LLM_API_URL=your-llm-api-endpoint
LLM_API_KEY=your-llm-api-key

# Vector Store
VECTOR_STORE_TYPE=chromadb  # or faiss
VECTOR_STORE_PATH=./vector_store

# Embedding Model
EMBEDDING_MODEL=sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2

# Logging
LOG_LEVEL=INFO
```

## 🧪 Testing

Run the test suite:

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src --cov-report=html

# Run specific test categories
pytest -m unit          # Unit tests only
pytest -m integration   # Integration tests only
```

## 📊 API Documentation

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### Key Endpoints

- `POST /chat/` - Send a message to the chatbot
- `GET /chat/history/{user_id}` - Get conversation history
- `POST /auth/login` - User authentication
- `GET /health` - Health check
- `POST /admin/documents/` - Upload knowledge base documents

## 🔄 Development Workflow

### Code Quality

This project uses several tools to maintain code quality:

```bash
# Format code
black .
isort .

# Lint code
flake8 .
mypy .

# Run pre-commit hooks
pre-commit run --all-files
```

### Database Migrations

```bash
# Create a new migration
alembic revision --autogenerate -m "Description of changes"

# Apply migrations
alembic upgrade head

# Rollback migrations
alembic downgrade -1
```

## 🐳 Docker Deployment

### Using Docker Compose

```bash
# Build and start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

### Production Deployment

```bash
# Build production image
docker build -t ibtikar-chatbot:latest .

# Run with production settings
docker run -d \
  --name ibtikar-chatbot \
  -p 8000:8000 \
  --env-file .env.prod \
  ibtikar-chatbot:latest
```

## 📈 Monitoring

The application includes built-in monitoring and metrics:

- **Health Checks**: `/health` endpoint
- **Metrics**: Prometheus metrics at `/metrics`
- **Logging**: Structured logging with Loguru
- **Performance**: Request timing and error tracking

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Development Guidelines

- Follow PEP 8 style guide
- Write comprehensive tests
- Update documentation
- Use conventional commit messages
- Ensure Arabic text handling is properly tested

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [FastAPI](https://fastapi.tiangolo.com/) - Modern web framework
- [LangChain](https://python.langchain.com/) - LLM application framework
- [Sentence Transformers](https://www.sbert.net/) - Multilingual embeddings
- [ChromaDB](https://www.trychroma.com/) - Vector database
- The Ibtikar community for inspiration and requirements

## 📞 Support

- **Documentation**: [Wiki](https://github.com/ibtikar-org-tr/ibtikar-chatbot/wiki)
- **Issues**: [GitHub Issues](https://github.com/ibtikar-org-tr/ibtikar-chatbot/issues)
- **Discussions**: [GitHub Discussions](https://github.com/ibtikar-org-tr/ibtikar-chatbot/discussions)
- **Email**: dev@ibtikar.org

---

**Made with ❤️ for the Arabic-speaking innovation community**
