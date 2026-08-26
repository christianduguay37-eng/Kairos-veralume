"""
MÉMOIRE ÉPISTÉMIQUE - Indexeur Automatique du Grand Traité
Découpe et indexe le document méta-synthèse par section et registre épistémique.
"""

import os
import re
from .vector_store import EpistemicMemoryStore

class EpistemicIndexer:
    @staticmethod
    def index_meta_document(doc_path: str, memory_store: EpistemicMemoryStore):
        if not os.path.exists(doc_path):
            raise FileNotFoundError(f"Document introuvable : {doc_path}")

        with open(doc_path, "r", encoding="utf-8") as f:
            content = f.read()

        # Découpage par sections markdown (# ou ##)
        sections = re.split(r"\n(?=##?\s+)", content)
        indexed_count = 0

        for sec in sections:
            sec = sec.strip()
            if not sec:
                continue

            lines = sec.split("\n")
            header = lines[0].replace("#", "").strip()
            body = "\n".join(lines[1:]).strip()

            # Attribution heuristique de registre épistémique
            register = "Ingénierie"
            if re.search(r"hamiltonien|formalisme|mathématique|chiralité|théorie cpc", header, re.IGNORECASE):
                register = "Hard Science"
            elif re.search(r"cosmologie|livre|âme|esprit|corps|celtok|manitou", header, re.IGNORECASE):
                register = "Imaginal"
            elif re.search(r"opérateur|kernel|stric|kle|pce|density", header, re.IGNORECASE):
                register = "Ingénierie"
            elif re.search(r"kairos|tuple|langage vectoriel|scaling", header, re.IGNORECASE):
                register = "Ingénierie"

            memory_store.add_chunk(
                title=header,
                content=body[:1500],  # Taille de chunk optimale
                register=register,
                source_file=os.path.basename(doc_path)
            )
            indexed_count += 1

        memory_store.save()
        return indexed_count