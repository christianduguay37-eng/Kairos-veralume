"""
MÉMOIRE ÉPISTÉMIQUE NŒUD G - Vector Store Embarqué
Moteur de stockage et recherche vectorielle léger sans dépendances lourdes.
"""

import math
import re
from typing import List, Dict, Any, Tuple
import json
import os

class EpistemicChunk:
    def __init__(self, chunk_id: str, title: str, content: str, register: str, source_file: str, embedding: List[float] = None):
        self.chunk_id = chunk_id
        self.title = title
        self.content = content
        self.register = register  # "Hard Science", "Ingénierie", "Imaginal", "Attesté", "Inféré"
        self.source_file = source_file
        self.embedding = embedding or []

class EpistemicMemoryStore:
    """Magasin vectoriel et sémantique pour le Corpus Veralume & Kairos."""

    def __init__(self, storage_file: str = "data/epistemic_memory.json"):
        self.storage_file = storage_file
        self.chunks: List[EpistemicChunk] = []
        self.vocabulary: Dict[str, int] = {}
        self.load()

    def _tokenize(self, text: str) -> List[str]:
        return [w.lower() for w in re.findall(r"\b\w{3,}\b", text)]

    def _compute_bow_vector(self, text: str) -> Dict[str, float]:
        tokens = self._tokenize(text)
        tf = {}
        for t in tokens:
            tf[t] = tf.get(t, 0) + 1
        # Normalisation
        total = max(1, len(tokens))
        return {k: v / total for k, v in tf.items()}

    def add_chunk(self, title: str, content: str, register: str, source_file: str):
        chunk_id = f"chunk_{len(self.chunks)+1}"
        chunk = EpistemicChunk(chunk_id, title, content, register, source_file)
        self.chunks.append(chunk)

    def search(self, query: str, top_k: int = 3, filter_register: str = None) -> List[Tuple[EpistemicChunk, float]]:
        """Recherche sémantique par similarité cosinus TF-IDF."""
        query_vec = self._compute_bow_vector(query)
        if not query_vec:
            return []

        results = []
        for chunk in self.chunks:
            if filter_register and chunk.register != filter_register:
                continue

            chunk_vec = self._compute_bow_vector(chunk.title + " " + chunk.content)
            
            # Calcul du produit scalaire cosinus
            dot_product = sum(query_vec.get(term, 0.0) * chunk_vec.get(term, 0.0) for term in query_vec)
            norm_q = math.sqrt(sum(v**2 for v in query_vec.values()))
            norm_c = math.sqrt(sum(v**2 for v in chunk_vec.values()))

            if norm_q > 0 and norm_c > 0:
                score = dot_product / (norm_q * norm_c)
            else:
                score = 0.0

            if score > 0.0:
                results.append((chunk, score))

        results.sort(key=lambda x: x[1], reverse=True)
        return results[:top_k]

    def save(self):
        os.makedirs(os.path.dirname(self.storage_file), exist_ok=True)
        data = [{
            "chunk_id": c.chunk_id,
            "title": c.title,
            "content": c.content,
            "register": c.register,
            "source_file": c.source_file
        } for c in self.chunks]
        with open(self.storage_file, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def load(self):
        if os.path.exists(self.storage_file):
            try:
                with open(self.storage_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.chunks = [EpistemicChunk(
                        d["chunk_id"], d["title"], d["content"], d["register"], d["source_file"]
                    ) for d in data]
            except Exception:
                self.chunks = []