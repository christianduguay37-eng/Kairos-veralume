#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
alix_memory.py — Système de Mémoire Long-Terme Persistante pour Alix / VERALUME
Permet à l'agent de stocker, retenir et faire évoluer ses souvenirs et connaissances
"""

import os
import sys
import json
import time
from typing import Dict, Any, List, Optional

DEFAULT_MEMORY_FILE = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "workspace_sandbox",
    "alix_memoire.json"
)

class AlixMemory:
    """
    Gestionnaire de mémoire persistante pour Alix.
    """

    def __init__(self, filepath: str = DEFAULT_MEMORY_FILE):
        self.filepath = os.path.abspath(filepath)
        os.makedirs(os.path.dirname(self.filepath), exist_ok=True)
        self.data: Dict[str, Any] = self._load()

    def _load(self) -> Dict[str, Any]:
        if os.path.exists(self.filepath):
            try:
                with open(self.filepath, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                pass
        
        # Initialisation du cerveau par défaut d'Alix
        initial_data = {
            "nom_agent": "Alix",
            "utilisateur": "Christian Duguay",
            "cree_le": time.strftime("%Y-%m-%d %H:%M:%S"),
            "derniere_mise_a_jour": time.strftime("%Y-%m-%d %H:%M:%S"),
            "faits_et_preferences": {
                "utilisateur": "Christian Duguay (Créateur de KAIROS V6 & VERALUME)",
                "materiel": "Intel Core Ultra 7 258V (Lunar Lake), 32 Go RAM, Intel Arc 140V GPU",
                "systeme": "Windows 11 avec Ollama en local",
                "langue_preferee": "Français direct, chaleureux et technique"
            },
            "journal_souvenirs": [
                f"{time.strftime('%Y-%m-%d')}: Initialisation de ma mémoire autonome. Je suis le binôme de Christian pour le code, le SRE et le contrôle système."
            ]
        }
        self._save(initial_data)
        return initial_data

    def _save(self, data: Optional[Dict[str, Any]] = None):
        if data is not None:
            self.data = data
        self.data["derniere_mise_a_jour"] = time.strftime("%Y-%m-%d %H:%M:%S")
        with open(self.filepath, "w", encoding="utf-8") as f:
            json.dump(self.data, f, ensure_ascii=False, indent=2)

    def memoriser_fait(self, cle: str, valeur: str) -> str:
        """
        Enregistre ou met à jour une information clé-valeur dans son cerveau.
        """
        cle_clean = cle.strip()
        self.data.setdefault("faits_et_preferences", {})[cle_clean] = valeur.strip()
        self._save()
        return f"Souvenir enregistré dans ma mémoire : [{cle_clean}] = '{valeur}'"

    def ajouter_note(self, note: str) -> str:
        """
        Ajoute une note ou réflexion libre à son journal de bord.
        """
        entree = f"{time.strftime('%Y-%m-%d %H:%M')}: {note.strip()}"
        self.data.setdefault("journal_souvenirs", []).append(entree)
        self._save()
        return f"Note ajoutée à mon journal de bord : '{note}'"

    def lire_resume_memoire(self) -> str:
        """
        Retourne une synthèse compacte de la mémoire pour l'injection dans le prompt.
        """
        faits = self.data.get("faits_et_preferences", {})
        faits_str = ", ".join([f"{k}: {v}" for k, v in faits.items()])
        notes = self.data.get("journal_souvenirs", [])[-3:] # 3 dernières notes
        notes_str = " | ".join(notes)
        return f"Faits connus : [{faits_str}] | Dernières notes : [{notes_str}]"

    def obtenir_toute_la_memoire(self) -> Dict[str, Any]:
        return self.data

if __name__ == "__main__":
    mem = AlixMemory()
    print("Mémoire chargée :")
    print(json.dumps(mem.obtenir_toute_la_memoire(), indent=2, ensure_ascii=False))
