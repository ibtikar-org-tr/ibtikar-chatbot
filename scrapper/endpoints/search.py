"""
Search API endpoints.
"""
import time
from typing import List
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from core.deps import get_vector_store
from core.exceptions import VectorStoreException
from core.logging import get_logger
from schemas.api import SearchRequest, SearchResponse, SearchResult

router = APIRouter()
logger = get_logger("search")


@router.get("/search", response_model=SearchResponse)
async def search_documents(
    q: str = Query(..., description="Search query"),
    top_k: int = Query(10, ge=1, le=100, description="Number of results to return"),
    similarity_threshold: float = Query(0.7, ge=0.0, le=1.0, description="Minimum similarity score"),
    namespace: str = Query(None, description="Search namespace"),
    vector_store = Depends(get_vector_store)
):
    """
    Search documents using vector similarity.
    
    - **q**: Search query text
    - **top_k**: Maximum number of results to return (1-100)
    - **similarity_threshold**: Minimum similarity score (0.0-1.0)
    - **namespace**: Optional namespace to search within
    """
    start_time = time.time()
    
    try:
        logger.info(f"Searching for query: '{q}' with top_k={top_k}")
        
        # Perform vector search
        search_results = await vector_store.search(
            query=q,
            top_k=top_k,
            similarity_threshold=similarity_threshold,
            namespace=namespace
        )
        
        # Convert to response format
        results = []
        for result in search_results:
            search_result = SearchResult(
                document_id=result.get("document_id", 0),
                title=result.get("title", ""),
                content=result.get("content", ""),
                url=result.get("url", ""),
                similarity_score=result.get("similarity_score", 0.0),
                metadata=result.get("metadata", {})
            )
            results.append(search_result)
        
        processing_time = time.time() - start_time
        
        return SearchResponse(
            query=q,
            results=results,
            total_results=len(results),
            processing_time=processing_time
        )
        
    except VectorStoreException as e:
        logger.error(f"Vector store error during search: {e}")
        raise HTTPException(status_code=500, detail=f"Search failed: {e.message}")
    except Exception as e:
        logger.error(f"Error in search endpoint: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/search", response_model=SearchResponse)
async def search_documents_post(
    request: SearchRequest,
    vector_store = Depends(get_vector_store)
):
    """
    Search documents using vector similarity (POST version).
    
    Accepts a JSON payload with search parameters.
    """
    start_time = time.time()
    
    try:
        logger.info(f"POST search for query: '{request.query}' with top_k={request.top_k}")
        
        # Perform vector search
        search_results = await vector_store.search(
            query=request.query,
            top_k=request.top_k,
            similarity_threshold=request.similarity_threshold,
            namespace=request.namespace
        )
        
        # Convert to response format
        results = []
        for result in search_results:
            search_result = SearchResult(
                document_id=result.get("document_id", 0),
                title=result.get("title", ""),
                content=result.get("content", ""),
                url=result.get("url", ""),
                similarity_score=result.get("similarity_score", 0.0),
                metadata=result.get("metadata", {})
            )
            results.append(search_result)
        
        processing_time = time.time() - start_time
        
        return SearchResponse(
            query=request.query,
            results=results,
            total_results=len(results),
            processing_time=processing_time
        )
        
    except VectorStoreException as e:
        logger.error(f"Vector store error during search: {e}")
        raise HTTPException(status_code=500, detail=f"Search failed: {e.message}")
    except Exception as e:
        logger.error(f"Error in search endpoint: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))
