"""
Scraping API endpoints.
"""
import asyncio
import time
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, BackgroundTasks
from sqlalchemy.orm import Session

from core.deps import get_storage, get_vector_store
from core.exceptions import ScrapingException, StorageException, VectorStoreException
from core.logging import get_logger
from schemas.api import ScrapeRequest, ScrapeResponse, DocumentResponse
from services.web_scraper.scraper import WebScraper
from services.data_processing.data_cleaner import clean_data

router = APIRouter()
logger = get_logger("scraping")


@router.post("/scrape", response_model=ScrapeResponse)
async def scrape_website(
    background_tasks: BackgroundTasks,
    file: Optional[UploadFile] = File(None),
    url: Optional[str] = Form(None),
    max_depth: Optional[int] = Form(3),
    max_pages: Optional[int] = Form(100),
    storage = Depends(get_storage),
    vector_store = Depends(get_vector_store)
):
    """
    Scrape a website or process uploaded file.
    
    - **file**: Upload a document file (docx, pdf, txt)
    - **url**: URL to scrape
    - **max_depth**: Maximum depth for web crawling
    - **max_pages**: Maximum number of pages to scrape
    """
    start_time = time.time()
    
    try:
        scraper = WebScraper()
        documents = []
        urls_scraped = []

        # Process uploaded file
        if file:
            logger.info(f"Processing uploaded file: {file.filename}")
            try:
                contents = await file.read()
                from io import BytesIO
                import docx

                doc = docx.Document(BytesIO(contents))
                text = "\n".join([p.text for p in doc.paragraphs])
                documents.append({
                    "title": file.filename,
                    "content": text,
                    "url": f"upload://{file.filename}",
                    "content_type": file.content_type
                })
                urls_scraped.append(f"upload://{file.filename}")
            except Exception as e:
                raise HTTPException(status_code=400, detail=f"File processing error: {e}")

        # Scrape URL
        if url:
            logger.info(f"Scraping URL: {url}")
            try:
                raw_data = await scraper.scrape_website(url)
                cleaned_docs = [clean_data(doc) for doc in raw_data if doc.get("content")]
                documents.extend(cleaned_docs)
                urls_scraped.extend([doc.get("url", "") for doc in cleaned_docs])
            except Exception as e:
                raise ScrapingException(f"Failed to scrape URL: {url}", url=url)

        if not documents:
            raise HTTPException(status_code=400, detail="No URL or file provided.")

        # Store and index documents in background
        background_tasks.add_task(
            process_documents_background,
            documents,
            storage,
            vector_store
        )

        processing_time = time.time() - start_time
        
        return ScrapeResponse(
            message=f"Successfully queued {len(documents)} documents for processing",
            documents_count=len(documents),
            urls_scraped=urls_scraped,
            processing_time=processing_time
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in scraping endpoint: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


async def process_documents_background(documents: List[dict], storage, vector_store):
    """Background task to process, store and index documents."""
    try:
        logger.info(f"Processing {len(documents)} documents in background")
        
        # Store documents
        for doc in documents:
            try:
                await storage.store_data([doc])
            except Exception as e:
                logger.error(f"Failed to store document {doc.get('url', 'unknown')}: {e}")
        
        # Index documents
        try:
            await vector_store.add_documents(documents)
        except Exception as e:
            logger.error(f"Failed to index documents: {e}")
            
        logger.info("Background processing completed")
        
    except Exception as e:
        logger.error(f"Error in background processing: {e}", exc_info=True)


@router.post("/scrape-predefined", response_model=ScrapeResponse)
async def scrape_predefined_websites(
    background_tasks: BackgroundTasks,
    storage = Depends(get_storage),
    vector_store = Depends(get_vector_store)
):
    """
    Scrape predefined Ibtikar community URLs.
    """
    TARGET_URLS = [
        "https://ibtikar.org.tr/",
        "https://github.com/ibtikar-org-tr/bylaws/blob/main/README.md",
        "https://github.com/ibtikar-org-tr/bylaws/blob/main/FAQ.md",
        "https://github.com/ibtikar-org-tr/bylaws/blob/main/TEKNOFEST_ar/README.md",
        "https://github.com/ibtikar-org-tr/bylaws/blob/main/TEKNOFEST_ar/TAP_RT.md",
    ]
    
    start_time = time.time()
    
    try:
        scraper = WebScraper()
        all_documents = []
        urls_scraped = []

        for url in TARGET_URLS:
            try:
                logger.info(f"Scraping predefined URL: {url}")
                raw_data = await scraper.scrape_website(url)
                cleaned_docs = [clean_data(doc) for doc in raw_data if doc.get("content")]
                all_documents.extend(cleaned_docs)
                urls_scraped.append(url)
            except Exception as e:
                logger.error(f"Failed to scrape {url}: {e}")
                continue

        if not all_documents:
            raise HTTPException(status_code=400, detail="No data scraped from target URLs.")

        # Process documents in background
        background_tasks.add_task(
            process_documents_background,
            all_documents,
            storage,
            vector_store
        )

        processing_time = time.time() - start_time
        
        return ScrapeResponse(
            message=f"Successfully queued {len(all_documents)} documents from predefined URLs",
            documents_count=len(all_documents),
            urls_scraped=urls_scraped,
            processing_time=processing_time
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in predefined scraping: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))
