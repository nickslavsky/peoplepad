import httpx
import logging
from typing import List, Optional
import hashlib
from threading import Lock
from pydantic_settings import BaseSettings
from tenacity import retry, stop_after_attempt, wait_exponential
from sqlalchemy.orm import Session
from fastapi import Depends
from app.config import settings

logger = logging.getLogger(__name__)

# Thread-safe in-memory cache
class EmbeddingCache:
    def __init__(self):
        self.cache = {}
        self.lock = Lock()

    def get(self, key: str) -> Optional[List[float]]:
        with self.lock:
            return self.cache.get(key)

    def set(self, key: str, value: List[float]) -> None:
        with self.lock:
            self.cache[key] = value

    def clear(self) -> None:
        with self.lock:
            self.cache.clear()


# Global cache instance
embedding_cache = EmbeddingCache()

def generate_cache_key(text: str) -> str:
    """Generate a deterministic cache key from input text."""
    return hashlib.md5(text.encode('utf-8')).hexdigest()


@retry(stop=stop_after_attempt(settings.max_embedding_retries),
       wait=wait_exponential(multiplier=settings.embedding_retry_delay, min=1, max=10))
async def get_embedding(text: str) -> List[float]:
    cache_key = generate_cache_key(text)

    # Check cache first
    cached_embedding = embedding_cache.get(cache_key)
    if cached_embedding is not None:
        return cached_embedding
    # Call embedding service
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                settings.embedding_service_url,
                headers={
                    "Authorization": f"Bearer {settings.embedding_service_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "input": text,
                    "model": settings.embedding_model,
                    "encoding_format": "float"
                },
                timeout=10.0
            )
            response.raise_for_status()
            embedding = response.json().get("data", [{}])[0].get("embedding")

            # Store in cache
            embedding_cache.set(cache_key, embedding)
            logger.info(f"Generated and cached embedding for text: {text[:50]}...")
            return embedding
        except httpx.HTTPStatusError as e:
            logger.error(f"Embedding service error: {e}")
            raise
        except httpx.RequestError as e:
            logger.error(f"Embedding service error: {e}")
            raise
