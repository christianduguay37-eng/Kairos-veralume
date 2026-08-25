#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
skills_registry.py — Registre des Skills Modulaires VERALUME
Issu du corpus des 36 Skills développé par Christian Duguay
"""

from typing import Dict, Any, List

SKILLS_VERALUME: Dict[str, Dict[str, Any]] = {
    "audit_systeme": {
        "nom": "Audit Système & Diagnostic SRE",
        "description": "Analyse rigoureuse de la mémoire, des threads CPU, des descripteurs de fichiers et de la latence.",
        "protocole": "1. Mesurer métriques réelles. 2. Isoler les anomalies de dispersion. 3. Proposer correctif versionné."
    },
    "securite_coupe_circuit": {
        "nom": "Sécurité & Coupe-Circuit Déterministe",
        "description": "Validation des ordres avant exécution physique selon la matrice de réversibilité.",
        "protocole": "1. Analyse d'intention (STRIC_i). 2. Vérification de la licence Gatekeeper. 3. Exécution avec copie .bak."
    },
    "refactorisation_code": {
        "nom": "Refactorisation de Code Haute Performance",
        "description": "Structuration modulaire, typage strict, élimination des redondances et conformité PEP8/Async.",
        "protocole": "1. Identifier les dépendances. 2. Découper en fonctions pures. 3. Valider par tests unitaires."
    },
    "veille_web_osint": {
        "nom": "Recherche & Synthèse Web Récente",
        "description": "Extraction factuelle d'informations sur le Web sans biais ni hallucination.",
        "protocole": "1. Requête DuckDuckGo ciblée. 2. Extraction du texte brut. 3. Synthèse concise en français."
    },
    "moteur_de_reve": {
        "nom": "Consolidation Nocturne & Moteur de Rêve",
        "description": "Défragmentation de la mémoire persistante et structuration des connaissances durables.",
        "protocole": "1. Lecture du journal. 2. Déduplication des faits. 3. Cristallisation des invariants."
    }
}

class SkillsRegistry:
    @classmethod
    def lister_skills(cls) -> List[Dict[str, str]]:
        return [{"id": k, "nom": v["nom"], "description": v["description"]} for k, v in SKILLS_VERALUME.items()]

    @classmethod
    def obtenir_skill(cls, skill_id: str) -> Dict[str, Any]:
        return SKILLS_VERALUME.get(skill_id, {})

if __name__ == "__main__":
    print("Skills disponibles :", SkillsRegistry.lister_skills())
