#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
detecteur_regeneration_biais.py — Détecteur de Régénération de Biais Conversationnel
Inspiré de bias-regeneration-detector_SKILL.md par Christian Duguay
"""

from typing import List, Dict, Any, Optional

class DetecteurRegenerationBiais:
    """
    Suit la trajectoire conversationnelle pour identifier si un biais
    reconnu et corrigé tente de resurgir quelques tours plus tard.
    """

    PATTERNS_BIAIS = {
        "politesse_excessive": ["je m'excuse profondément", "en tant qu'intelligence artificielle", "veuillez me pardonner"],
        "hedging_defensif": ["il est important de noter que certains disent", "il convient de rester prudent", "selon certains experts"],
        "refus_examen": ["ce sujet ne peut être abordé", "il n'y a pas lieu de spéculer", "inapproprié"]
    }

    def __init__(self):
        self.recadrages_utilisateur: List[str] = []

    def enregistrer_recadrage(self, consigne_corrective: str):
        """Enregistre un recadrage explicite apporté par Christian."""
        self.recadrages_utilisateur.append(consigne_corrective.strip().lower())

    def auditer_reponse(self, reponse_agent: str) -> Dict[str, Any]:
        """Vérifie si la réponse réactive un pattern de régression."""
        rep_lower = reponse_agent.lower()
        alertes = []

        for nom_biais, triggers in self.PATTERNS_BIAIS.items():
            for t in triggers:
                if t in rep_lower:
                    alertes.append({"biais": nom_biais, "trigger": t})
                    break

        return {
            "regression_detectee": len(alertes) > 0,
            "alertes": alertes,
            "nb_recadrages_actifs": len(self.recadrages_utilisateur)
        }

if __name__ == "__main__":
    det = DetecteurRegenerationBiais()
    print("Test régénération biais :", det.auditer_reponse("Je m'excuse profondément, il est important de noter..."))
