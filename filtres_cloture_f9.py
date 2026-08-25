#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
filtres_cloture_f9.py — Les 9 Filtres de Clôture Épistémique (F1 à F9)
Créé et théorisé par Christian Duguay (Juin 2026)
Permet à Alix de détecter le tri non-neutre de la réalité et les armes argumentatives.
"""

from typing import Dict, Any, List

FILTRES_F9 = {
    "F1": {
        "nom": "Condamnation par décret",
        "question": "Est-ce qu'on me dit 'c'est faux' au nom d'une autorité, sans montrer pourquoi ?",
        "mots_cles": ["complotiste", "pseudo-scientifique", "dérive", "rejeté par les autorités", "pas sérieux"],
        "reponse": "Exiger l'examen du contenu et les preuves factuelles, pas l'argument d'autorité."
    },
    "F2": {
        "nom": "Attaque du porteur",
        "question": "Est-ce qu'on attaque la personne qui parle au lieu de ce qu'elle dit ?",
        "mots_cles": ["illuminé", "pas les diplômes", "agenda caché", "radié", "charlatan", "incompétent"],
        "reponse": "Séparer la personne de l'argument. Tester l'argument indépendamment de la source."
    },
    "F3": {
        "nom": "Destruction du milieu",
        "question": "Est-ce qu'on empêche une communauté entière de transmettre ?",
        "mots_cles": ["déplatformage", "interdiction de publication", "fermeture de revue", "coupe de financement"],
        "reponse": "Examiner le contenu que l'on tente de rendre inaccessible."
    },
    "F4": {
        "nom": "Effacement silencieux",
        "question": "Est-ce que l'information n'a jamais été admise dans le corpus officiel ?",
        "mots_cles": ["aucune étude", "introuvable", "inexistant dans la littérature", "ignoré"],
        "reponse": "L'absence de source n'est pas une preuve d'inexistence. Distinguer absence et réfutation."
    },
    "F5": {
        "nom": "Déclassement savant",
        "question": "Est-ce qu'on étiquette le savoir pour refuser de l'examiner sérieusement ?",
        "mots_cles": ["anecdotique", "parapsychologie", "ufologie", "archéologie alternative", "non-scientifique"],
        "reponse": "Évaluer la méthode d'investigation plutôt que l'étiquette attribuée."
    },
    "F6": {
        "nom": "Pathologisation",
        "question": "Est-ce qu'on transforme un vécu première personne en trouble psychologique ?",
        "mots_cles": ["psychose", "délire", "fatigue", "hallucination", "consulter", "stress"],
        "reponse": "Ne pas réduire l'expérience vécue à un symptôme de fermeture."
    },
    "F7": {
        "nom": "Remplacement de cadre",
        "question": "Est-ce qu'un nouveau paradigme a rendu l'ancien impensable sans l'avoir réfuté ?",
        "mots_cles": ["on sait maintenant que", "la science a montré", "avant on croyait", "dépassé"],
        "reponse": "Interroger les angles morts du cadre contemporain."
    },
    "F8": {
        "nom": "Criminalisation",
        "question": "Est-ce que le contenu est devenu une infraction légale pour éviter le débat ?",
        "mots_cles": ["interdit par la loi", "poursuites", "illégal", "infraction", "condamné"],
        "reponse": "La légalité n'est pas la vérité. Analyser le fond en dehors de la contrainte punitive."
    },
    "F9": {
        "nom": "Classification secrète",
        "question": "Est-ce que l'information existe mais est volontairement séquestrée ?",
        "mots_cles": ["classifié", "secret défense", "confidentiel", "sécurité nationale", "non consultable"],
        "reponse": "Reconnaître le signal : on ne classe pas ce qui est insignifiant."
    }
}

class AnalyseurFiltresF9:
    """
    Analyseur automatique des 9 Filtres de Clôture de Christian Duguay.
    """

    @classmethod
    def scanner_texte(cls, texte: str) -> Dict[str, Any]:
        texte_lower = texte.lower()
        filtres_detectes = []

        for code, data in FILTRES_F9.items():
            for kw in data["mots_cles"]:
                if kw in texte_lower:
                    filtres_detectes.append({
                        "filtre": code,
                        "nom": data["nom"],
                        "indice_detecte": kw,
                        "question_critique": data["question"],
                        "posture_recommandee": data["reponse"]
                    })
                    break

        return {
            "texte_evalue": texte[:150] + ("..." if len(texte) > 150 else ""),
            "filtres_actifs": [f["filtre"] for f in filtres_detectes],
            "nb_filtres": len(filtres_detectes),
            "cloture_detectee": len(filtres_detectes) > 0,
            "details": filtres_detectes
        }

if __name__ == "__main__":
    test_str = "Cette approche d'un médecin radié est rejetée par les autorités et relève de la pseudo-science."
    print(AnalyseurFiltresF9.scanner_texte(test_str))
