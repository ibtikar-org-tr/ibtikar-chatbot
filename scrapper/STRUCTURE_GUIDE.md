# Ibtikar Community RAG Chatbot - Code Structure Guide

## 📁 Project Structure Overview

```
ibtikar-chatbot/
├── 📁 core/                    # Core application configuration
│   ├── config.py              # Application settings and configuration
│   ├── deps.py                # Dependency injection and providers
│   ├── exceptions.py          # Custom exception classes
│   ├── logging.py             # Logging configuration
│   └── database.py            # Database connection management
├── 📁 models/                  # SQLAlchemy database models
│   ├── base.py                # Base model with common fields
│   ├── document.py            # Document model for scraped content
│   └── vector_index.py        # Vector index tracking model
├── 📁 schemas/                 # Pydantic schemas for API
│   └── api.py                 # Request/response schemas
├── 📁 crud/                    # Database CRUD operations
│   ├── base.py                # Base CRUD operations
│   └── document.py            # Document-specific CRUD operations
├── 📁 endpoints/               # FastAPI route handlers
│   ├── health.py              # Health check endpoints
│   ├── scraping.py            # Web scraping endpoints
│   └── search.py              # Search endpoints
├── 📁 services/                # Business logic services
│   ├── data_processing/       # Data cleaning and processing
│   ├── embeddings/            # Embedding generation services
│   ├── storage/               # Storage backends (local/cloud)
│   ├── vector_store/          # Vector database handlers
│   └── web_scraper/           # Web scraping implementations
├── 📁 alembic/                 # Database migrations
├── main.py                    # Original application entry point
├── main_new.py               # Refactored application entry point
├── pyproject.toml            # Project dependencies and metadata
└── .env.example              # Environment configuration template
```

## 🏗️ Architecture Improvements Made

### 1. **Configuration Management**
- **Before**: Hard-coded configurations scattered throughout the code
- **After**: Centralized configuration in `core/config.py` using Pydantic Settings
- **Benefits**: Environment-based configuration, type validation, easy testing

### 2. **Dependency Injection**
- **Before**: Direct instantiation of services in endpoints
- **After**: Proper dependency injection pattern in `core/deps.py`
- **Benefits**: Better testability, loose coupling, easier mocking

### 3. **Exception Handling**
- **Before**: Generic exception handling with basic error messages
- **After**: Custom exception hierarchy in `core/exceptions.py`
- **Benefits**: Structured error responses, better debugging, consistent error handling

### 4. **Database Models**
- **Before**: No database models, data stored only in files
- **After**: Proper SQLAlchemy models for documents and vector indices
- **Benefits**: Data integrity, relationships, query optimization

### 5. **API Structure**
- **Before**: All endpoints in single `main.py` file
- **After**: Modular router structure with proper API versioning
- **Benefits**: Better organization, easier maintenance, clear API versioning

### 6. **CRUD Operations**
- **Before**: No structured database operations
- **After**: Generic CRUD base class with model-specific operations
- **Benefits**: Consistent database access, reduced code duplication

### 7. **Data Processing**
- **Before**: Basic data cleaning function
- **After**: Comprehensive data processing with Arabic text support
- **Benefits**: Better text processing, metadata extraction, chunking support

## 🚀 Quick Start Guide

### 1. Environment Setup
```bash
# Copy environment template
cp .env.example .env

# Edit .env with your configurations
# Set STORAGE_BACKEND, VECTOR_BACKEND, etc.
```

### 2. Install Dependencies
```bash
pip install -e .
```

### 3. Database Setup (Optional)
```bash
# Set DATABASE_URL in .env if using database
alembic upgrade head
```

### 4. Run the Application
```bash
# Using the new refactored main
python main_new.py

# Or with uvicorn
uvicorn main_new:app --reload
```

## 🔧 Configuration Options

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

## 📚 API Documentation

Once running, visit:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### Key Endpoints:
- `GET /api/v1/health` - Health check
- `POST /api/v1/scrape` - Scrape website or upload file
- `GET /api/v1/search` - Search documents

## 🧪 Testing the Improvements

### 1. Health Check
```bash
curl http://localhost:8000/api/v1/health
```

### 2. Scrape Website
```bash
curl -X POST "http://localhost:8000/api/v1/scrape" \
  -F "url=https://ibtikar.org.tr/"
```

### 3. Search Documents
```bash
curl "http://localhost:8000/api/v1/search?q=إبتكار&top_k=5"
```

## 🏆 Benefits of New Structure

1. **Maintainability**: Clear separation of concerns
2. **Scalability**: Easy to add new features and endpoints
3. **Testability**: Dependency injection enables easy testing
4. **Configurability**: Environment-based configuration
5. **Error Handling**: Structured error responses
6. **Documentation**: Auto-generated API docs
7. **Type Safety**: Pydantic schemas for validation
8. **Database Support**: Optional database integration
9. **Monitoring**: Health check endpoints
10. **Production Ready**: Proper logging and exception handling

## 🔄 Migration Guide

To migrate from the old structure:

1. **Replace main.py** with `main_new.py`
2. **Update imports** to use new structure
3. **Configure environment** variables in `.env`
4. **Test endpoints** with new API structure
5. **Update client code** to use `/api/v1/` prefix

## 🐛 Troubleshooting

### Common Issues:
1. **Import Errors**: Ensure all dependencies are installed
2. **Configuration Errors**: Check `.env` file setup
3. **Database Errors**: Verify DATABASE_URL if using database
4. **Vector Store Errors**: Check VECTOR_BACKEND configuration

### Debugging:
- Set `DEBUG=true` in `.env` for verbose logging
- Check logs for detailed error information
- Use health check endpoint to verify service status

This restructured codebase follows FastAPI best practices and provides a solid foundation for scaling your Arabic RAG chatbot system.
