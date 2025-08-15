"""
CRUD operations for Document model.
"""
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc

from crud.base import CRUDBase
from models.document import Document
from schemas.api import DocumentCreate, DocumentUpdate


class CRUDDocument(CRUDBase[Document, DocumentCreate, DocumentUpdate]):
    """CRUD operations for Document model."""
    
    def get_by_url(self, db: Session, *, url: str) -> Optional[Document]:
        """Get document by URL."""
        return db.query(Document).filter(Document.url == url).first()
    
    def get_by_title(self, db: Session, *, title: str) -> Optional[Document]:
        """Get document by title."""
        return db.query(Document).filter(Document.title == title).first()
    
    def get_unprocessed(self, db: Session, *, limit: int = 100) -> List[Document]:
        """Get unprocessed documents."""
        return (
            db.query(Document)
            .filter(Document.is_processed == False)
            .limit(limit)
            .all()
        )
    
    def get_unindexed(self, db: Session, *, limit: int = 100) -> List[Document]:
        """Get unindexed documents."""
        return (
            db.query(Document)
            .filter(and_(Document.is_processed == True, Document.is_indexed == False))
            .limit(limit)
            .all()
        )
    
    def search_by_content(
        self, 
        db: Session, 
        *, 
        query: str, 
        limit: int = 10
    ) -> List[Document]:
        """Search documents by content (basic text search)."""
        return (
            db.query(Document)
            .filter(
                or_(
                    Document.title.contains(query),
                    Document.content.contains(query)
                )
            )
            .order_by(desc(Document.created_at))
            .limit(limit)
            .all()
        )
    
    def get_by_language(
        self, 
        db: Session, 
        *, 
        language: str, 
        skip: int = 0, 
        limit: int = 100
    ) -> List[Document]:
        """Get documents by language."""
        return (
            db.query(Document)
            .filter(Document.language == language)
            .offset(skip)
            .limit(limit)
            .all()
        )
    
    def mark_as_processed(self, db: Session, *, doc_id: int) -> Optional[Document]:
        """Mark document as processed."""
        doc = self.get(db, doc_id)
        if doc:
            doc.is_processed = True
            db.commit()
            db.refresh(doc)
        return doc
    
    def mark_as_indexed(self, db: Session, *, doc_id: int) -> Optional[Document]:
        """Mark document as indexed."""
        doc = self.get(db, doc_id)
        if doc:
            doc.is_indexed = True
            db.commit()
            db.refresh(doc)
        return doc


# Create instance
document = CRUDDocument(Document)
