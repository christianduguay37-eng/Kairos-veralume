"""
VERALUME MIDDLEWARE - Sentinelle Cerbère
Garde-fous runtime : vérification de la Distance Sacrée, du ratio Signal/Bruit et audit d'intégrité.
"""

from typing import Dict, Any, List
import numpy as np
from .metrics import CPCMetrics

class CerbereSentinel:
    """Middleware de protection cognitive et d'audit runtime."""

    @staticmethod
    def audit_social_distance(s_i: np.ndarray, s_j: np.ndarray) -> Dict[str, Any]:
        chi = CPCMetrics.social_chirality(s_i, s_j)
        is_safe = 0.3 <= chi <= 0.95
        is_sacred = 0.45 <= chi <= 0.75

        status = "DISTANCE_SACREE" if is_sacred else ("ZONE_STABLE" if is_safe else "ALERTE_FUSION")
        return {
            "chi_soc": round(chi, 4),
            "is_safe": is_safe,
            "is_sacred": is_sacred,
            "status": status,
            "intervention_needed": chi < 0.3
        }

    @staticmethod
    def audit_density(text: str) -> Dict[str, Any]:
        total_len = len(text)
        if total_len == 0:
            return {"ratio": 1.0, "passed": True}
        # Ratio heuristique : densité lexicale sans verbiage
        words = text.split()
        avg_word_len = sum(len(w) for w in words) / max(1, len(words))
        density_score = min(1.0, round(avg_word_len / 7.0, 2))
        return {
            "word_count": len(words),
            "density_score": density_score,
            "passed": density_score >= 0.7
        }