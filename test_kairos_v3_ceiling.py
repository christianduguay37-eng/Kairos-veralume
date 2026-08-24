#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
test_kairos_v3_ceiling.py — Épreuve de Haute Densité Cognitive (Phase 4)
Teste les limites extrêmes de Qwen 7B sur 3 épreuves :
  Épreuve 1 : L'Abstraction Théorique (Épistémologie / Intégration d'information)
  Épreuve 2 : Le Paradoxe Récursif (A -> B -> C -> casse A)
  Épreuve 3 : Le Cross-Domain (Sociologie des organisations + Split-Brain Distribué)

Pour chaque épreuve :
  1. Traduction Prose -> Tuple V2 (Traducteur)
  2. Résolution Tuple V2 -> Diagnostic & Solution (Exécuteur)
  3. Analyse de rupture d'attention (Traducteur vs Exécuteur).
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
print("[+] Modèle prêt pour la Phase 4 (Crash-test Haute Densité).\n")

SYSTEM_PROMPT_TRANSLATOR = """Tu es le TRADUCTEUR COGNITIF KAIROS V2.
Ton unique rôle est de traduire les intentions humaines verbeuses ou théoriques en coordonnées vectorielles pures appelées "Tuple". 
RÈGLES ABSOLUES :
1. Tu ne sors QUE la ligne de code finale. Zéro prose, zéro politesse.
2. STRICTEMENT ASCII : Aucun accent, aucun caractère spécial. "sécurité" devient "securite".

La syntaxe stricte (8 facettes) :
nom|couche|tier|activation|requires|prevents|rayonnement|section

RÈGLE CAUSALE (V2) :
Dans le champ "nom" ou "requires", tu DOIS utiliser des préfixes pour définir la polarité :
- symp: (Le symptôme, le paradoxe, la dégénérescence)
- fix: (La solution curative, l'invariant, le mécanisme)
- tgt: (La cible conceptuelle ou structurelle)"""

SYSTEM_PROMPT_EXECUTOR = """Tu es une unité d'analyse et de résolution d'ingénierie cognitive et systémique de niveau recherche.
On te transmet une coordonnée vectorielle sous format Tuple Kairos V2 (8 facettes).
Décode les polarités causales (symp, fix, tgt) et fournis une résolution théorique, structurelle et opérationnelle rigoureuse."""

TEST_CASES = [
    {
        "id": "EPREUVE_1_ABSTRACTION",
        "titre": "L'Abstraction Théorique (Épistémologie cognitive)",
        "prompt": (
            "Dans une architecture cognitive distribuée, nous observons un effondrement de l'intégration d'information (baisse drastique de Phi / IIT) "
            "lorsque le réseau sur-optimise ses représentations locales : la modularité excessive détruit la conscience phénoménale globale et fragmente l'espace latent en silos hermétiques. "
            "Applique un invariant métacognitif de rétroaction globale (Global Workspace recurrent routing) pour forcer la ré-intégration causale sans détruire la spécialisation des sous-agents."
        )
    },
    {
        "id": "EPREUVE_2_PARADOXE_RECURSIF",
        "titre": "Le Paradoxe Récursif (Chaîne causale à 3 niveaux)",
        "prompt": (
            "Nous faisons face à un paradoxe triangulaire vicieux : un verrouillage trop strict (A) provoque un goulot d'étranglement de latence (B). "
            "Pour réduire la latence (B), l'optimiseur déclenche des écritures optimistes asynchrones (C). "
            "Mais ces écritures optimistes (C) corrompent l'état sous contention et forcent un rollback massif qui réactive et durcit le verrouillage strict (A). "
            "Conçois une solution de découplage par consensus MVCC multi-versions à horloge vectorielle causale pour casser définitivement cette boucle de rétroaction récursive."
        )
    },
    {
        "id": "EPREUVE_3_CROSS_DOMAIN",
        "titre": "Le Cross-Domain (Sociologie organisationnelle + Split-Brain Distribué)",
        "prompt": (
            "Dans une organisation décentralisée autonome, l'asymétrie d'information entre deux factions dirigeantes rivales génère une divergence cognitive analogue à un Split-Brain de base de données partitionnée (théorème CAP). "
            "Chaque faction s'autoproclame quorum légitime et applique des décisions conflictuelles en prod. "
            "Implémente un protocole d'arbitrage par bail de leadership renouvelable avec clôture cryptographique (Fencing Token / Epoch Lease) pour éliminer les écritures zombies et forcer la réconciliation institutionnelle."
        )
    }
]

def run_inference(system_prompt, user_prompt, max_tokens=500):
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

for idx, tc in enumerate(TEST_CASES, 1):
    print("=" * 80)
    print(f"LANCEMENT ÉPREUVE {idx}/3 : {tc['titre']}")
    print("=" * 80)
    
    # 1. Phase Traducteur
    print(f"\n[1] Traduction de la requête humaine ({len(tc['prompt'].split())} mots)...")
    res_trans = run_inference(SYSTEM_PROMPT_TRANSLATOR, tc["prompt"], max_tokens=50)
    tuple_line = res_trans["text"].split("\n")[0].strip()
    
    is_ascii = all(ord(c) < 128 for c in tuple_line)
    facets = tuple_line.split("|")
    is_8_facets = (len(facets) == 8)
    has_symp = "symp:" in tuple_line
    has_fix = "fix:" in tuple_line
    
    print(f"    Tuple produit : {tuple_line}")
    print(f"    Conformité    : ASCII={is_ascii} | 8-facettes={is_8_facets} | symp={has_symp} | fix={has_fix}")
    
    # 2. Phase Exécuteur
    print(f"\n[2] Résolution par l'Exécuteur à partir du Tuple...")
    res_exec = run_inference(SYSTEM_PROMPT_EXECUTOR, tuple_line, max_tokens=450)
    
    print(f"    Extrait de résolution :\n{res_exec['text'][:250]}...\n")
    
    results.append({
        "epreuve_id": tc["id"],
        "titre": tc["titre"],
        "prompt_humain": tc["prompt"],
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

with open("kairos_v3_ceiling_report.json", "w", encoding="utf-8") as f:
    json.dump(results, f, ensure_ascii=False, indent=2)

print("\n[+] Télémétrie complète Phase 4 enregistrée dans 'kairos_v3_ceiling_report.json'.")
