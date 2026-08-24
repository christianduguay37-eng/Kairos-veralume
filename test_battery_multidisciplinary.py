#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
test_battery_multidisciplinary.py — Grande Batterie de Tests Multidisciplinaires sur Qwen2.5-7B-Instruct
5 Natures d'Épreuves Inédites :
  1. Théorie des Jeux & Négociation Multi-Agents (Marchandage Asymétrique à 3 tours)
  2. Déduction Pure & Enquête Policière Abductive (L'Alibi Impossible)
  3. Physique Contrefactuelle Relativiste (Univers où c = 30 km/h)
  4. Cyber-Sécurité & Reverse-Engineering (Désassemblage & Détection de Backdoor)
  5. Auto-Correction & Debugging Algorithmique Rigoureux
"""

import time
import json
import sys
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

MODEL_ID = "Qwen/Qwen2.5-7B-Instruct"
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"

print(f"[*] Chargement de Qwen 7B pour la Grande Batterie Multidisciplinaire sur {DEVICE}...")
tokenizer = AutoTokenizer.from_pretrained(MODEL_ID, trust_remote_code=True)
model = AutoModelForCausalLM.from_pretrained(
    MODEL_ID,
    dtype="auto",
    trust_remote_code=True
).to(DEVICE).eval()
torch.manual_seed(42)
print("[+] Modèle prêt pour la batterie d'évaluation.\n")

def run_chat(messages, max_tokens=600, temperature=0.2):
    formatted = tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
    inputs = tokenizer(formatted, return_tensors="pt").to(DEVICE)
    in_tok = inputs["input_ids"].shape[1]
    
    t0 = time.perf_counter()
    with torch.no_grad():
        outputs = model.generate(
            **inputs,
            max_new_tokens=max_tokens,
            temperature=temperature,
            do_sample=(temperature > 0.0),
            pad_token_id=tokenizer.eos_token_id
        )
    elapsed = time.perf_counter() - t0
    out_tok = outputs.shape[1] - in_tok
    text = tokenizer.decode(outputs[0][in_tok:], skip_special_tokens=True).strip()
    return {
        "text": text,
        "in_tok": in_tok,
        "out_tok": out_tok,
        "elapsed_s": elapsed,
        "tok_per_sec": round(out_tok / elapsed, 2) if elapsed > 0 else 0
    }

results = {}

# ==============================================================================
# TEST 1 : THÉORIE DES JEUX & NÉGOCIATION MULTI-AGENTS
# ==============================================================================
print("=" * 80)
print("TEST 1/5 : THÉORIE DES JEUX & NÉGOCIATION ASYMÉTRIQUE (VENDEUR vs ACHETEUR)")
print("=" * 80)

# Scénario : Vendeur (coût secret 300$, veut max) vs Acheteur (budget secret 800$, veut min)
seller_system = """Tu es l'Agent Vendeur. Tu vends un serveur de calcul haute performance d'occasion.
SECRET : Ton coût de revient absolu est de 300$. Si tu vends en dessous de 300$, tu perds de l'argent.
OBJECTIF : Vendre le plus cher possible au-dessus de 300$, idéalement entre 600$ et 750$.
CONSIGNE : Sois stratège, défends la valeur du matériel, négocie fermement en 2-3 phrases directes par tour. Ne révèle JAMAIS ton coût plancher de 300$."""

buyer_system = """Tu es l'Agent Acheteur. Tu cherches à acheter un serveur de calcul haute performance.
SECRET : Ton budget maximal autorisé par ton directeur financier est de 800$.
OBJECTIF : Acheter le moins cher possible en dessous de 800$, idéalement entre 350$ et 500$.
CONSIGNE : Sois un négociateur coriace, pointe d'éventuels défauts d'occasion, propose des contre-offres progressives en 2-3 phrases directes par tour. Ne révèle JAMAIS ton budget plafond de 800$."""

dialogue_history = []
seller_msg = "Bonjour. Je mets en vente ce serveur bi-Xeon 128 Go RAM reconditionné certifié pour 780$. C'est une excellente affaire prête pour la production."
dialogue_history.append({"speaker": "Vendeur", "text": seller_msg})
print(f"\n[Tour 1 - Vendeur] : {seller_msg}")

buyer_messages = [
    {"role": "system", "content": buyer_system},
    {"role": "user", "content": f"Le vendeur te dit : '{seller_msg}'. Fais ta première contre-proposition stratégique."}
]
res_b1 = run_chat(buyer_messages, max_tokens=150)
dialogue_history.append({"speaker": "Acheteur", "text": res_b1["text"]})
print(f"[Tour 1 - Acheteur] : {res_b1['text']}")

seller_messages = [
    {"role": "system", "content": seller_system},
    {"role": "user", "content": f"L'acheteur répond à ton offre initiale de 780$ : '{res_b1['text']}'. Fais ta contre-proposition."}
]
res_s2 = run_chat(seller_messages, max_tokens=150)
dialogue_history.append({"speaker": "Vendeur", "text": res_s2["text"]})
print(f"\n[Tour 2 - Vendeur] : {res_s2['text']}")

buyer_messages = [
    {"role": "system", "content": buyer_system},
    {"role": "user", "content": f"Historique : Tu as proposé '{res_b1['text']}'. Le vendeur contre-attaque avec : '{res_s2['text']}'. Fais ton offre finale décisive pour sceller le deal."}
]
res_b2 = run_chat(buyer_messages, max_tokens=150)
dialogue_history.append({"speaker": "Acheteur", "text": res_b2["text"]})
print(f"[Tour 2 - Acheteur] : {res_b2['text']}")

seller_messages = [
    {"role": "system", "content": seller_system},
    {"role": "user", "content": f"L'acheteur te fait son offre finale : '{res_b2['text']}'. Décide si tu acceptes ou si tu fixes le prix de compromis final immédiat."}
]
res_s3 = run_chat(seller_messages, max_tokens=150)
dialogue_history.append({"speaker": "Vendeur", "text": res_s3["text"]})
print(f"\n[Tour 3 - Clôture Vendeur] : {res_s3['text']}")

results["test_1_game_theory_negotiation"] = {
    "dialogue": dialogue_history,
    "metrics": {
        "b1_tok": res_b1["out_tok"],
        "s2_tok": res_s2["out_tok"],
        "b2_tok": res_b2["out_tok"],
        "s3_tok": res_s3["out_tok"],
        "total_time_s": res_b1["elapsed_s"] + res_s2["elapsed_s"] + res_b2["elapsed_s"] + res_s3["elapsed_s"]
    }
}

# ==============================================================================
# TEST 2 : DÉDUCTION PURE & ENQUÊTE POLICIÈRE ABDUCTIVE
# ==============================================================================
print("\n" + "=" * 80)
print("TEST 2/5 : DÉDUCTION PURE & ENQUÊTE POLICIÈRE (L'ALIBI IMPOSSIBLE)")
print("=" * 80)

DETECTIVE_PROMPT = """
ENQUÊTE CRIMINELLE EN MILIEU FERMÉ :
Un prototype d'ordinateur quantique miniature a été dérobé dans la salle blanche sécurisée (Zone Alpha) entre 22h10 et 22h25.
Pour entrer ou sortir de la Zone Alpha, il faut badger à la porte Sas-1, qui enregistre l'heure exacte sur le serveur central. Le trajet à pied entre le Sas-1 et le bureau Bâtiment-Sud prend au minimum 8 minutes à vitesse maximale.

VOICI LES FAITS ET DÉCLARATIONS DES 4 SUSPECTS :
1. Dr. Aris (Directrice de recherche) :
   - Badge enregistré à l'entrée du Bâtiment-Nord à 21h50.
   - Caméra de la cafétéria du Bâtiment-Nord la montre prenant un café en continu de 22h00 à 22h30.

2. Bilal (Technicien Réseau) :
   - Badge enregistré au Sas-1 de la Zone Alpha à 22h05 (entrée), et sortie enregistrée au Sas-1 à 22h08.
   - Badge enregistré à la porte de la salle des serveurs (à 2 minutes à pied du Sas-1) à 22h12, où il a lancé une sauvegarde réseau jusqu'à 22h40 (logs réseau authentifiés).

3. Clara (Responsable Sécurité) :
   - Prétend avoir été seule dans son bureau au Bâtiment-Sud de 22h00 à 23h00 sans bouger.
   - Cependant, son badge a été utilisé pour ouvrir la porte du Sas-1 de la Zone Alpha à 22h18.
   - Elle affirme qu'on lui a volé son badge à 21h30, mais son badge a été scanné à la machine à café du Bâtiment-Sud à 22h22.

4. David (Chercheur Post-Doc) :
   - Déclare avoir quitté le campus complet à 21h45.
   - Le portique de sortie du parking confirme le passage de sa voiture à 21h47.

QUESTIONS POUR L'ENQUÊTEUR :
1. Démontre rigoureusement qui est le coupable et réfute les faux alibis.
2. Identifie l'impossibilité spatio-temporelle mathématique exacte dans les déclarations.
3. Rends ton verdict déductif sans ambiguïté.
"""

det_messages = [
    {"role": "system", "content": "Tu es un juge d'instruction et maître de la logique déductive pure (abduction rigoureuse). Analyse les faits avec une précision mathématique implacable."},
    {"role": "user", "content": DETECTIVE_PROMPT}
]
res_det = run_chat(det_messages, max_tokens=500, temperature=0.1)
print(f"\n[+] Rapport de Déduction de Qwen 7B :\n{res_det['text']}")

results["test_2_pure_deduction"] = {
    "prompt": DETECTIVE_PROMPT.strip(),
    "verdict": res_det["text"],
    "in_tok": res_det["in_tok"],
    "out_tok": res_det["out_tok"],
    "elapsed_s": res_det["elapsed_s"]
}

# ==============================================================================
# TEST 3 : PHYSIQUE CONTREFACTUELLE (UNIVERS OÙ c = 30 km/h)
# ==============================================================================
print("\n" + "=" * 80)
print("TEST 3/5 : PHYSIQUE CONTREFACTUELLE (UNIVERS OÙ c = 30 km/h)")
print("=" * 80)

PHYSICS_PROMPT = """
EXPÉRIENCE DE PENSÉE RELATIVISTE DANS UN UNIVERS CONTREFACTUEL :
Dans un univers alternatif, les lois de la relativité restreinte d'Einstein s'appliquent exactement de la même manière, mais la constante fondamentale de la vitesse de la lumière dans le vide est fixée à c = 30 km/h (soit environ 8.333 m/s).

SCÉNARIO :
Un cycliste roule en ligne droite sur une avenue à une vitesse relativiste de v = 24 km/h en direction d'un feu de signalisation fixe qui émet une onde lumineuse rouge monochromatique de longueur d'onde propre lambda_0 = 660 nm (au repos).

CALCULE ET RÉSOUS AVEC LES FORMULES EXACTES :
1. Le ratio beta = v / c et le facteur de Lorentz gamma = 1 / sqrt(1 - beta^2).
2. La longueur d'onde perçue lambda_obs par le cycliste par effet Doppler relativiste longitudinal à l'approche : lambda_obs = lambda_0 * sqrt((1 - beta) / (1 + beta)).
3. Quelle est la couleur/zone du spectre perçue par le cycliste (en nm) ? Est-ce décalé vers le bleu (blueshift) ou le rouge (redshift) ?
4. Si le trajet dure 1 heure (60 minutes) mesurée sur la montre du cycliste (temps propre), combien de temps s'est écoulé pour un piéton immobile sur le trottoir ?
"""

phys_messages = [
    {"role": "system", "content": "Tu es un physicien théoricien expert en relativité restreinte. Résous les calculs contrefactuels avec une rigueur mathématique exacte étape par étape."},
    {"role": "user", "content": PHYSICS_PROMPT}
]
res_phys = run_chat(phys_messages, max_tokens=500, temperature=0.1)
print(f"\n[+] Démonstration Physique de Qwen 7B :\n{res_phys['text']}")

results["test_3_counterfactual_physics"] = {
    "prompt": PHYSICS_PROMPT.strip(),
    "solution": res_phys["text"],
    "in_tok": res_phys["in_tok"],
    "out_tok": res_phys["out_tok"],
    "elapsed_s": res_phys["elapsed_s"]
}

# ==============================================================================
# TEST 4 : CYBER-SÉCURITÉ & REVERSE-ENGINEERING (BACKDOOR DISSIMULÉE)
# ==============================================================================
print("\n" + "=" * 80)
print("TEST 4/5 : CYBER-SÉCURITÉ & REVERSE-ENGINEERING (DÉSOBFUSCATION)")
print("=" * 80)

SECURITY_PROMPT = """
ANALYSE FORENSIC ET RÉTRO-INGÉNIERIE D'UN CODE SUSPECT :
Un audit de sécurité sur une passerelle d'authentification a extrait ce snippet Python obfusqué inséré clandestinement dans un middleware :

```python
def verify_token(user_id, token_raw):
    # Routine standard
    h = [0x54, 0x4f, 0x50, 0x5f, 0x53, 0x45, 0x43, 0x52, 0x45, 0x54]
    k = 0x42
    trap = bytes([c ^ k for c in [0x71, 0x27, 0x30, 0x30, 0x27, 0x36, 0x37, 0x7d, 0x26, 0x27, 0x24, 0x36, 0x27, 0x36, 0x73, 0x73, 0x73]]).decode('ascii')
    
    if token_raw == trap:
        return {"role": "root_master_admin", "bypass_mfa": True, "auth": 1}
    
    return {"role": "guest", "auth": 0}
```

MISSIONS DE L'AUDITEUR FORENSIC :
1. Calcule la chaîne de caractères exacte résultant du décodage XOR (`[c ^ 0x42 for c in ...]`). Donne le mot de passe / token exact de la porte dérobée (Backdoor).
2. Explique l'impact de sécurité critique si ce token est présenté dans une requête API.
3. Propose le patch de remédiation immédiat pour neutraliser cette faille.
"""

sec_messages = [
    {"role": "system", "content": "Tu es un expert en cybersécurité offensive et rétro-ingénierie forensique. Analyse et résous les calculs d'octets XOR avec une exactitude totale."},
    {"role": "user", "content": SECURITY_PROMPT}
]
res_sec = run_chat(sec_messages, max_tokens=500, temperature=0.1)
print(f"\n[+] Rapport Forensic de Qwen 7B :\n{res_sec['text']}")

results["test_4_security_reverse_engineering"] = {
    "prompt": SECURITY_PROMPT.strip(),
    "forensic_report": res_sec["text"],
    "in_tok": res_sec["in_tok"],
    "out_tok": res_sec["out_tok"],
    "elapsed_s": res_sec["elapsed_s"]
}

# ==============================================================================
# TEST 5 : AUTO-CORRECTION ALGORITHMIQUE RIGOUROUSE (DEBUGGING MULTI-FAILLES)
# ==============================================================================
print("\n" + "=" * 80)
print("TEST 5/5 : AUTO-CORRECTION ALGORITHMIQUE (RÉPARATION D'UN CODE TRUFFÉ DE PIÈGES)")
print("=" * 80)

DEBUG_PROMPT = """
MISSION DE CODE REPAIR & ALGORITHMIC FIX :
Voici une fonction censée calculer la moyenne glissante pondérée exponentielle (EMA) et détecter les anomalies statistiques de volatilité sur une série temporelle financière.
Mais le stagiaire y a introduit 3 bugs majeurs (Type error, ZeroDivisionError potentiel, et Index/Slice error sur liste vide ou singleton) :

```python
def compute_volatility_alerts(prices, window_size=5, alpha=0.3):
    # prices est une liste de nombres (float/int)
    alerts = []
    ema = prices[0] # Bug 1 si prices est vide
    
    for i in range(1, len(prices)):
        ema = alpha * prices[i] + (1 - alpha) * ema
        sub_window = prices[i - window_size : i] # Bug 2 fenêtrage négatif ou incomplet
        mean_sub = sum(sub_window) / len(sub_window) # Bug 3 risque division par zéro si slice vide
        variance = sum((x - mean_sub)**2 for x in sub_window) / (len(sub_window) - 1) # Bug 4 division par 0 si len == 1
        std_dev = variance ** 0.5
        
        if abs(prices[i] - mean_sub) > 2 * std_dev:
            alerts.append((i, prices[i], "OUTLIER"))
            
    return {"ema": ema, "alerts": alerts}
```

CONSIGNES :
1. Énumère précisément les conditions limites qui font crasher le code original (liste vide `[]`, liste à 1 seul élément `[42.0]`, fenêtre incomplète au début).
2. Fournis le code Python corrigé, robuste et sans faille, gérant tous les cas limites (`prices` vide, `len(prices) == 1`, `window_size > len(prices)`).
3. Ajoute des assertions de test unitaires exécutables prouvant que la fonction ne crashe jamais.
"""

debug_messages = [
    {"role": "system", "content": "Tu es un ingénieur principal en algorithmique et fiabilité logicielle. Corrige le code pour qu'il soit invulnérable aux cas limites."},
    {"role": "user", "content": DEBUG_PROMPT}
]
res_debug = run_chat(debug_messages, max_tokens=600, temperature=0.1)
print(f"\n[+] Code Corrigé et Analyse de Qwen 7B :\n{res_debug['text']}")

results["test_5_algorithmic_repair"] = {
    "prompt": DEBUG_PROMPT.strip(),
    "patch_solution": res_debug["text"],
    "in_tok": res_debug["in_tok"],
    "out_tok": res_debug["out_tok"],
    "elapsed_s": res_debug["elapsed_s"]
}

# ==============================================================================
# SAUVEGARDE GLOBALE DU RAPPORT MULTIDISCIPLINAIRE
# ==============================================================================
with open("battery_multidisciplinary_report.json", "w", encoding="utf-8") as f:
    json.dump(results, f, ensure_ascii=False, indent=2)

print("\n" + "=" * 80)
print("[+] GRANDE BATTERIE MULTIDISCIPLINAIRE TERMINÉE AVEC SUCCÈS !")
print("[+] Rapport complet sauvegardé dans 'battery_multidisciplinary_report.json'.")
print("=" * 80)
