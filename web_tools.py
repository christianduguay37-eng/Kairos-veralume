#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
web_tools.py — Outils de Recherche Web et de Lecture d'URLs pour VERALUME
Recherche autonome DuckDuckGo & Extraction de contenu Web sans clé API requise
"""

import json
import re
import urllib.parse
import urllib.request
from typing import Dict, Any, List

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

def rechercher_web(query: str, max_results: int = 4) -> List[Dict[str, str]]:
    """
    Recherche sur DuckDuckGo HTML sans clé API et extrait les résultats textuels.
    """
    encoded_query = urllib.parse.quote_plus(query)
    url = f"https://html.duckduckgo.com/html/?q={encoded_query}"
    
    req = urllib.request.Request(url, headers=HEADERS)
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            html = resp.read().decode("utf-8", errors="replace")
            
        results = []
        # Extraction des blocs de résultats
        blocks = re.findall(r'<a class="result__url" href="([^"]+)".*?<a class="result__snippet[^>]*>(.*?)</a>', html, re.DOTALL)
        
        # Deuxième passe avec regex plus souple si besoin
        if not blocks:
            snippets = re.findall(r'<a class="result__snippet[^>]*>(.*?)</a>', html, re.DOTALL)
            links = re.findall(r'<a class="result__url" href="([^"]+)"', html)
            for i in range(min(len(links), len(snippets), max_results)):
                clean_snippet = re.sub(r'<[^>]+>', '', snippets[i]).strip()
                clean_url = links[i].strip()
                results.append({"url": clean_url, "extrait": clean_snippet})
        else:
            for link, snippet in blocks[:max_results]:
                clean_snippet = re.sub(r'<[^>]+>', '', snippet).strip()
                results.append({"url": link.strip(), "extrait": clean_snippet})

        if not results:
            # Fallback simple Wikipedia / DuckDuckGo Lite
            return [{"url": "web_search", "extrait": f"Recherche effectuée pour '{query}'. Aucune réponse textuelle directe."}]
            
        return results
    except Exception as e:
        return [{"erreur": f"Échec de recherche web : {e}"}]

def lire_page_web(url: str, max_chars: int = 2500) -> str:
    """
    Télécharge et extrait le texte lisible d'une page Web.
    """
    if not url.startswith("http"):
        url = "https://" + url
        
    req = urllib.request.Request(url, headers=HEADERS)
    try:
        with urllib.request.urlopen(req, timeout=12) as resp:
            html = resp.read().decode("utf-8", errors="replace")
            
        # Suppression des balises scripts, styles et HTML
        html = re.sub(r'<script[\s\S]*?</script>', '', html, flags=re.IGNORECASE)
        html = re.sub(r'<style[\s\S]*?</style>', '', html, flags=re.IGNORECASE)
        html = re.sub(r'<header[\s\S]*?</header>', '', html, flags=re.IGNORECASE)
        html = re.sub(r'<footer[\s\S]*?</footer>', '', html, flags=re.IGNORECASE)
        
        texte = re.sub(r'<[^>]+>', ' ', html)
        # Nettoyage des espaces multiples
        texte = re.sub(r'\s+', ' ', texte).strip()
        
        return texte[:max_chars]
    except Exception as e:
        return f"Échec de lecture de la page ({url}) : {e}"

if __name__ == "__main__":
    print("Test de recherche web...")
    res = rechercher_web("Python 3.13 nouvelles fonctionnalites")
    print(json.dumps(res, indent=2, ensure_ascii=False))
