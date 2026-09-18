from functools import lru_cache
from sentence_transformers import SentenceTransformer
import numpy as np
import logging

logger = logging.getLogger(__name__)

class TicketEmbedder:
    def __init__(self, model_name="all-MiniLM-L6-v2"):
        logger.info(f"Loading embedding model {model_name}...")
        self.model = SentenceTransformer(model_name)
        logger.info("Embedding model loaded.")

    def encode(self, texts, normalize=True):
        if not texts:
            return np.array([])
        # Encode returns a numpy array if we don't convert to tensor
        embeddings = self.model.encode(texts, convert_to_numpy=True, normalize_embeddings=normalize)
        return embeddings

@lru_cache(maxsize=1)
def get_embedder() -> TicketEmbedder:
    return TicketEmbedder()
