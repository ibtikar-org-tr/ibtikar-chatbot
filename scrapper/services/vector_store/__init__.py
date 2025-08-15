"""
Vector store implementations with graceful dependency handling.
"""

# Import with graceful failure handling
try:
    from .faiss_store import FaissStore
    FAISS_AVAILABLE = True
except ImportError:
    FaissStore = None
    FAISS_AVAILABLE = False

try:
    from .upstash_store import UpstashVectorIndex, get_vector_index
    UPSTASH_AVAILABLE = True
except ImportError:
    UpstashVectorIndex = None
    get_vector_index = None
    UPSTASH_AVAILABLE = False

from .vector_store_handler import VectorStoreHandler

# Export available components
__all__ = ["VectorStoreHandler"]

if FAISS_AVAILABLE:
    __all__.append("FaissStore")

if UPSTASH_AVAILABLE:
    __all__.extend(["UpstashVectorIndex", "get_vector_index"])
