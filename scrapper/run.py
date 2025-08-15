#!/usr/bin/env python3
"""
Run script for the Ibtikar Chatbot Scrapper.
This script sets up the environment and runs the application.
"""
import os
import sys
from pathlib import Path

# Add current directory to Python path
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

def main():
    """Main entry point."""
    try:
        # Import and run the FastAPI app
        from main_new import app
        import uvicorn
        
        print("🚀 Starting Ibtikar Chatbot Scrapper...")
        print(f"📁 Working directory: {current_dir}")
        print("🌐 Server will be available at: http://localhost:8000")
        print("📚 API Documentation: http://localhost:8000/docs")
        print("=" * 50)
        
        # Run the application
        uvicorn.run(
            "main_new:app",
            host="0.0.0.0",
            port=8000,
            reload=True,
            log_level="info"
        )
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("💡 Make sure to install dependencies first:")
        print("   pip install -e .")
        print("   or")
        print("   pip install -r requirements-core.txt")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error starting application: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
