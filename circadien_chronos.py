#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
circadien_chronos.py — Cycle Circadien & Ancrage Temporel Chronos pour Alix (VERALUME v3.4)
Issu de l'architecture cognitive Veralume développée par Christian Duguay
"""

import time
import datetime
from enum import Enum
from typing import Dict, Any, Optional, List, Tuple

class PhaseCircadienne(Enum):
    JOUR = "jour"                # Activité nominale & accumulation
    CREPUSCULE = "crepuscule"    # Décantation cognitive & synthèse
    NUIT = "nuit"                # Fenêtre du Moteur de Rêve (Consolidation mémoire)
    AUBE = "aube"                # Réveil des priors & ouverture

class HorlogeN:
    """Capteur temporel matériel local."""
    def __init__(self, fuseau: str = "local"):
        self.fuseau = fuseau

    def maintenant(self) -> datetime.datetime:
        return datetime.datetime.now()

    def minutes_depuis_minuit(self) -> int:
        t = self.maintenant()
        return t.hour * 60 + t.minute

    def jour_ordinal(self) -> int:
        return self.maintenant().toordinal()

    def provenance(self) -> str:
        return "capteur_materiel_os"


class CycleCircadien:
    """
    Gère le rythme circadien d'Alix en fonction de l'heure locale réelle.
    """
    FRONTIERES: List[Tuple[int, int, PhaseCircadienne]] = [
        (5 * 60,  7 * 60,  PhaseCircadienne.AUBE),
        (7 * 60,  20 * 60, PhaseCircadienne.JOUR),
        (20 * 60, 23 * 60, PhaseCircadienne.CREPUSCULE),
    ]  # 23:00 - 05:00 = NUIT (Fenêtre de Rêve)

    def __init__(self, horloge: Optional[HorlogeN] = None):
        self.horloge = horloge or HorlogeN()
        self.tour = 0
        self._phase_precedente: Optional[PhaseCircadienne] = None

    @classmethod
    def phase_de(cls, minutes: int) -> PhaseCircadienne:
        m = minutes % (24 * 60)
        for debut, fin, phase in cls.FRONTIERES:
            if debut <= m < fin:
                return phase
        return PhaseCircadienne.NUIT

    def phase_actuelle(self) -> PhaseCircadienne:
        return self.phase_de(self.horloge.minutes_depuis_minuit())

    def relever(self) -> Dict[str, Any]:
        p = self.phase_actuelle()
        if p is PhaseCircadienne.NUIT and self._phase_precedente is not p:
            self.tour += 1
        self._phase_precedente = p

        emojis = {
            PhaseCircadienne.AUBE: "🌅 AUBE",
            PhaseCircadienne.JOUR: "☀️ JOUR (Activité)",
            PhaseCircadienne.CREPUSCULE: "🌆 CRÉPUSCULE (Synthèse)",
            PhaseCircadienne.NUIT: "🌙 NUIT (Consolidation / Rêve)"
        }

        return {
            "phase": p.value,
            "label": emojis[p],
            "tour": self.tour,
            "fenetre_reve": p is PhaseCircadienne.NUIT,
            "heure_locale": self.horloge.maintenant().strftime("%H:%M:%S")
        }


class AncrageChronos:
    """
    Calibre l'intervalle de temps réel écoulé entre les échanges avec Christian.
    """
    def __init__(self, horloge: Optional[HorlogeN] = None):
        self.derniere_minute: Optional[int] = None
        self._horloge = horloge or HorlogeN()

    def tick(self) -> Dict[str, Any]:
        t = self._horloge.minutes_depuis_minuit()
        ecart = None if self.derniere_minute is None else (t - self.derniere_minute) % (24 * 60)
        self.derniere_minute = t
        return {
            "minutes_depuis_minuit": t,
            "intervalle_min": ecart,
            "langage": self._langage(ecart)
        }

    @staticmethod
    def _langage(ecart: Optional[int]) -> str:
        if ecart is None:
            return "premier échange de la session"
        if ecart < 1:
            return "dans le même souffle (immédiat)"
        if ecart < 15:
            return f"il y a {ecart} minute(s)"
        if ecart < 90:
            return "il y a environ une heure" if ecart >= 60 else f"il y a {ecart} minutes"
        return f"il y a {ecart // 60} h {ecart % 60:02d}"


if __name__ == "__main__":
    circ = CycleCircadien()
    chronos = AncrageChronos()
    print("Relevé circadien :", circ.relever())
    print("Ancrage chronos  :", chronos.tick())
