"""
Test script to validate the new project structure.
"""
import asyncio
import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

async def test_imports():
    """Test that all new modules can be imported successfully."""
    
    print("🧪 Testing imports...")
    
    try:
        # Test core modules
        from core.config import settings
        from core.deps import get_settings, get_storage, get_vector_store
        from core.exceptions import IbtikarChatbotException
        from core.logging import setup_logging, get_logger
        print("✅ Core modules imported successfully")
        
        # Test models
        from models.base import Base
        from models.document import Document
        from models.vector_index import VectorIndex
        print("✅ Models imported successfully")
        
        # Test schemas
        from schemas.api import (
            DocumentCreate, DocumentResponse, 
            ScrapeRequest, ScrapeResponse,
            SearchRequest, SearchResponse
        )
        print("✅ Schemas imported successfully")
        
        # Test CRUD
        from crud.document import document
        print("✅ CRUD operations imported successfully")
        
        # Test endpoints
        from endpoints import scraping, search, health
        print("✅ Endpoints imported successfully")
        
        # Test enhanced services
        from services.data_processing.data_cleaner_enhanced import clean_data, chunk_document
        print("✅ Enhanced services imported successfully")
        
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False


async def test_configuration():
    """Test configuration loading."""
    
    print("\n⚙️ Testing configuration...")
    
    try:
        from core.config import settings
        
        # Test basic settings
        assert settings.APP_NAME == "Ibtikar Community RAG Chatbot"
        assert settings.API_V1_PREFIX == "/api/v1"
        assert settings.STORAGE_BACKEND in ["local", "azure"]
        assert settings.VECTOR_BACKEND in ["faiss", "upstash"]
        
        print(f"✅ App Name: {settings.APP_NAME}")
        print(f"✅ API Prefix: {settings.API_V1_PREFIX}")
        print(f"✅ Storage Backend: {settings.STORAGE_BACKEND}")
        print(f"✅ Vector Backend: {settings.VECTOR_BACKEND}")
        print(f"✅ Embedding Model: {settings.EMBEDDING_MODEL}")
        
        return True
        
    except Exception as e:
        print(f"❌ Configuration error: {e}")
        return False


async def test_data_processing():
    """Test enhanced data processing."""
    
    print("\n📊 Testing data processing...")
    
    try:
        from services.data_processing.data_cleaner_enhanced import clean_data, chunk_document
        
        # Test document
        test_doc = {
            "title": "Test Document   ",
            "content": "This is a test document with some <b>HTML</b> content and extra   spaces.",
            "url": "https://example.com/test",
            "metadata": {}
        }
        
        # Test cleaning
        cleaned = clean_data(test_doc)
        assert "Test Document" in cleaned["title"]
        assert "<b>" not in cleaned["content"]
        assert "metadata" in cleaned
        print("✅ Document cleaning works")
        
        # Test chunking
        chunks = chunk_document(cleaned, chunk_size=50, overlap=10)
        assert len(chunks) > 0
        assert all(chunk["chunk_index"] >= 0 for chunk in chunks)
        print(f"✅ Document chunking works (created {len(chunks)} chunks)")
        
        return True
        
    except Exception as e:
        print(f"❌ Data processing error: {e}")
        return False


async def test_fastapi_app():
    """Test FastAPI application creation."""
    
    print("\n🚀 Testing FastAPI application...")
    
    try:
        from main_new import app
        
        # Test app creation
        assert app.title == "Ibtikar Community RAG Chatbot"
        assert app.version == "0.1.0"
        
        # Test routes
        routes = [route.path for route in app.routes]
        expected_routes = ["/", "/api/v1/health", "/api/v1/scrape", "/api/v1/search"]
        
        for expected_route in expected_routes:
            # Check if route exists (may have slight variations)
            route_exists = any(expected_route in route for route in routes)
            if route_exists:
                print(f"✅ Route found: {expected_route}")
            else:
                print(f"⚠️ Route not found exactly: {expected_route}")
        
        print("✅ FastAPI application created successfully")
        return True
        
    except Exception as e:
        print(f"❌ FastAPI application error: {e}")
        return False


async def main():
    """Run all tests."""
    
    print("🔍 Ibtikar Chatbot - Structure Validation Test")
    print("=" * 50)
    
    tests = [
        ("Import Test", test_imports),
        ("Configuration Test", test_configuration), 
        ("Data Processing Test", test_data_processing),
        ("FastAPI Application Test", test_fastapi_app),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n🧪 Running {test_name}...")
        try:
            result = await test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} failed with exception: {e}")
            results.append((test_name, False))
    
    print("\n" + "=" * 50)
    print("📋 Test Results Summary:")
    print("=" * 50)
    
    passed = 0
    for test_name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\nTotal: {passed}/{len(results)} tests passed")
    
    if passed == len(results):
        print("🎉 All tests passed! Your project structure is working correctly.")
        return True
    else:
        print("⚠️ Some tests failed. Please check the errors above.")
        return False


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
