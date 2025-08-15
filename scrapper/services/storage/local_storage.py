"""
This file is part of Abduallah Damash implementation
"""

import json
import os
import logging
from datetime import datetime

class LocalStorage:
    def __init__(self, filename="scraped_data.json"):
        self.filename = filename

    def store_data(self, data):
        """
        Store data locally as JSON. Appends to existing file.
        """
        if not data:
            return
        
        existing_data = []
        if os.path.exists(self.filename):
            with open(self.filename, "r", encoding="utf-8") as f:
                try:
                    existing_data = json.load(f)
                except json.JSONDecodeError:
                    existing_data = []

        existing_data.extend(data)
        with open(self.filename, "w", encoding="utf-8") as f:
            json.dump(existing_data, f, indent=2, ensure_ascii=False)

        logging.info(f"[LocalStorage] Stored {len(data)} items at {datetime.now()}")
