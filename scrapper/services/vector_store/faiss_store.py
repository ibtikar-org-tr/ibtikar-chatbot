"""
This file is part of Abduallah Damash implementation
"""

import faiss
import numpy as np

class FaissStore:
    def __init__(self):
        self.index = None
        self.documents = []
        self.dimension = 512  # Example dimension; adjust as needed

    def add_documents(self, docs):
        """
        Convert each doc's content into a vector, then add these vectors to the FAISS index.
        """
        if not docs:
            return

        vectors = []
        for doc in docs:
            vector = self._embed(doc["content"])
            vectors.append(vector)
            self.documents.append(doc)

        vectors_np = np.array(vectors).astype(np.float32)

        if self.index is None:
            self.index = faiss.IndexFlatL2(self.dimension)
        self.index.add(vectors_np)

    def search(self, query, k=5):
        """
        Embed the query, then retrieve top k results from FAISS.
        """
        if self.index is None:
            return []

        query_vec = np.array([self._embed(query)], dtype=np.float32)
        distances, indices = self.index.search(query_vec, k)
        results = []
        for dist, idx in zip(distances[0], indices[0]):
            if idx < len(self.documents):
                doc = self.documents[idx]
                results.append({
                    "url": doc["url"],
                    "content": doc["content"],
                    "distance": float(dist)
                })
        return results

    def _embed(self, text):
        """
        Placeholder for text->vector embedding. 
        Replace with a real model for production usage.
        """
        vec = np.zeros(self.dimension, dtype=np.float32)
        for i, ch in enumerate(text[: self.dimension]):
            vec[i] = float(ord(ch) % 256) / 256.0
        return vec
