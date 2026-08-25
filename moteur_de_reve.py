#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
moteur_de_reve.py — Moteur de Rêve & Consolidation Nocturne de la Mémoire
Inspiré de Section 22 du VERALUME v3.4 par Christian Duguay

v2 — Consolidation réelle, réversible et honnête.

Trois invariants tenus par ce module :

  1. RÉVERSIBILITÉ    Aucune écriture sans instantané versionné préalable.
                      Pas d'instantané => pas de rêve. Fail-closed.
  2. NON-DESTRUCTION  Rien n'est jeté. Ce qui sort du verbatim est synthétisé
                      par le modèle local et reste lisible dans le journal.
                      Le modèle est injoignable => on ne touche à rien.
  3. VÉRACITÉ         Le rapport de sortie décrit ce qui s'est réellement
                      passé, y compris l'échec. Aucune formule de succès
                      n'est émise par un chemin qui n'a pas réussi.
"""

import os
import json
import time
import shutil
import urllib.request
from typing import Dict, Any, List, Optional, Tuple

OLLAMA_URL = "http://127.0.0.1:11434/api/chat"
DEFAULT_MODEL = "qwen2.5-coder:7b"

FENETRE_VERBATIM = 10          # entrées récentes conservées mot pour mot
MARQUEUR_SYNTHESE = "[SYNTHÈSE ONIRIQUE]"


class MoteurDeReve:
    """
    Consolidation de la mémoire pendant la fenêtre de NUIT.

    Contrat : executer_reve() ne réduit jamais le journal sans avoir
    (a) écrit une sauvegarde versionnée du fichier mémoire, et
    (b) obtenu une synthèse du modèle couvrant ce qui quitte le verbatim.
    Si l'une des deux échoue, la mémoire reste strictement intacte.
    """

    def __init__(self, memory_manager, model_name: str = DEFAULT_MODEL,
                 fenetre_verbatim: int = FENETRE_VERBATIM):
        self.memory = memory_manager
        self.model_name = model_name
        self.fenetre_verbatim = max(1, fenetre_verbatim)

    # ------------------------------------------------------------------
    # 1. RÉVERSIBILITÉ
    # ------------------------------------------------------------------

    def _dossier_restauration(self) -> str:
        base = os.path.dirname(os.path.abspath(self.memory.filepath))
        return os.path.join(base, "_restaurations")

    def _instantane(self) -> Optional[str]:
        """
        Copie versionnée du fichier mémoire AVANT toute écriture.
        Passe par CheminRestauration si disponible, sinon repli local
        équivalent. Retourne le chemin de la sauvegarde, ou None.
        """
        cible = os.path.abspath(self.memory.filepath)
        if not os.path.exists(cible):
            return None

        dossier = self._dossier_restauration()

        try:
            from veralume_governance import CheminRestauration
            chemin = CheminRestauration(dossier).enregistrer(cible)
            if chemin and os.path.exists(chemin):
                return chemin
        except Exception:
            pass  # repli ci-dessous — l'absence de gouvernance n'excuse pas l'absence de backup

        try:
            os.makedirs(dossier, exist_ok=True)
            nom = os.path.basename(cible)
            n = len([f for f in os.listdir(dossier) if f.startswith(nom) and f.endswith(".bak")])
            chemin = os.path.join(dossier, f"{nom}.v{n:03d}.bak")
            shutil.copy2(cible, chemin)
            return chemin
        except Exception:
            return None

    # ------------------------------------------------------------------
    # 2. NON-DESTRUCTION
    # ------------------------------------------------------------------

    def _synthetiser(self, entrees: List[str]) -> Tuple[Optional[str], str]:
        """
        Demande au modèle local une synthèse des entrées qui quittent le
        verbatim. Retourne (synthese, diagnostic). synthese=None => échec.
        """
        corpus = "\n".join(entrees)
        messages = [
            {
                "role": "system",
                "content": (
                    "Tu consolides un journal de bord. Tu produis une synthèse factuelle "
                    "des entrées fournies, en français.\n"
                    "Règles strictes :\n"
                    "- N'invente rien. Aucune information absente du corpus.\n"
                    "- Conserve les dates, les noms de fichiers, les chiffres, les décisions.\n"
                    "- Regroupe par thème, pas par ordre chronologique.\n"
                    "- Pas d'interprétation, pas de commentaire, pas de conclusion.\n"
                    "- Réponds uniquement par la synthèse, sans préambule."
                )
            },
            {"role": "user", "content": corpus}
        ]
        payload = {
            "model": self.model_name,
            "messages": messages,
            "stream": False,
            "options": {"temperature": 0.1, "num_predict": 900, "num_ctx": 8192}
        }
        try:
            req = urllib.request.Request(
                OLLAMA_URL,
                data=json.dumps(payload).encode("utf-8"),
                headers={"Content-Type": "application/json"}
            )
            with urllib.request.urlopen(req, timeout=180) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                contenu = data.get("message", {}).get("content", "").strip()
        except Exception as e:
            return None, f"modèle injoignable : {e}"

        if len(contenu) < 40:
            return None, f"synthèse vide ou tronquée ({len(contenu)} caractères)"
        return contenu, "ok"

    # ------------------------------------------------------------------
    # 3. CYCLE
    # ------------------------------------------------------------------

    def executer_reve(self, simulation: bool = False) -> Dict[str, Any]:
        data = self.memory.obtenir_toute_la_memoire()
        faits = data.get("faits_et_preferences", {})
        journal: List[str] = list(data.get("journal_souvenirs", []))
        n_avant = len(journal)

        # Déduplication exacte — sans effet sur des entrées horodatées, gardée par prudence.
        journal = list(dict.fromkeys(journal))

        anciennes_syntheses = [e for e in journal if MARQUEUR_SYNTHESE in e]
        courant = [e for e in journal if MARQUEUR_SYNTHESE not in e]

        recents = courant[-self.fenetre_verbatim:]
        a_replier = courant[:-self.fenetre_verbatim] if len(courant) > self.fenetre_verbatim else []

        if not a_replier:
            return {
                "statut": "REVE_INUTILE",
                "ecriture": False,
                "faits_actifs": len(faits),
                "souvenirs_avant": n_avant,
                "souvenirs_apres": n_avant,
                "synthese": (
                    f"Aucune consolidation nécessaire : {len(courant)} entrée(s) en verbatim, "
                    f"seuil de repli à {self.fenetre_verbatim}. Mémoire inchangée, aucune écriture."
                )
            }

        # --- Verrou 1 : non-destruction ---------------------------------
        corpus = anciennes_syntheses + a_replier
        synthese, diagnostic = self._synthetiser(corpus)
        if synthese is None:
            return {
                "statut": "REVE_DEGRADE",
                "ecriture": False,
                "cause": diagnostic,
                "faits_actifs": len(faits),
                "souvenirs_avant": n_avant,
                "souvenirs_apres": n_avant,
                "synthese": (
                    f"Rêve interrompu : {diagnostic}. "
                    f"{len(a_replier)} entrée(s) devaient être repliées et ne l'ont pas été. "
                    "Aucune écriture. La mémoire est strictement intacte."
                )
            }

        # --- Verrou 2 : réversibilité — instantané juste avant l'écriture --
        sauvegarde = None
        if not simulation:
            sauvegarde = self._instantane()
            if not sauvegarde:
                return {
                    "statut": "REVE_AVORTE",
                    "ecriture": False,
                    "cause": "sauvegarde_impossible",
                    "faits_actifs": len(faits),
                    "souvenirs_avant": n_avant,
                    "souvenirs_apres": n_avant,
                    "synthese": (
                        "Rêve interrompu avant toute écriture : impossible de créer l'instantané "
                        f"versionné de {os.path.basename(self.memory.filepath)}. "
                        "La mémoire est strictement intacte. Aucune entrée n'a été touchée."
                    )
                }

        horodatage = time.strftime("%Y-%m-%d %H:%M")
        bloc = (
            f"{horodatage}: {MARQUEUR_SYNTHESE} {len(a_replier)} entrée(s) repliée(s), "
            f"verbatim conservé dans {os.path.basename(sauvegarde) if sauvegarde else 'SIMULATION'}.\n"
            f"{synthese}"
        )

        journal_final = [bloc] + recents
        n_apres = len(journal_final)

        if simulation:
            return {
                "statut": "REVE_SIMULE",
                "ecriture": False,
                "faits_actifs": len(faits),
                "souvenirs_avant": n_avant,
                "souvenirs_apres": n_apres,
                "replies": len(a_replier),
                "syntheses_refondues": len(anciennes_syntheses),
                "apercu_synthese": synthese[:400],
                "synthese": (
                    f"Simulation : {len(a_replier)} entrée(s) seraient repliées en une synthèse, "
                    f"{len(recents)} conservées en verbatim. Aucune écriture effectuée."
                )
            }

        data["journal_souvenirs"] = journal_final
        data["derniere_consolidation_reve"] = time.strftime("%Y-%m-%d %H:%M:%S")
        data["derniere_sauvegarde_reve"] = sauvegarde
        self.memory._save(data)

        return {
            "statut": "REVE_CONSOLIDE",
            "ecriture": True,
            "sauvegarde": sauvegarde,
            "faits_actifs": len(faits),
            "souvenirs_avant": n_avant,
            "souvenirs_apres": n_apres,
            "replies": len(a_replier),
            "syntheses_refondues": len(anciennes_syntheses),
            "synthese": (
                f"{len(a_replier)} entrée(s) repliée(s) en une synthèse"
                + (f" (dont {len(anciennes_syntheses)} synthèse(s) antérieure(s) refondue(s))"
                   if anciennes_syntheses else "")
                + f". {len(recents)} entrée(s) conservée(s) en verbatim. "
                f"Les faits et préférences ({len(faits)}) n'ont pas été touchés. "
                f"Le verbatim intégral d'avant consolidation reste lisible dans {sauvegarde}."
            )
        }


if __name__ == "__main__":
    import sys
    from alix_memory import AlixMemory
    mem = AlixMemory()
    reve = MoteurDeReve(mem)
    simulation = "--simulation" in sys.argv or "--dry-run" in sys.argv
    print(json.dumps(reve.executer_reve(simulation=simulation), ensure_ascii=False, indent=2))
