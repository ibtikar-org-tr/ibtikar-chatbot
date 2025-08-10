"""
This file is part of Abduallah Damash implementation
"""

def clean_data(document):
    """
    Clean and preprocess a scraped document.
    For example, remove extra whitespace or perform text normalization.
    """
    cleaned_content = " ".join(document["content"].split())
    return {
        "url": document["url"],
        "content": cleaned_content
    }
