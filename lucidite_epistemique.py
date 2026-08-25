#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
lucidite_epistemique.py — Kernel de Lucidité Épistémique & Anti-Hallucination
Inspiré de KERNEL_LUCIDITE_EPISTEMIQUE_v1.0.md (Architecture VERALUME par Christian Duguay)
"""

import math
from typing import Dict, Any, Tuple

class LuciditeEpistemique:
    """
    Mesure la dispersion cognitive (sigma) et le biais de fermeture (FC).
    Empêche l'agent d'agir sous illusion de certitude.
    """

    SEUIL_SIGMA_CRITIQUE = 0.35
    SEUIL_DELTA_BIAIS = 0.40
    SEUIL_FC_MINIMAL = 0.70

    @classmethod
    def auditer_posture(cls, sigma: float, delta: float, fc: float, prompt: str, action_demandee: str) -> Dict[str, Any]:
        """
        Analyse l'alignement entre le niveau de certitude affiché et le risque de l'action.
        """
        alerte_hallucination = False
        recommandation = "NOMINALE"
        motif = "Posture cognitive équilibrée."

        # Cas 1 : Haute incertitude déclarée ou détectée
        if sigma >= cls.SEUIL_SIGMA_CRITIQUE:
            alerte_hallucination = True
            recommandation = "INVESTIGATION_REQUISE"
            motif = f"Dispersion épistémique élevée (σ={sigma:.2f} >= {cls.SEUIL_SIGMA_CRITIQUE}). L'agent doit vérifier ses sources avant d'agir."

        # Cas 2 : Biais narratif élevé (déplacement delta)
        elif delta >= cls.SEUIL_DELTA_BIAIS:
            alerte_hallucination = True
            recommandation = "CALIBRATION_REQUISE"
            motif = f"Biais narratif détecté (δ={delta:.2f} >= {cls.SEUIL_DELTA_BIAIS}). Risque de distorsion factuelle."

        # Cas 3 : Clôture forcée fragile
        elif fc < cls.SEUIL_FC_MINIMAL and action_demandee not in ["aucun", "rechercher_web", "lire"]:
            alerte_hallucination = True
            recommandation = "BLOCAGE_SECURITE"
            motif = f"Clôture logique insuffisante (FC={fc:.2f} < {cls.SEUIL_FC_MINIMAL}) pour engager une action matérielle."

        return {
            "lucide": not alerte_hallucination,
            "recommandation": recommandation,
            "sigma": sigma,
            "delta": delta,
            "fc": fc,
            "motif": motif
        }

if __name__ == "__main__":
    test = LuciditeEpistemique.auditer_posture(0.42, 0.10, 0.95, "Supprime le disque C:", "supprimer")
    print("Test Lucidité :", test)
