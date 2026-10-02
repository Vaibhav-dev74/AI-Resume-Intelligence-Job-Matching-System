from collections import OrderedDict
import hashlib
from typing import List, Union
import numpy as np
from app.core.config import settings
from app.core.logging import logger


class EmbeddingEngine:
    MAX_CACHE_SIZE: int = 4096

    def __init__(self, model_name: str = None):
        self.model_name = model_name or settings.EMBEDDING_MODEL_NAME
        self.dimension = settings.EMBEDDING_DIMENSION
        self._model = None
        self._cache: OrderedDict[str, np.ndarray] = OrderedDict()

    def _get_model(self):
        if self._model is None:
            try:
                from sentence_transformers import SentenceTransformer
                logger.info(f"Loading SentenceTransformer model: {self.model_name}...")
                self._model = SentenceTransformer(self.model_name)
                logger.info("SentenceTransformer model loaded successfully.")
            except Exception as e:
                logger.warning(f"Could not load SentenceTransformer ({e}). Using deterministic fallback embedding.")
                self._model = "FALLBACK"
        return self._model

    def encode(self, text: Union[str, List[str]]) -> np.ndarray:
        if isinstance(text, str):
            single = True
            texts = [text]
        else:
            single = False
            texts = text

        results = []
        texts_to_compute = []
        compute_indices = []

        for idx, t in enumerate(texts):
            clean_t = t.strip()
            cache_key = hashlib.sha256(clean_t.encode("utf-8")).hexdigest()
            if cache_key in self._cache:
                self._cache.move_to_end(cache_key)
                results.append((idx, self._cache[cache_key]))
            else:
                texts_to_compute.append(clean_t)
                compute_indices.append((idx, cache_key))

        if texts_to_compute:
            model = self._get_model()
            if model != "FALLBACK":
                try:
                    embeddings = model.encode(
                        texts_to_compute,
                        normalize_embeddings=True,
                        show_progress_bar=False
                    )
                except Exception as e:
                    logger.warning(f"Model encoding failed: {e}. Falling back.")
                    embeddings = [self._deterministic_fallback_vector(t) for t in texts_to_compute]
            else:
                embeddings = [self._deterministic_fallback_vector(t) for t in texts_to_compute]

            for (orig_idx, key), emb in zip(compute_indices, embeddings):
                norm_emb = np.array(emb, dtype=np.float32)
                norm = np.linalg.norm(norm_emb)
                if norm > 0:
                    norm_emb = norm_emb / norm

                # Enforce bounded LRU cache capacity
                if len(self._cache) >= self.MAX_CACHE_SIZE:
                    self._cache.popitem(last=False)
                self._cache[key] = norm_emb
                results.append((orig_idx, norm_emb))

        results.sort(key=lambda x: x[0])
        final_array = np.array([r[1] for r in results], dtype=np.float32)

        return final_array[0] if single else final_array

    def cosine_similarity(self, vec_a: np.ndarray, vec_b: np.ndarray) -> float:
        a = np.array(vec_a, dtype=np.float32)
        b = np.array(vec_b, dtype=np.float32)
        norm_a = np.linalg.norm(a)
        norm_b = np.linalg.norm(b)
        if norm_a == 0 or norm_b == 0:
            return 0.0
        similarity = float(np.dot(a, b) / (norm_a * norm_b))
        # Monotonically map cosine similarity in range [0.0, 1.0]
        return max(0.0, min(1.0, float(similarity)))

    def _deterministic_fallback_vector(self, text: str) -> np.ndarray:
        vec = np.zeros(self.dimension, dtype=np.float32)
        words = text.lower().split()
        if not words:
            vec[0] = 1.0
            return vec

        for word in words:
            h = int(hashlib.md5(word.encode("utf-8")).hexdigest(), 16)
            dim_idx = h % self.dimension
            vec[dim_idx] += 1.0

        norm = np.linalg.norm(vec)
        if norm > 0:
            vec = vec / norm
        return vec


embedding_engine = EmbeddingEngine()
