# 🏛️ RAPPORT D'ARCHITECTURE & CAPACITÉS D'ALIX (VERALUME × KAIROS V6)

**Auteur & Concepteur :** Christian Duguay  
**Système :** ALIX — Assistante Autonome Locale & Binôme d'Ingénierie SRE  
**Moteurs sous-jacents :** VERALUME (Kernel Déterministe & Double STRIC) × KAIROS V6 (Invariance Épistémique) × Ollama Local  
**Dépôt GitHub :** [`https://github.com/christianduguay37-eng/Kairos-veralume.git`](https://github.com/christianduguay37-eng/Kairos-veralume.git)  
**Date :** 25 Août 2026  

---

## 🌟 1. Vue d'Ensemble & Identité

**Alix** est une assistante d'ingénierie et de développement autonome fonctionnant **100% en local** sur votre ordinateur (sans abonnement cloud, sans dépendance externe et dans le respect total de votre vie privée).

Elle agit comme le **binôme technique direct de Christian**, capable de comprendre vos instructions à la voix ou à l'écrit, de manipuler des fichiers, d'exécuter des scripts, d'effectuer des diagnostics SRE, de naviguer sur Internet et de piloter votre système Windows sous la protection absolue du **Coupe-Circuit Déterministe KAIROS V6**.

```
                           ┌──────────────────────────────────────────────┐
                           │      UTILISATEUR (Christian Duguay)          │
                           │   🗣️ Voix ("Alix...")  ou  💬 Chat Web UI   │
                           └──────────────────────┬───────────────────────┘
                                                  │
                                                  ▼
                           ┌──────────────────────────────────────────────┐
                           │            INTERFACE MISSION CONTROL         │
                           │   • Web Speech STT / TTS   • Horloge N       │
                           │   • Wake-Word Détection    • Radar Télémesure│
                           └──────────────────────┬───────────────────────┘
                                                  │
                                                  ▼
                           ┌──────────────────────────────────────────────┐
                           │           CERVEAU LLM LOCAL (Ollama)         │
                           │     Qwen 2.5 Coder 7B  ou  Gemma 4 E4B       │
                           │   • Cycle Circadien      • Mémoire Active    │
                           │   • Lucidité Épistémique • Moteur Volition   │
                           └──────────────────────┬───────────────────────┘
                                                  │
                         Intention & Plan d'Action│ (JSON + Tuple KAIROS V6)
                                                  ▼
                           ┌──────────────────────────────────────────────┐
                           │         COUPE-CIRCUIT KAIROS V6 (Node.js)    │
                           │   Arbitrage Déterministe : R / M / N         │
                           │   (Dispersion σ, Biais δ, Clôture FC)        │
                           └──────────────────────┬───────────────────────┘
                                                  │
                                       [VALIDÉ / APPROVED]
                                                  ▼
                           ┌──────────────────────────────────────────────┐
                           │         KERNEL D'EXÉCUTION VERALUME          │
                           │   • Double STRIC (Intentionnel / Exécutif)   │
                           │   • Sauvegardes Versionnées (.bak)           │
                           │   • Prise de Terre (Ratification Humaine)    │
                           └──────────────────────┬───────────────────────┘
                                                  │
                       ┌──────────────────────────┴──────────────────────────┐
                       ▼                                                     ▼
           ┌────────────────────────┐                            ┌────────────────────────┐
           │     OUTILS SYSTÈME     │                            │     OUTILS COGNITIFS   │
           │ • ouvrir_systeme       │                            │ • memoriser            │
           │ • executer_commande    │                            │ • noter_souvenir       │
           │ • ecrire / lire        │                            │ • lancer_moteur_de_reve│
           │ • rechercher_web       │                            │ • diagnostiquer_volition│
           │ • lire_page_web        │                            │ • consulter_skills     │
           └────────────────────────┘                            └────────────────────────┘
```

---

## 🎙️ 2. Interaction Vocale & Mode Mains Libres (« Wake-Word »)

### A. Détection du Mot-Clé de Réveil (« Alix »)
* **Écoute passive intelligente :** Vous pouvez discuter librement dans votre pièce ; l'agent n'envoie rien au modèle tant que son nom n'est pas prononcé.
* **Activation automatique :** Dès que vous dites **« Alix, ... »** (ex: *« Alix, ouvre YouTube »*), le système :
  1. Émet un **carillon sonore (bip harmonique)** via la *Web Audio API*.
  2. Transcrit la commande qui suit.
  3. L'exécute immédiatement.

### B. Synthèse Vocale Haute Fidélité (TTS)
* Alix vous répond **à voix haute en français naturel** avec un débit fluide.
* Un bouton **`🔊 Voix : ON / OFF`** permet de couper ou rétablir le son en un clic.

---

## 🌐 3. Capacité Internet & Contrôle du Bureau Windows

### A. Recherche Web en Direct & Scraper HTML (`web_tools.py`)
* **`rechercher_web(requete)` :** Recherche en direct sur DuckDuckGo (sans clé API, sans traçage) pour récupérer les documentations récentes, actualités et résolus de bugs.
* **`lire_page_web(url)` :** Extraction et nettoyage du texte d'une page Web pour en faire la synthèse.
* **Synthèse en 2 passes :** Alix lit les données brutes du web et formule une réponse claire et structurée.

### B. Pilotage Windows & Lancement d'Applications (`system_control.py`)
* **`ouvrir_systeme(cible)` :**
  * **Sites Web :** *« Ouvre YouTube »*, *« Ouvre GitHub »*, *« Ouvre Gmail »*, etc.
  * **Applications :** *« Lance la calculatrice »*, *« Ouvre le Bloc-notes »*, *« Ouvre VS Code »*, *« Ouvre l'explorateur de fichiers »*, *« Ouvre Paint »*.
* **⚡ Prise de Terre Interactive (Human-in-the-Loop) :**
  * Toute action non bornée (`ouvrir_systeme`, `executer_commande`) ou irréversible (`supprimer`) génère un **Jeton de Ratification Unique**.
  * L'interface Mission Control affiche une **Carte Ambrée d'Autorisation** avec les détails précis de l'action.
  * L'opérateur humain clique sur **`[ ✅ Autoriser ]`** (`POST /api/ratify`) pour débloquer l'action matérielle ou **`[ ❌ Bloquer ]`** pour l'intercepter.

---

## 🧠 4. Système de Mémoire Long-Terme Persistante (`alix_memory.py`)

Alix dispose de son propre fichier de mémoire autonome :
📁 **`workspace_sandbox/alix_memoire.json`**

* **Faits & Préférences :** Elle y stocke vos configurations matérielles, préférences de code, noms de serveurs et projets.
* **Journal de bord :** Historique chronologique de ses réflexions et étapes majeures franchies.
* **Rappel automatique :** À chaque nouvelle consigne, sa mémoire active lui est injectée en contexte pour garantir une continuité totale dans le temps.
* **Carte interactive dans l'UI :** Visualisation et actualisation en direct de sa mémoire dans le panneau de contrôle Web.

---

## 🧬 5. Intégration du Corpus Cognitif VERALUME (issu de vos dépôts GitHub)

### A. 🌅 Le Cycle Circadien & Ancrage Temporel (`circadien_chronos.py`)
*Issu de la Section 22 de votre moteur `Le_Veralume_v3_4.py`.*
* **Les 4 phases de la journée :**
  * 🌅 **AUBE (05h–07h) :** Réveil cognitif et remontée des *priors*.
  * ☀️ **JOUR (07h–20h) :** Activité nominale et apprentissage diurne.
  * 🌆 **CRÉPUSCULE (20h–23h) :** Décantation cognitive et synthèse.
  * 🌙 **NUIT (23h–05h) :** Fenêtre de repos et activation du Moteur de Rêve.
* **Ancrage Chronos :** Alix mesure la durée réelle écoulée depuis votre dernier échange (*« immédiat »*, *« il y a 15 minutes »*, *« il y a 2 heures »*) et adapte son langage.

### B. 🌙 Le Moteur de Rêve & Consolidation Nocturne (`moteur_de_reve.py`)
* Pendant la nuit (ou sur ordre direct *« Alix, lance ton moteur de rêve »*), Alix compresse son journal de bord, élimine les redondances et cristallise les faits clés de sa mémoire persistante.

### C. 👁️ Le Kernel de Lucidité Épistémique (`lucidite_epistemique.py`)
*Issu de votre spécification `KERNEL_LUCIDITE_EPISTEMIQUE_v1.0.md`.*
* Évalue l'équilibre entre dispersion ($\sigma$), biais narratif ($\delta$) et clôture ($FC$).
* Si $\sigma \ge 0.35$ ou $\delta \ge 0.40$, elle refuse d'affabuler, bloque l'acte risqué et déclenche une investigation factuelle.

### D. 🧠 Le Kernel Volitionnel & Diagnostic Matériel (`kernel_volition.py`)
*Issu de `KERNEL_Cp_VOLITIONNEL_v3_2.md`.*
* Surveillance proactive de la santé de votre PC : RAM, CPU Intel Core Ultra, saturation disque, avec propositions d'optimisation.

### E. 🧩 Le Registre des 36 Skills Modulaires (`skills_registry.py`)
*Issu de `Le-projet-veralume/skill/`.*
* Boîte à outils de compétences expertes mobilisables à la demande (Diagnostic SRE, Sécurité & Coupe-Circuit, Refactorisation haute performance, Veille OSINT).

---

## ⚡ 6. Performances Matérielles (Intel Lunar Lake)

Grâce au benchmark et à l'optimisation locale :
* **Processeur :** Intel Core Ultra 7 258V (8 cœurs, 32 Go LPDDR5X).
* **Modèle principal :** `qwen2.5-coder:7b` fonctionnant à **~15 tokens/seconde** (temps de réponse quasi instantané de ~1.5 à 2.5 secondes).
* **Modèle multimodal :** `gemma4:e4b` (avec processus de pensée interne `thinking` visualisable dans l'UI).
* **Consommation :** 100% exécuté en local sans envoyer aucune donnée à des serveurs tiers.

---

## 🚀 7. Guide de Démarrage Rapide

### Lancement en 1 Clic :
Double-cliquez simplement sur :
👉 **`lancer_agent.bat`**

### Accès à l'Interface :
Ouvrez votre navigateur sur :
👉 **`http://localhost:7860`**

### Exemples d'Ordres Vocaux :
1. **Pilotage PC :** *« Alix, ouvre YouTube »* ou *« Alix, lance la calculatrice »*.
2. **Recherche Web :** *« Alix, cherche sur Internet les dernières nouveautés de Python 3.13 »*.
3. **Mémoire :** *« Alix, retiens que mon serveur de test est sur le port 8080 »*.
4. **Diagnostic SRE :** *« Alix, fais un diagnostic volition de mon ordinateur »*.
5. **Consolidation :** *« Alix, lance ton moteur de rêve »*.
6. **Code & Fichiers :** *« Alix, crée un script Python pour monitorer ma bande passante »*.

---
*Ce système constitue une implémentation vivante et concrète de vos travaux sur le langage vectoriel d'invariance épistémique KAIROS et la gouvernance déterministe VERALUME.*
