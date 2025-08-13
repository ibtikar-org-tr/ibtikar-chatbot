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

    async def upsert_vector(self, namespace: str, vector_id: str, vector: List[float], metadata: Optional[Dict[str, Any]] = None) -> bool:
        url = f"{self.rest_url}/upsert/{namespace}"
        data = {"id": vector_id, "vector": vector, "metadata": metadata or {}}
        async with httpx.AsyncClient() as client:
            response = await client.post(url, headers=self._get_headers(), json=data)
            if response.status_code not in [200, 201]:
                raise VectorIndexError(f"Upsert failed: {response.status_code} - {response.text}", "UPSERT_ERROR")
        return True

    async def upsert_vectors(self, namespace: str, vectors: List[Dict[str, Any]]) -> bool:
        url = f"{self.rest_url}/upsert/{namespace}"
        data = {"vectors": vectors}
        async with httpx.AsyncClient() as client:
            response = await client.post(url, headers=self._get_headers(), json=data)
            if response.status_code not in [200, 201]:
                raise VectorIndexError(f"Batch upsert failed: {response.status_code} - {response.text}", "BATCH_UPSERT_ERROR")
        return True

    async def query_namespace(self, namespace: str, vector: List[float], top_k: int = 5, include_metadata: bool = True, include_values: bool = False, filter_metadata: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        url = f"{self.rest_url}/query/{namespace}"
        data = {"vector": vector, "topK": top_k, "includeMetadata": include_metadata, "includeValues": include_values}
        if filter_metadata:
            data["filter"] = filter_metadata
        async with httpx.AsyncClient() as client:
            response = await client.post(url, headers=self._get_headers(readonly=True), json=data)
            if response.status_code == 404:
                return []
            if response.status_code != 200:
                raise VectorIndexError(f"Query failed: {response.status_code} - {response.text}", "QUERY_ERROR")
            return response.json().get("result", [])

    async def query_by_text(self, namespace: str, text: str, top_k: int = 5, include_metadata: bool = True, filter_metadata: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        query_vector = self.embedding_client.embed_query(text)
        return await self.query_namespace(namespace, query_vector, top_k, include_metadata, filter_metadata)

    async def delete_vector(self, namespace: str, vector_id: str) -> bool:
        url = f"{self.rest_url}/delete/{namespace}/{vector_id}"
        async with httpx.AsyncClient() as client:
            response = await client.delete(url, headers=self._get_headers())
            if response.status_code not in [200, 404]:
                raise VectorIndexError(f"Delete failed: {response.status_code} - {response.text}", "DELETE_ERROR")
        return True

    def is_available(self) -> bool:
        return bool(self.rest_url and self.rest_token and self.embedding_client.is_available())

    def get_index_info(self) -> Dict[str, Any]:
        return {"provider": "upstash_vector", "rest_url": self.rest_url, "embedding_model": self.embedding_client.get_model_info(), "available": self.is_available()}


_vector_index: Optional[UpstashVectorIndex] = None


def get_vector_index() -> UpstashVectorIndex:
    """Get or create the global vector index"""
    global _vector_index
    
    if _vector_index is None:
        _vector_index = UpstashVectorIndex()
    
    return _vector_index