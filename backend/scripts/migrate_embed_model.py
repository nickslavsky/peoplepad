"""
Migration script to re-embed records with a new embedding model.

Usage:
    docker exec -it peoplepad-backend python -m scripts.migrate_embed_model
"""

import asyncio
import httpx
from sqlalchemy import create_engine, select, text
from sqlalchemy.orm import sessionmaker
from typing import List, Dict, Any
import sys

# Import your models and settings
from app.models.record import Record
from app.config import settings

BATCH_SIZE = 100  # Max batch size supported by embedding service


async def get_embeddings_batch(
        client: httpx.AsyncClient,
        records: List[Dict[str, Any]]
) -> List[Dict[str, Any]]:
    """
    Get embeddings for a batch of records.

    Args:
        client: HTTPX async client
        records: List of dicts with 'id' and 'text' keys

    Returns:
        List of dicts with 'id' and 'embedding' from the service
    """
    batch_request = {
        "inputs": [{"id": str(r["id"]), "text": r["text"]} for r in records],
        "model": settings.embedding_model,
        "encoding_format": "float"
    }

    try:
        response = await client.post(
            f"{settings.embedding_service_url}/batch",
            headers={
                "Authorization": f"Bearer {settings.embedding_service_key}",
                "Content-Type": "application/json"
            },
            json=batch_request,
            timeout=30.0
        )
        response.raise_for_status()
        data = response.json()
        return data.get("data", [])
    except httpx.HTTPError as e:
        print(f"Error calling embedding service: {e}")
        raise


def update_embeddings_in_db(
        session,
        embeddings: List[Dict[str, Any]],
        column_name: str
):
    """
    Update the database with new embeddings.

    Args:
        session: SQLAlchemy session
        embeddings: List of dicts with 'id' and 'embedding'
        column_name: Name of the column to update
    """
    for item in embeddings:
        record_id = item["id"]
        embedding = item["embedding"]

        # Update the record with the new embedding
        stmt = (
            text(f"UPDATE records SET {column_name} = :embedding, updated_at = NOW() WHERE id = :id")
        )
        session.execute(stmt, {"embedding": embedding, "id": record_id})

    session.commit()


async def migrate_embeddings():
    """
    Main migration function.
    """
    # Determine the column name based on settings
    column_name = f"{settings.embedding_model.replace('-','_')}_embedding"

    print(f"Starting embedding migration to column: {column_name}")
    print(f"Using model: {settings.embedding_model}")

    # Create database engine and session
    engine = create_engine(settings.database_url)
    Session = sessionmaker(bind=engine)
    session = Session()

    try:
        # Find all records where the target embedding column is NULL
        stmt = text(f"""
            SELECT id, notes 
            FROM records 
            WHERE {column_name} IS NULL 
            AND notes IS NOT NULL 
            AND notes != ''
        """)

        result = session.execute(stmt)
        records_to_process = [
            {"id": row[0], "text": row[1]}
            for row in result.fetchall()
        ]

        total_records = len(records_to_process)
        print(f"Found {total_records} records to process")

        if total_records == 0:
            print("No records to migrate. Exiting.")
            return

        # Process in batches
        async with httpx.AsyncClient() as client:
            processed = 0

            for i in range(0, total_records, BATCH_SIZE):
                batch = records_to_process[i:i + BATCH_SIZE]
                batch_num = (i // BATCH_SIZE) + 1
                total_batches = (total_records + BATCH_SIZE - 1) // BATCH_SIZE

                print(f"Processing batch {batch_num}/{total_batches} ({len(batch)} records)...")

                try:
                    # Get embeddings for this batch
                    embeddings = await get_embeddings_batch(client, batch)

                    # Update database
                    update_embeddings_in_db(session, embeddings, column_name)

                    processed += len(batch)
                    print(f"Successfully processed {processed}/{total_records} records")

                except Exception as e:
                    print(f"Error processing batch {batch_num}: {e}")
                    session.rollback()
                    print("Rolling back batch. Continuing with next batch...")
                    continue

        print(f"\nMigration complete! Processed {processed}/{total_records} records.")

    except Exception as e:
        print(f"Fatal error during migration: {e}")
        session.rollback()
        sys.exit(1)
    finally:
        session.close()
        engine.dispose()


def main():
    """Entry point for the migration script."""
    print("=" * 60)
    print("Embedding Migration Script")
    print("=" * 60)
    asyncio.run(migrate_embeddings())


if __name__ == "__main__":
    main()