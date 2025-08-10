from .local_storage import LocalStorage
from .cloud_storage import AzureBlobStorage

# Export LocalStorage directly
__all__ = ["LocalStorage"
           "AzureBlobStorage"]
