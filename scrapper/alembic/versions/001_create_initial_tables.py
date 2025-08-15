"""create_initial_tables

Revision ID: 001
Revises: 
Create Date: 2025-01-01 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create documents table
    op.create_table('documents',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
    sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('title', sa.String(length=500), nullable=False),
    sa.Column('content', sa.Text(), nullable=False),
    sa.Column('url', sa.String(length=2000), nullable=False),
    sa.Column('content_type', sa.String(length=100), nullable=True),
    sa.Column('language', sa.String(length=10), nullable=True),
    sa.Column('word_count', sa.Integer(), nullable=True),
    sa.Column('is_processed', sa.Boolean(), nullable=True),
    sa.Column('is_indexed', sa.Boolean(), nullable=True),
    sa.Column('metadata', sa.JSON(), nullable=True),
    sa.Column('scraped_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
    sa.Column('processed_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('indexed_at', sa.DateTime(timezone=True), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_documents_id'), 'documents', ['id'], unique=False)
    op.create_index(op.f('ix_documents_url'), 'documents', ['url'], unique=False)

    # Create vector_indices table
    op.create_table('vector_indices',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
    sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('document_id', sa.Integer(), nullable=False),
    sa.Column('vector_id', sa.String(length=100), nullable=False),
    sa.Column('chunk_index', sa.Integer(), nullable=True),
    sa.Column('chunk_text', sa.Text(), nullable=False),
    sa.Column('vector_store_type', sa.String(length=50), nullable=False),
    sa.Column('namespace', sa.String(length=100), nullable=True),
    sa.Column('embedding_model', sa.String(length=100), nullable=True),
    sa.Column('embedding_dimension', sa.Integer(), nullable=True),
    sa.Column('similarity_threshold', sa.Float(), nullable=True),
    sa.Column('metadata', sa.JSON(), nullable=True),
    sa.ForeignKeyConstraint(['document_id'], ['documents.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_vector_indices_id'), 'vector_indices', ['id'], unique=False)
    op.create_index(op.f('ix_vector_indices_vector_id'), 'vector_indices', ['vector_id'], unique=True)


def downgrade() -> None:
    op.drop_index(op.f('ix_vector_indices_vector_id'), table_name='vector_indices')
    op.drop_index(op.f('ix_vector_indices_id'), table_name='vector_indices')
    op.drop_table('vector_indices')
    op.drop_index(op.f('ix_documents_url'), table_name='documents')
    op.drop_index(op.f('ix_documents_id'), table_name='documents')
    op.drop_table('documents')
