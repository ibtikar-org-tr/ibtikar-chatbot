"""
Enhanced data cleaning and processing utilities.
"""
import re
import html
from typing import Dict, List, Optional, Any
from urllib.parse import urlparse

from core.logging import get_logger
from core.exceptions import DataProcessingException

logger = get_logger("data_processing")


class DataCleaner:
    """Advanced data cleaning and processing."""
    
    def __init__(self):
        # Arabic text processing patterns
        self.arabic_diacritics = re.compile(r'[\u064B-\u065F\u0670\u0671]')
        self.extra_whitespace = re.compile(r'\s+')
        self.html_tags = re.compile(r'<[^>]+>')
        self.urls = re.compile(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+')
        self.emails = re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b')
        
    def clean_text(self, text: str, options: Optional[Dict[str, bool]] = None) -> str:
        """
        Clean and normalize text content.
        
        Args:
            text: Raw text content
            options: Cleaning options dict
                - remove_diacritics: Remove Arabic diacritics
                - normalize_whitespace: Normalize whitespace
                - remove_html: Remove HTML tags
                - remove_urls: Remove URLs
                - remove_emails: Remove email addresses
        """
        if not text or not isinstance(text, str):
            return ""
        
        # Default options
        opts = {
            'remove_diacritics': True,
            'normalize_whitespace': True,
            'remove_html': True,
            'remove_urls': False,
            'remove_emails': False,
            **(options or {})
        }
        
        try:
            # HTML decode
            text = html.unescape(text)
            
            # Remove HTML tags
            if opts['remove_html']:
                text = self.html_tags.sub(' ', text)
            
            # Remove URLs if requested
            if opts['remove_urls']:
                text = self.urls.sub(' ', text)
            
            # Remove emails if requested
            if opts['remove_emails']:
                text = self.emails.sub(' ', text)
            
            # Remove Arabic diacritics
            if opts['remove_diacritics']:
                text = self.arabic_diacritics.sub('', text)
            
            # Normalize whitespace
            if opts['normalize_whitespace']:
                text = self.extra_whitespace.sub(' ', text)
            
            # Strip and return
            return text.strip()
            
        except Exception as e:
            logger.error(f"Error cleaning text: {e}")
            raise DataProcessingException(f"Text cleaning failed: {e}", stage="clean_text")
    
    def extract_metadata(self, document: Dict[str, Any]) -> Dict[str, Any]:
        """Extract and enhance document metadata."""
        try:
            metadata = document.get('metadata', {})
            
            # Extract domain from URL
            url = document.get('url', '')
            if url:
                parsed_url = urlparse(url)
                metadata['domain'] = parsed_url.netloc
                metadata['path'] = parsed_url.path
            
            # Calculate content statistics
            content = document.get('content', '')
            if content:
                words = content.split()
                metadata['word_count'] = len(words)
                metadata['char_count'] = len(content)
                
                # Detect language (basic heuristic)
                arabic_chars = len(re.findall(r'[\u0600-\u06FF]', content))
                english_chars = len(re.findall(r'[a-zA-Z]', content))
                
                if arabic_chars > english_chars:
                    metadata['detected_language'] = 'ar'
                elif english_chars > 0:
                    metadata['detected_language'] = 'en'
                else:
                    metadata['detected_language'] = 'unknown'
            
            # Extract title if not present
            if not document.get('title') and content:
                lines = content.split('\n')
                for line in lines:
                    line = line.strip()
                    if line and len(line) < 200:  # Reasonable title length
                        metadata['extracted_title'] = line
                        break
            
            return metadata
            
        except Exception as e:
            logger.error(f"Error extracting metadata: {e}")
            return {}
    
    def chunk_text(
        self, 
        text: str, 
        chunk_size: int = 500, 
        overlap: int = 50,
        respect_sentences: bool = True
    ) -> List[str]:
        """
        Split text into chunks for embedding.
        
        Args:
            text: Text to chunk
            chunk_size: Maximum chunk size in characters
            overlap: Overlap between chunks in characters
            respect_sentences: Try to break at sentence boundaries
        """
        if not text:
            return []
        
        try:
            chunks = []
            
            if respect_sentences:
                # Split by sentences (basic approach)
                sentences = re.split(r'[.!?]+', text)
                current_chunk = ""
                
                for sentence in sentences:
                    sentence = sentence.strip()
                    if not sentence:
                        continue
                    
                    # If adding this sentence exceeds chunk_size, save current chunk
                    if len(current_chunk) + len(sentence) > chunk_size and current_chunk:
                        chunks.append(current_chunk.strip())
                        # Start new chunk with overlap
                        if overlap > 0:
                            words = current_chunk.split()
                            overlap_words = words[-overlap//10:]  # Approximate word overlap
                            current_chunk = ' '.join(overlap_words) + ' ' + sentence
                        else:
                            current_chunk = sentence
                    else:
                        current_chunk += ' ' + sentence if current_chunk else sentence
                
                # Add final chunk
                if current_chunk.strip():
                    chunks.append(current_chunk.strip())
            else:
                # Simple character-based chunking
                for i in range(0, len(text), chunk_size - overlap):
                    chunk = text[i:i + chunk_size]
                    if chunk.strip():
                        chunks.append(chunk.strip())
            
            return chunks
            
        except Exception as e:
            logger.error(f"Error chunking text: {e}")
            raise DataProcessingException(f"Text chunking failed: {e}", stage="chunk_text")


# Global instance
data_cleaner = DataCleaner()


def clean_data(document: Dict[str, Any], options: Optional[Dict[str, bool]] = None) -> Dict[str, Any]:
    """
    Clean and process a document.
    
    Args:
        document: Document dict with 'content', 'title', 'url', etc.
        options: Cleaning options
    
    Returns:
        Cleaned document dict
    """
    try:
        cleaned_doc = document.copy()
        
        # Clean content
        if 'content' in cleaned_doc:
            cleaned_doc['content'] = data_cleaner.clean_text(
                cleaned_doc['content'], 
                options
            )
        
        # Clean title
        if 'title' in cleaned_doc:
            title_options = {**(options or {}), 'remove_urls': True, 'remove_emails': True}
            cleaned_doc['title'] = data_cleaner.clean_text(
                cleaned_doc['title'], 
                title_options
            )
        
        # Extract and enhance metadata
        cleaned_doc['metadata'] = data_cleaner.extract_metadata(cleaned_doc)
        
        return cleaned_doc
        
    except Exception as e:
        logger.error(f"Error processing document: {e}")
        raise DataProcessingException(f"Document processing failed: {e}")


def chunk_document(
    document: Dict[str, Any], 
    chunk_size: int = 500, 
    overlap: int = 50
) -> List[Dict[str, Any]]:
    """
    Split a document into chunks for embedding.
    
    Args:
        document: Document dict
        chunk_size: Maximum chunk size
        overlap: Overlap between chunks
    
    Returns:
        List of document chunks
    """
    try:
        content = document.get('content', '')
        if not content:
            return []
        
        chunks = data_cleaner.chunk_text(content, chunk_size, overlap)
        
        chunked_docs = []
        for i, chunk in enumerate(chunks):
            chunk_doc = document.copy()
            chunk_doc['content'] = chunk
            chunk_doc['chunk_index'] = i
            chunk_doc['total_chunks'] = len(chunks)
            
            # Update metadata
            metadata = chunk_doc.get('metadata', {})
            metadata['is_chunk'] = True
            metadata['chunk_index'] = i
            metadata['total_chunks'] = len(chunks)
            chunk_doc['metadata'] = metadata
            
            chunked_docs.append(chunk_doc)
        
        return chunked_docs
        
    except Exception as e:
        logger.error(f"Error chunking document: {e}")
        raise DataProcessingException(f"Document chunking failed: {e}")
