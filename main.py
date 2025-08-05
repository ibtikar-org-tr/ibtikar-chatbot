"""
FastAPI Main Application

This is the main entry point for the Ibtikar Community RAG Chatbot API.
"""

from fastapi import FastAPI

# Initialize FastAPI application
app = FastAPI(
    title="Ibtikar Community RAG Chatbot",
    description="Arabic-first RAG chatbot system for university students",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

@app.get("/")
async def root():
    """Root endpoint - Health check"""
    return {
        "message": "مرحباً بكم في نظام الدردشة الذكي لمجتمع إبتكار",
        "status": "active",
        "version": "0.1.0"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}
