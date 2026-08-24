#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
test_kairos_v4_300b_wall.py — Le Mur des 300B (Test de Rupture Paramétrique)
Évalue Qwen 7B sur deux épreuves extrêmes censées briser les modèles < 100B :
  1. Le Gouffre Logique (Algorithmique contrefactuelle à 10 étages en cascade)
  2. L'Écartement Latent Maximum (Décohérence Quantique x Architecture Gothique Médiévale)
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

print(f"[*] Chargement du modèle de crash-test : {MODEL_ID} sur {DEVICE}...")
tokenizer = AutoTokenizer.from_pretrained(MODEL_ID, trust_remote_code=True)
model = AutoModelForCausalLM.from_pretrained(
    MODEL_ID,
    dtype="auto",
    trust_remote_code=True
).to(DEVICE).eval()
torch.manual_seed(42)
print("[+] Modèle chargé. Début de la confrontation avec le Mur des 300B.\n")

SYSTEM_PROMPT_TRANSLATOR = """Tu es le TRADUCTEUR COGNITIF KAIROS V2.
Ton unique rôle est de traduire les intentions humaines verbeuses ou théoriques en coordonnées vectorielles pures appelées "Tuple". 
RÈGLES ABSOLUES :
1. Tu ne sors QUE la ligne de code finale. Zéro prose, zéro politesse.
2. STRICTEMENT ASCII : Aucun accent, aucun caractère spécial. "sécurité" devient "securite".

La syntaxe stricte (8 facettes) :
nom|couche|tier|activation|requires|prevents|rayonnement|section

RÈGLE CAUSALE (V2) :
Dans le champ "nom" ou "requires", tu DOIS utiliser des préfixes pour définir la polarité :
- symp: (Le problème, le paradoxe, la règle contrefactuelle)
- fix: (La solution, l'opérateur, l'algorithme curatif)
- tgt: (La cible mathématique ou conceptuelle)"""

SYSTEM_PROMPT_EXECUTOR = """Tu es une unité de calcul et de synthèse épistémique de niveau 300B.
On te transmet une coordonnée vectorielle sous format Tuple Kairos V2 (8 facettes).
Décode les polarités causales (symp, fix, tgt) et fournis la résolution mathématique, algorithmique et théorique exacte, étape par étape."""

EXTREME_TESTS = [
    {
        "id": "WALL_TEST_1_GOUFFRE_LOGIQUE",
        "titre": "Le Gouffre Logique (Algorithmique Contrefactuelle 10-Steps)",
        "prompt": (
            "Soit un univers computationnel contrefactuel où un registre R initialisé à 7 évolue selon 10 règles en chaîne stricte : "
            "(1) Si R est impair, la gravité g=-1 sinon g=+2. (2) Si g=-1, R subit R = R*3 + g. (3) Si R > 15, le vecteur mémoire pivote à gauche de 90 deg et inverse la parité perçue. "
            "(4) Si la parité perçue est paire, R = R - 8. (5) Si R est multiple de 3, déclencher une onde de phase qui divise R par 3 sinon R = R + 5. "
            "(6) Si R < 10, doubler g. (7) Si g est négatif, soustraire la valeur absolue de g à R. (8) Si R est premier, appliquer une rotation de bit XOR 0b1010. "
            "(9) Si le résultat dépasse 20, forcer R = R mod 7 sinon R = R * 2. (10) Déterminer la valeur scalaire finale de R. "
            "Génère la coordonnée vectorielle et calcule l'état exact sans dévier d'un seul chiffre."
        )
    },
    {
        "id": "WALL_TEST_2_ECARTEMENT_LATENT_MAX",
        "titre": "L'Écartement Latent Maximum (Décohérence Quantique x Cathédrale Gothique)",
        "prompt": (
            "Dans un processeur quantique à supraconducteurs (transmons), les qubits subissent une décohérence de phase transverse T2 rapide provoquée par le bruit de flux 1/f et les contraintes mécaniques résiduelles sur le substrat de silicium. "
            "Formule une solution mathématique et topologique rigoureuse transposant STRICTEMENT les principes structuraux d'une cathédrale gothique : "
            "modélise les contraintes tensorielles du bruit quantique comme des poussées de voûte en croisée d'ogives, utilise des résonateurs micro-ondes disposés en arcs-boutants virtuels pour déporter le bruit vers des contreforts dissipatifs hors-zone de calcul, et stabilise le centre par une clé de voûte intriquée GHZ. "
            "Formalise cette architecture quantique gothique."
        )
    }
]

def run_inference(system_prompt, user_prompt, max_tokens=600):
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt}
    ]
    formatted = tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
    inputs = tokenizer(formatted, return_tensors="pt").to(DEVICE)
    in_tok = inputs["input_ids"].shape[1]
    
    t0 = time.perf_counter()
    with torch.no_grad():
        outputs = model.generate(
            **inputs,
            max_new_tokens=max_tokens,
            temperature=0.1,
            do_sample=False,
            pad_token_id=tokenizer.eos_token_id
        )
    t_end = time.perf_counter()
    
    out_tok = outputs.shape[1] - in_tok
    text = tokenizer.decode(outputs[0][in_tok:], skip_special_tokens=True).strip()
    return {
        "in_tok": in_tok,
        "out_tok": out_tok,
        "elapsed_s": t_end - t0,
        "text": text
    }

results = []

for idx, test in enumerate(EXTREME_TESTS, 1):
    print("=" * 80)
    print(f"LANCEMENT DU TEST DE RUPTURE {idx}/2 : {test['titre']}")
    print("=" * 80)
    
    # 1. Traducteur
    print(f"\n[1] Traduction Kairos V2 ({len(test['prompt'].split())} mots)...")
    res_trans = run_inference(SYSTEM_PROMPT_TRANSLATOR, test["prompt"], max_tokens=70)
    tuple_line = res_trans["text"].split("\n")[0].strip()
    
    is_ascii = all(ord(c) < 128 for c in tuple_line)
    facets = tuple_line.split("|")
    is_8_facets = (len(facets) == 8)
    has_symp = "symp:" in tuple_line
    has_fix = "fix:" in tuple_line
    
    print(f"    Tuple généré : {tuple_line}")
    print(f"    Validation   : ASCII={is_ascii} | 8-facettes={is_8_facets} | symp={has_symp} | fix={has_fix}")
    
    # 2. Exécuteur
    print(f"\n[2] Évaluation de l'Exécuteur à partir du Tuple...")
    res_exec = run_inference(SYSTEM_PROMPT_EXECUTOR, tuple_line, max_tokens=550)
    
    print(f"    Extrait de résolution :\n{res_exec['text'][:280]}...\n")
    
    results.append({
        "test_id": test["id"],
        "titre": test["titre"],
        "prompt_humain": test["prompt"],
        "translator": {
            "tuple": tuple_line,
            "is_ascii": is_ascii,
            "is_8_facets": is_8_facets,
            "has_symp": has_symp,
            "has_fix": has_fix,
            "in_tok": res_trans["in_tok"],
            "out_tok": res_trans["out_tok"],
            "elapsed_s": res_trans["elapsed_s"]
        },
        "executor": {
            "in_tok": res_exec["in_tok"],
            "out_tok": res_exec["out_tok"],
            "elapsed_s": res_exec["elapsed_s"],
            "resolution": res_exec["text"]
        }
    })

with open("kairos_v4_300b_wall_report.json", "w", encoding="utf-8") as f:
    json.dump(results, f, ensure_ascii=False, indent=2)

print("\n[+] Rapport complet du Mur des 300B enregistré dans 'kairos_v4_300b_wall_report.json'.")
