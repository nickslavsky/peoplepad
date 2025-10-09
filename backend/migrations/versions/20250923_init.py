"""Initial migration for PeoplePad

Revision ID: 20250923_init
Revises:
Create Date: 2025-09-23 00:00:00
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
from pgvector.sqlalchemy import Vector

revision = '20250923_init'
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    # Enable extensions
    op.execute('CREATE EXTENSION IF NOT EXISTS "uuid-ossp"')
    op.execute('CREATE EXTENSION IF NOT EXISTS "vector"')
    op.execute('CREATE EXTENSION IF NOT EXISTS "pg_trgm"')

    # Create users table
    op.create_table(
        'users',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('uuid_generate_v4()')),
        sa.Column('email', sa.String, nullable=False, unique=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    # Create records table
    op.create_table(
        'records',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('uuid_generate_v4()')),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('name', sa.String, nullable=False),
        sa.Column('notes', sa.String, nullable=True),
        sa.Column('embedding', Vector(1536), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now()),
    )

    # Create tags table
    op.create_table(
        'tags',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('uuid_generate_v4()')),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('name', sa.String, nullable=False),
        sa.UniqueConstraint('user_id', 'name'),
    )

    # Create record_tags table
    op.create_table(
        'record_tags',
        sa.Column('record_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('records.id'), primary_key=True),
        sa.Column('tag_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('tags.id'), primary_key=True),
    )

def downgrade():
    op.drop_table('record_tags')
    op.drop_table('tags')
    op.drop_table('records')
    op.drop_table('users')
    op.execute('DROP EXTENSION IF EXISTS "pg_trgm"')
    op.execute('DROP EXTENSION IF EXISTS "pgvector"')
    op.execute('DROP EXTENSION IF EXISTS "uuid-ossp"')