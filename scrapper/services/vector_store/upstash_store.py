import logging
from typing import List, Dict, Optional, Any
from dotenv import load_dotenv
import os
import httpx
from services.embeddings.bge_client import get_embedding_client

load_dotenv()

UPSTASH_VECTOR_REST_URL = os.getenv("UPSTASH_VECTOR_REST_URL", "").rstrip("/")
UPSTASH_VECTOR_REST_TOKEN = os.getenv("UPSTASH_VECTOR_REST_TOKEN", "")
UPSTASH_VECTOR_REST_READONLY_TOKEN = os.getenv("UPSTASH_VECTOR_REST_READONLY_TOKEN", "")

logger = logging.getLogger(__name__)

# Basit özel hata sınıfı
class VectorIndexError(Exception):
    def __init__(self, message: str, error_code: str = "VECTOR_ERROR"):
        super().__init__(message)
        self.error_code = error_code


class UpstashVectorIndex:
    """Client for Upstash Vector database"""
    
    def __init__(
        self,
        rest_url: str = None,
        rest_token: str = None,
        readonly_token: str = None
    ):
        self.rest_url = (rest_url or UPSTASH_VECTOR_REST_URL).rstrip('/')
        self.rest_token = rest_token or UPSTASH_VECTOR_REST_TOKEN
        self.readonly_token = readonly_token or UPSTASH_VECTOR_REST_READONLY_TOKEN
        
        if not self.rest_url or not self.rest_token:
            raise VectorIndexError("Upstash Vector URL and token are required", "MISSING_CREDENTIALS")
        
        self.embedding_client = get_embedding_client()
    
    def _get_headers(self, readonly: bool = False) -> Dict[str, str]:
        token = self.readonly_token if readonly and self.readonly_token else self.rest_token
        return {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "Accept": "application/json"
        }

    async def upsert_vector(
        self, 
        namespace: str, 
        vector_id: str, 
        vector: List[float], 
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Upsert a single vector to Upstash Vector store.
        
        Args:
            namespace: The namespace to upsert the vector to
            vector_id: Unique identifier for the vector
            vector: The vector values
            metadata: Optional metadata associated with the vector
        
        Returns:
            bool: True if successful
        """
        url = f"{self.rest_url}/upsert/{namespace}"
        
        # Create vector object
        vector_obj = {
            "id": vector_id,
            "vector": vector
        }
        
        if metadata:
            vector_obj["metadata"] = metadata
        
        # Send as array with single item (consistent with batch upsert)
        data = [vector_obj]
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                url, 
                headers=self._get_headers(), 
                json=data
            )
            
            if response.status_code not in [200, 201]:
                logger.error(f"Single vector upsert failed: {response.status_code} - {response.text}")
                raise VectorIndexError(
                    f"Upsert failed: {response.status_code} - {response.text}", 
                    "UPSERT_ERROR"
                )
        
        return True

    async def upsert_vectors(self, namespace: str, vectors: List[Dict[str, Any]]) -> bool:
        """
        Upsert multiple vectors to Upstash Vector store.
        
        Args:
            namespace: The namespace to upsert vectors to
            vectors: List of vector objects with 'id', 'vector', and optional 'metadata'
        
        Returns:
            bool: True if successful
        
        Raises:
            VectorIndexError: If upsert fails
        """
        url = f"{self.rest_url}/upsert/{namespace}"
        
        # Validate input vectors
        for vector_obj in vectors:
            if not vector_obj.get("id"):
                raise VectorIndexError("Vector id is required for all vectors", "VALIDATION_ERROR")
            if "vector" not in vector_obj and "sparseVector" not in vector_obj:
                raise VectorIndexError("Must include 'vector' or 'sparseVector' for all vectors", "VALIDATION_ERROR")
        
        # Split into chunks to avoid payload size issues
        CHUNK_SIZE = 1000  # Recommended max batch size
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            for i in range(0, len(vectors), CHUNK_SIZE):
                chunk = vectors[i:i+CHUNK_SIZE]
                
                logger.info(f"Upserting chunk {i//CHUNK_SIZE + 1}/{(len(vectors) + CHUNK_SIZE - 1)//CHUNK_SIZE} with {len(chunk)} vectors")
                
                # Send the array directly, not wrapped in {"vectors": ...}
                response = await client.post(
                    url, 
                    headers=self._get_headers(), 
                    json=chunk  # ✅ Send array directly, not wrapped
                )
                
                if response.status_code not in [200, 201]:
                    logger.error(f"Batch upsert failed for chunk: {response.status_code} - {response.text}")
                    raise VectorIndexError(
                        f"Batch upsert failed: {response.status_code} - {response.text}", 
                        "BATCH_UPSERT_ERROR"
                    )
                
                logger.info(f"Successfully upserted chunk with {len(chunk)} vectors")
        
        return True

    async def query_namespace(
        self, 
        namespace: str, 
        vector: List[float], 
        top_k: int = 5, 
        include_metadata: bool = True, 
        include_values: bool = False, 
        filter_metadata: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Query vectors from a namespace.
        
        Args:
            namespace: The namespace to query
            vector: Query vector
            top_k: Number of results to return
            include_metadata: Whether to include metadata in results
            include_values: Whether to include vector values in results
            filter_metadata: Optional metadata filter
        
        Returns:
            List of matching vectors with scores and metadata
        """
        url = f"{self.rest_url}/query/{namespace}"
        
        data = {
            "vector": vector,
            "topK": top_k,
            "includeMetadata": include_metadata,
            "includeVectors": include_values,  # ✅ Corrected key name
        }
        
        # Handle filter metadata - convert dict to string expression if needed
        if filter_metadata:
            if isinstance(filter_metadata, dict):
                # Convert dict to Upstash filter string format
                filter_expressions = []
                for key, value in filter_metadata.items():
                    if isinstance(value, str):
                        filter_expressions.append(f"{key} = '{value}'")
                    elif isinstance(value, (int, float)):
                        filter_expressions.append(f"{key} = {value}")
                    elif isinstance(value, bool):
                        filter_expressions.append(f"{key} = {str(value).lower()}")
                    else:
                        filter_expressions.append(f"{key} = '{str(value)}'")
                
                data["filter"] = " AND ".join(filter_expressions)
            else:
                # Assume it's already a string expression
                data["filter"] = str(filter_metadata)
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                url, 
                headers=self._get_headers(readonly=True), 
                json=data
            )
            
            if response.status_code == 404:
                logger.warning(f"Namespace '{namespace}' not found")
                return []
            
            if response.status_code != 200:
                logger.error(f"Query failed: {response.status_code} - {response.text}")
                raise VectorIndexError(
                    f"Query failed: {response.status_code} - {response.text}", 
                    "QUERY_ERROR"
                )
            
            result = response.json()
            return result.get("result", [])

    async def query_by_text(
        self, 
        namespace: str, 
        text: str, 
        top_k: int = 5, 
        include_metadata: bool = True, 
        filter_metadata: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Query vectors using text (will be embedded automatically).
        
        Args:
            namespace: The namespace to query
            text: Text to embed and search with
            top_k: Number of results to return
            include_metadata: Whether to include metadata in results
            filter_metadata: Optional metadata filter
        
        Returns:
            List of matching vectors with scores and metadata
        """
        try:
            query_vector = self.embedding_client.embed_query(text)
            return await self.query_namespace(
                namespace=namespace,
                vector=query_vector,
                top_k=top_k,
                include_metadata=include_metadata,
                include_values=False,  # Usually not needed for text queries
                filter_metadata=filter_metadata
            )
        except Exception as e:
            logger.error(f"Text query failed: {e}")
            raise VectorIndexError(f"Text query failed: {e}", "TEXT_QUERY_ERROR")

    async def delete_vector(self, namespace: str, vector_id: str) -> bool:
        """
        Delete a vector from the namespace.
        
        Args:
            namespace: The namespace containing the vector
            vector_id: ID of the vector to delete
        
        Returns:
            bool: True if successful (or vector didn't exist)
        """
        url = f"{self.rest_url}/delete/{namespace}/{vector_id}"
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.delete(url, headers=self._get_headers())
            
            if response.status_code not in [200, 404]:
                logger.error(f"Delete failed: {response.status_code} - {response.text}")
                raise VectorIndexError(
                    f"Delete failed: {response.status_code} - {response.text}", 
                    "DELETE_ERROR"
                )
        
        return True

    async def delete_namespace(self, namespace: str) -> bool:
        """
        Delete an entire namespace and all its vectors.
        
        Args:
            namespace: The namespace to delete
        
        Returns:
            bool: True if successful
        """
        url = f"{self.rest_url}/delete/{namespace}"
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.delete(url, headers=self._get_headers())
            
            if response.status_code not in [200, 404]:
                logger.error(f"Namespace delete failed: {response.status_code} - {response.text}")
                raise VectorIndexError(
                    f"Namespace delete failed: {response.status_code} - {response.text}", 
                    "NAMESPACE_DELETE_ERROR"
                )
        
        return True

    def is_available(self) -> bool:
        """Check if the Upstash Vector service is available."""
        return bool(
            self.rest_url and 
            self.rest_token and 
            self.embedding_client.is_available()
        )

    def get_index_info(self) -> Dict[str, Any]:
        """Get information about the vector index configuration."""
        return {
            "provider": "upstash_vector",
            "rest_url": self.rest_url,
            "embedding_model": self.embedding_client.get_model_info(),
            "available": self.is_available()
        }

    async def get_namespace_info(self, namespace: str) -> Dict[str, Any]:
        """
        Get information about a specific namespace.
        
        Args:
            namespace: The namespace to get info for
        
        Returns:
            Dict with namespace information
        """
        url = f"{self.rest_url}/info/{namespace}"
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(url, headers=self._get_headers(readonly=True))
                
                if response.status_code == 404:
                    return {"exists": False, "namespace": namespace}
                
                if response.status_code == 200:
                    info = response.json()
                    info["exists"] = True
                    info["namespace"] = namespace
                    return info
                
                logger.warning(f"Unexpected response for namespace info: {response.status_code}")
                return {"exists": False, "namespace": namespace, "error": response.text}
                
        except Exception as e:
            logger.error(f"Failed to get namespace info: {e}")
            return {"exists": False, "namespace": namespace, "error": str(e)}


_vector_index: Optional[UpstashVectorIndex] = None


def get_vector_index() -> UpstashVectorIndex:
    """Get or create the global vector index"""
    global _vector_index
    
    if _vector_index is None:
        _vector_index = UpstashVectorIndex()
    
    return _vector_index