"""
Simple script to test the scrapper application.
Run this from the scrapper directory.
"""
import sys
import asyncio
from pathlib import Path

# Add current directory to Python path
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

async def test_basic_imports():
    """Test basic imports from the scrapper directory."""
    print("🧪 Testing basic imports from scrapper directory...")
    
    try:
        # Test core imports
        from core.config import settings
        print(f"✅ Core config loaded: {settings.APP_NAME}")
        
        # Test data processing
        from services.data_processing.data_cleaner_enhanced import clean_data
        test_doc = {
            "title": "Test Document",
            "content": "This is a test.",
            "url": "https://test.com"
        }
        cleaned = clean_data(test_doc)
        print("✅ Data processing working")
        
        # Test FastAPI app
        from main_new import app
        print(f"✅ FastAPI app loaded: {app.title}")
        
        return True
        
    except Exception as e:
        print(f"❌ Import error: {e}")
        return False

async def main():
    """Run the test."""
    print("🔍 Scrapper Directory Test")
    print("=" * 30)
    
    success = await test_basic_imports()
    
    if success:
        print("\n🎉 All basic tests passed!")
        print("✅ You can now run the application with:")
        print("   python main_new.py")
    else:
        print("\n❌ Some tests failed. Check dependencies.")
    
    return success

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
