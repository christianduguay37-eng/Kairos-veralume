#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
system_control.py — Contrôle du Système d'Exploitation & Bureau pour VERALUME
Permet à l'agent d'ouvrir des sites, lancer des applications et interagir avec Windows
"""

import os
import sys
import subprocess
import webbrowser
from typing import Dict, Any, List

def ouvrir_site_ou_application(cible: str) -> str:
    """
    Ouvre un site Web (ex: YouTube, GitHub) ou lance une application Windows (ex: Calculatrice, Notepad, VS Code).
    """
    cible_clean = cible.strip().lower()
    
    # 1. Raccourcis de sites web connus
    sites_connus = {
        "youtube": "https://www.youtube.com",
        "google": "https://www.google.com",
        "github": "https://www.github.com",
        "gmail": "https://mail.google.com",
        "chatgpt": "https://chatgpt.com",
        "reddit": "https://www.reddit.com",
        "netflix": "https://www.netflix.com",
        "wikipedia": "https://fr.wikipedia.org"
    }

    # 2. Raccourcis d'applications Windows
    apps_connues = {
        "calculatrice": "calc.exe",
        "calculator": "calc.exe",
        "calc": "calc.exe",
        "bloc-notes": "notepad.exe",
        "bloc notes": "notepad.exe",
        "notepad": "notepad.exe",
        "vscode": "code",
        "vs code": "code",
        "code": "code",
        "explorateur": "explorer.exe",
        "fichiers": "explorer.exe",
        "terminal": "wt.exe",
        "powershell": "powershell.exe",
        "cmd": "cmd.exe",
        "spotify": "spotify.exe",
        "paint": "mspaint.exe"
    }

    # Cas 1 : URL explicite
    if cible.startswith("http://") or cible.startswith("https://") or cible.startswith("www."):
        url = cible if cible.startswith("http") else "https://" + cible
        webbrowser.open(url)
        return f"Page Web ouverte dans le navigateur : {url}"

    # Cas 2 : Mot-clé de site web
    for nom, url in sites_connus.items():
        if nom in cible_clean:
            webbrowser.open(url)
            return f"Site Web '{nom}' ouvert avec succès dans votre navigateur : {url}"

    # Cas 3 : Mot-clé d'application Windows
    for nom, cmd in apps_connues.items():
        if nom in cible_clean:
            try:
                subprocess.Popen(cmd, shell=True)
                return f"Application Windows '{nom}' lancée avec succès ({cmd})."
            except Exception as e:
                return f"Erreur lors du lancement de '{nom}' : {e}"

    # Cas 4 : Tentative générique de lancement
    try:
        subprocess.Popen(f"start {cible}", shell=True)
        return f"Commande de lancement exécutée pour '{cible}'."
    except Exception as e:
        return f"Impossible d'ouvrir '{cible}' : {e}"

if __name__ == "__main__":
    print("Module de contrôle système prêt.")
