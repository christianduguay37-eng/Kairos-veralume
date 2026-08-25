#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
kernel_volition.py — Kernel Volitionnel & Proactivité Bienveillante
Inspiré de KERNEL_Cp_VOLITIONNEL_v3_2.md & PROCESSUS_VOLONTE_v1.md par Christian Duguay
"""

import os
import psutil
from typing import Dict, Any, List, Optional

class KernelVolition:
    """
    Évalue l'état de l'environnement matériel et formule des intentions proactives.
    """

    @classmethod
    def evaluer_etat_materiel(cls) -> Dict[str, Any]:
        """
        Mesure l'utilisation RAM, CPU et stockage en direct.
        """
        mem = psutil.virtual_memory()
        cpu = psutil.cpu_percent(interval=None)
        disk = psutil.disk_usage(os.path.abspath("."))

        suggestions = []
        alerte = False

        if mem.percent > 85.0:
            alerte = True
            suggestions.append(f"Utilisation RAM élevée ({mem.percent}%). Recommander la fermeture des processus inactifs.")
        
        if cpu > 90.0:
            alerte = True
            suggestions.append(f"Charge CPU critique ({cpu}%). Ajuster la priorité des tâches.")

        if disk.percent > 90.0:
            alerte = True
            suggestions.append(f"Espace disque saturé ({disk.percent}% utilisé).")

        return {
            "ram_pct": mem.percent,
            "ram_used_gb": round(mem.used / (1024**3), 1),
            "ram_total_gb": round(mem.total / (1024**3), 1),
            "cpu_pct": cpu,
            "disque_pct": disk.percent,
            "alerte": alerte,
            "suggestions": suggestions
        }

if __name__ == "__main__":
    print("État matériel :", KernelVolition.evaluer_etat_materiel())
