"""
This file is part of Abduallah Damash implementation
"""

import os
import json
import logging
from datetime import datetime
from azure.storage.blob import BlobServiceClient

class AzureBlobStorage:
    def __init__(self):
        self.connection_string = os.getenv("AZURE_BLOB_CONNECTION_STRING")
        self.container_name = os.getenv("AZURE_CONTAINER_NAME")
        self.blob_service_client = BlobServiceClient.from_connection_string(
            self.connection_string
        )

    def store_data(self, data):
        """
        Store data as a JSON file in Azure Blob Storage.
        Appends new data to an existing blob if it exists.
        """
        if not data:
            return

        blob_name = f"scraped_data_{datetime.now()}.json"
        container_client = self.blob_service_client.get_container_client(self.container_name)

        existing_data = []
        try:
            blob_client = container_client.get_blob_client(blob_name)
            downloaded_blob = blob_client.download_blob().readall()
            existing_data = json.loads(downloaded_blob.decode("utf-8"))
        except Exception:
            # If blob doesn't exist or can't be read, start fresh
            pass

        existing_data.extend(data)
        blob_content = json.dumps(existing_data, indent=2, ensure_ascii=False)
        container_client.upload_blob(
            name=blob_name,
            data=blob_content,
            overwrite=True
        )

        logging.info(f"[AzureBlobStorage] Stored {len(data)} items at {datetime.now()}")
