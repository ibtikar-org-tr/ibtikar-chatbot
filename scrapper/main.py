"""
FastAPI Main Application

This is the main entry point for the Ibtikar Community RAG Chatbot API.
"""
import os
import sys
import asyncio
import logging
from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from pydantic import BaseModel
from dotenv import load_dotenv
import uuid

from services.web_scraper.scraper import WebScraper
from services.data_processing.data_cleaner import clean_data
from services.storage.local_storage import LocalStorage
from services.storage.cloud_storage import AzureBlobStorage
from services.vector_store.faiss_store import FaissStore
from services.vector_store.vector_store_handler import VectorStoreHandler
from services.vector_store.upstash_store import get_vector_index

# Set event loop policy on Windows to avoid NotImplementedError with subprocess
if sys.platform.startswith("win"):
    policy = asyncio.WindowsProactorEventLoopPolicy()
    asyncio.set_event_loop_policy(policy)

load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s'
)

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


# STORAGE setup
STORAGE_BACKEND = os.getenv("STORAGE_BACKEND", "local")
if STORAGE_BACKEND == "local":
    storage = LocalStorage()
elif STORAGE_BACKEND == "azure":
    storage = AzureBlobStorage()
else:
    raise ValueError("Unsupported STORAGE_BACKEND specified.")

# VECTOR store setup
VECTOR_BACKEND = os.getenv("VECTOR_BACKEND", "faiss")
if VECTOR_BACKEND == "faiss":
    vector_store = FaissStore()
else:
    vector_store = VectorStoreHandler()  # Could handle other backends

class ScrapeRequest(BaseModel):
    url: str = Form(None),
    file: UploadFile = File(None)

@app.post("/v1/scrape")
async def scrape_website(file: UploadFile = File(None), url: str = Form(None)):
    """
    Scrape a website starting from the given URL, store the data,
    and index it in a vector store if applicable.
    - Uses environment variable SCRAPE_BACKEND to decide whether to:
      * Use requests (sync)
      * Use Selenium (sync)
      * Use Playwright (async)
    - Also extracts PDF text content when encountered,
    skipping other non-text media.
    """
    try:
        scraper = WebScraper()

        documents = []

        if file is not None:
            contents = await file.read()
            from io import BytesIO
            import docx

            try:
                doc = docx.Document(BytesIO(contents))
                text = "\n".join([p.text for p in doc.paragraphs])
                documents.append({"url": file.filename, "content": text})
            except Exception as e:
                raise HTTPException(status_code=400, detail=f"File processing error: {e}")

        if url:
            raw_data = await scraper.scrape_website(url)
            cleaned_docs = [clean_data(doc) for doc in raw_data]
            documents.extend(cleaned_docs)

        if not documents:
            raise HTTPException(status_code=400, detail="No URL or file provided.")

        # Store data
        storage.store_data(cleaned_docs)

        # Add to vector store
        vector_store.add_documents(cleaned_docs)

        return {"message": f"Scraped and stored data from {url}."}
    except Exception as e:
        logging.error(f"Error in /scrape: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/v1/search")
async def search(q: str):
    """
    Perform a vector search for the user query.
    """
    try:
        results = vector_store.search(q)
        return {"query": q, "results": results}
    except Exception as e:
        logging.error(f"Error in /search: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))



@app.post("/v1/scrape_ibtkar")
async def scrape_predefined_websites():
    """
    Scrapes predefined URLs, cleans the data, and stores it in Upstash Vector DB.
    """
    BATCH_SIZE = 10
    CHUNK_SIZE = 500
    TARGET_URLS = [
        "https://ibtikar.org.tr/",
        "https://github.com/ibtikar-org-tr/bylaws/blob/main/README.md",
        "https://github.com/ibtikar-org-tr/bylaws/blob/main/FAQ.md",
        "https://github.com/ibtikar-org-tr/bylaws/blob/main/TEKNOFEST_ar/README.md",
        "https://github.com/ibtikar-org-tr/bylaws/blob/main/TEKNOFEST_ar/TAP_RT.md",
    ]
    try:
        scraper = WebScraper()
        all_documents = []

        for url in TARGET_URLS:
            raw_data = await scraper.scrape_website(url)
            cleaned_docs = [clean_data(doc) for doc in raw_data if doc.get("content")]
            all_documents.extend(cleaned_docs)

        if not all_documents:
            raise HTTPException(status_code=400, detail="No data scraped from target URLs.")

        vector_index = get_vector_index()
        vectors = []

        # Dokümanları chunk’la ve embedding oluştur
        for doc in all_documents:
            content = doc.get("content", "")
            url = doc.get("url", "")
            title = doc.get("title", "")

            # Metni CHUNK_SIZE karakterlik parçalara böl
            for i in range(0, len(content), CHUNK_SIZE):
                chunk_text = content[i:i+CHUNK_SIZE]
                if not chunk_text.strip():
                    continue

                vector = vector_index.embedding_client.embed_document(chunk_text)
                vectors.append({
                    "id": str(uuid.uuid4()),
                    "vector": vector,
                    "metadata": {"url": url, "title": title, "chunk_index": i // CHUNK_SIZE}
                })

        # Batch’ler halinde Upstash’a gönder
        for i in range(0, len(vectors), BATCH_SIZE):
            batch = vectors[i:i+BATCH_SIZE]
            await vector_index.upsert_vectors("my_namespace", batch)

        return {"message": f"Scraped and stored {len(all_documents)} documents in chunks from predefined URLs."}

    except Exception as e:
        logging.error(f"Error in /v1/scrape_ibtkar: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))