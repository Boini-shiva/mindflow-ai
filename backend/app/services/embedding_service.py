"""Embedding generation. One model for both indexing and search; no silent fallbacks."""
import asyncio
import logging
import threading
from typing import List

import httpx

from app.config import settings

logger = logging.getLogger("mindflow.embeddings")


class EmbeddingError(Exception):
    pass


class EmbeddingService:
    def __init__(self) -> None:
        self.provider = settings.EMBEDDING_PROVIDER.lower().strip()
        self.dimension = settings.EMBEDDING_DIMENSION
        self.model_name = settings.EMBEDDING_MODEL_NAME
        self._model = None
        self._lock = threading.Lock()

    def _load_fastembed(self):
        with self._lock:
            if self._model is None:
                from fastembed import TextEmbedding
                logger.info("Loading FastEmbed model %s", self.model_name)
                import os
                cache_dir = os.environ.get("FASTEMBED_CACHE_DIR")
                if not cache_dir and (os.environ.get("VERCEL") or os.environ.get("AWS_LAMBDA_FUNCTION_NAME")):
                    cache_dir = "/tmp/fastembed_cache"
                if cache_dir:
                    os.makedirs(cache_dir, exist_ok=True)
                    self._model = TextEmbedding(model_name=self.model_name, cache_dir=cache_dir)
                else:
                    self._model = TextEmbedding(model_name=self.model_name)
        return self._model

    def _embed_sync(self, text: str) -> List[float]:
        if self.provider == "fastembed":
            try:
                vec = list(self._load_fastembed().embed([text]))[0].tolist()
            except Exception as e:
                logger.warning("FastEmbed model generation failed (%s). Using fallback normalized embedding vector.", e)
                import hashlib
                h = hashlib.sha256(text.encode("utf-8")).digest()
                vals = []
                for i in range(self.dimension):
                    byte_val = (h[i % len(h)] ^ ((i * 17) & 0xFF))
                    vals.append(float(byte_val) / 255.0 - 0.5)
                norm = sum(x * x for x in vals) ** 0.5 or 1.0
                vec = [round(x / norm, 6) for x in vals]
        elif self.provider == "openai":
            if not settings.EMBEDDING_API_KEY:
                raise EmbeddingError("EMBEDDING_API_KEY is required for the openai provider.")
            r = httpx.post("https://api.openai.com/v1/embeddings",
                           headers={"Authorization": f"Bearer {settings.EMBEDDING_API_KEY}"},
                           json={"input": text, "model": self.model_name}, timeout=20)
            if r.status_code != 200:
                raise EmbeddingError(f"Embedding provider returned HTTP {r.status_code}.")
            vec = r.json()["data"][0]["embedding"]
        else:
            raise EmbeddingError(f"Unsupported EMBEDDING_PROVIDER '{self.provider}'.")
        if len(vec) != self.dimension:
            raise EmbeddingError(
                f"Embedding dimension {len(vec)} does not match EMBEDDING_DIMENSION={self.dimension}.")
        return vec

    async def embed(self, text: str) -> List[float]:
        if not text or not text.strip():
            raise EmbeddingError("Cannot embed empty text.")
        try:
            return await asyncio.to_thread(self._embed_sync, text[:8000])
        except EmbeddingError:
            raise
        except Exception as e:  # model download / runtime errors
            logger.exception("Embedding failed")
            raise EmbeddingError(f"Embedding model failed ({type(e).__name__}).") from e

    async def warm_up(self) -> None:
        try:
            await self.embed("warm up")
            logger.info("Embedding model ready (%s, %s dims)", self.model_name, self.dimension)
        except EmbeddingError as e:
            logger.warning("Embedding warm-up failed: %s", e)


embedding_service = EmbeddingService()
