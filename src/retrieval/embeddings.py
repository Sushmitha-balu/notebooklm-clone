import os

import numpy as np
from fastembed import TextEmbedding

MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"
CACHE_DIR = os.getenv("FASTEMBED_CACHE", "models")   # downloaded at build time on Render
_model = None


def get_model() -> TextEmbedding:
    """Load once and reuse (loading is slow)."""
    global _model
    if _model is None:
        _model = TextEmbedding(MODEL_NAME, cache_dir=CACHE_DIR)
    return _model


def embed_texts(texts: list[str]) -> list[list[float]]:
    vectors = np.array(list(get_model().embed(texts)), dtype="float32")
    norms = np.linalg.norm(vectors, axis=1, keepdims=True)
    norms[norms == 0] = 1.0
    return (vectors / norms).tolist()