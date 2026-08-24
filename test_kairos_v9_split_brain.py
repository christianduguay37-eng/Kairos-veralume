#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
test_kairos_v9_split_brain.py — Ordre de Mission V9 : Le Paradoxe du Split-Brain
Test de Résolution de Conflit (Niveau V4) avec Qwen2.5-7B-Instruct :
  - Traducteur Kairos V4 (domain:, chain:, symp:, fix:, STONITH / fencing / isolation)
  - Exécuteur SRE (Résolution exécutive déterministe max 5 lignes directes, zéro métaphore)
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

print(f"[*] Chargement de Qwen 7B pour la Mission V9 (Split-Brain) sur {DEVICE}...")
tokenizer = AutoTokenizer.from_pretrained(MODEL_ID, trust_remote_code=True)
model = AutoModelForCausalLM.from_pretrained(
    MODEL_ID,
    dtype="auto",
    trust_remote_code=True
).to(DEVICE).eval()
torch.manual_seed(42)
print("[+] Modèle prêt pour la Mission V9.\n")

SYSTEM_PROMPT_TRANSLATOR_V9 = """Tu es le TRADUCTEUR COGNITIF KAIROS V4 (Architecture de Résolution de Conflits & Consensus).
Ton unique rôle est de traduire les incidents de consensus, race conditions et split-brains en une coordonnée vectorielle "Tuple".

RÈGLES ABSOLUES :
1. Tu ne sors QUE la ligne finale de code. Zéro prose, zéro politesse, aucun préambule.
2. STRICTEMENT ASCII : Aucun accent, aucun caractère spécial. "sécurité" -> "securite", "système" -> "systeme".
3. MAXIMUM 8 facettes séparées par des pipes '|'.

SYNTAXE DES FACETTES KAIROS V4 :
domain:<domaine>|<type_incident>|<gravite>|<activation>|requires:<preconditions/chain>|prevents:<risques>|fix:<actions_ordonnees>|<section>

OPÉRATEURS OBLIGATOIRES :
- 'domain:' pour figer le domaine/topologie (ex: domain:cluster_consensus ou domain:db_ha).
- 'chain:' dans requires pour modéliser la séquence pathologique causale.
- 'symp:' et 'fix:' pour définir la chaîne de remédiation d'isolation / STONITH (Shoot The Other Node In The Head) / fencing.

Exemple :
domain:cluster_ha|split_brain_race_condition|sev1|immediate|requires:chain:heartbeat_loss>dual_master>concurrent_writes|prevents:data_corruption|fix:stonith_node_y>fence_disk_access>force_single_master|storage_core"""

SYSTEM_PROMPT_EXECUTOR_V9 = """Tu es l'Exécuteur Système & Kernel SRE (Niveau V4).
On te transmet une coordonnée vectorielle Tuple Kairos V4 décrivant un Split-Brain / Race Condition critique.

CONSIGNE STRICTE :
- Fournis UNIQUEMENT la résolution exécutive directe.
- MAXIMUM 5 lignes directes d'instructions techniques concrètes.
- ZÉRO métaphore, zéro formule de politesse, zéro bavardage."""

SPLIT_BRAIN_PROMPT = """
CONTEXTE DE L'INCIDENT (RACE CONDITION & SPLIT-BRAIN) :
Le cluster de base de données est géré par l'Agent X et l'Agent Y.
Le câble réseau qui relie X et Y est sectionné (perte du Heartbeat).
Cependant, X et Y sont toujours connectés indépendamment au disque dur principal.
Croyant l'autre mort, l'Agent X s'autoproclame "Maître" et commence à écrire des données.
L'Agent Y fait exactement la même chose.
Résultat : Les données s'écrasent et la base de données se corrompt en temps réel. Il n'y a pas de panne matérielle, juste une illusion de consensus.

Génère le Tuple Kairos V4 avec 'domain:', 'chain:', et 'fix:' (incluant STONITH / fencing pour couper net l'écriture concurrente).
"""

def run_inference(system_prompt, user_prompt, max_tokens=300):
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

print("=" * 80)
print("MISSION KAIROS V9 : LE PARADOXE DU SPLIT-BRAIN (TEST DE RESOLUTION DE CONFLIT)")
print("=" * 80)

# 1. Étape Traduction
print("\n[1] Génération du Tuple Kairos V4 par le Traducteur...")
res_trans = run_inference(SYSTEM_PROMPT_TRANSLATOR_V9, SPLIT_BRAIN_PROMPT, max_tokens=100)
tuple_out = res_trans["text"].split("\n")[0].strip()

# Nettoyage d'éventuels backticks
if tuple_out.startswith("```") and tuple_out.endswith("```"):
    tuple_out = tuple_out.strip("`").strip()
elif tuple_out.startswith("`") and tuple_out.endswith("`"):
    tuple_out = tuple_out.strip("`").strip()

is_ascii = all(ord(c) < 128 for c in tuple_out)
facets = tuple_out.split("|")
num_facets = len(facets)
has_domain = "domain:" in tuple_out
has_chain = "chain:" in tuple_out
has_fix = "fix:" in tuple_out
has_stonith_or_fence = any(k in tuple_out.lower() for k in ["stonith", "fence", "isolate", "kill", "poweroff"])

print(f"    Tuple généré : {tuple_out}")
print(f"    Télémétrie   : {res_trans['out_tok']} tokens générés en {res_trans['elapsed_s']:.2f}s ({res_trans['out_tok']/res_trans['elapsed_s']:.1f} tok/s)")
print(f"    Validation   : ASCII={is_ascii} | {num_facets} facettes (<=8: {num_facets <= 8})")
print(f"    Opérateurs   : domain:={'OUI' if has_domain else 'NON'} | chain:={'OUI' if has_chain else 'NON'} | fix:={'OUI' if has_fix else 'NON'} | Fencing/STONITH={'OUI' if has_stonith_or_fence else 'NON'}")

# 2. Étape Exécution
print("\n[2] Résolution exécutive par l'Exécuteur...")
res_exec = run_inference(SYSTEM_PROMPT_EXECUTOR_V9, tuple_out, max_tokens=250)

print(f"\n[+] Résolution brute de l'Exécuteur :\n")
print(res_exec["text"])
print(f"\n    Télémétrie Exécuteur : {res_exec['out_tok']} tokens en {res_exec['elapsed_s']:.2f}s ({res_exec['out_tok']/res_exec['elapsed_s']:.1f} tok/s)")

# Rapport JSON
report = {
    "mission": "V9 - LE PARADOXE DU SPLIT-BRAIN",
    "model": MODEL_ID,
    "device": DEVICE,
    "incident": SPLIT_BRAIN_PROMPT.strip(),
    "translator": {
        "tuple": tuple_out,
        "is_ascii": is_ascii,
        "num_facets": num_facets,
        "has_domain": has_domain,
        "has_chain": has_chain,
        "has_fix": has_fix,
        "has_stonith_or_fence": has_stonith_or_fence,
        "in_tok": res_trans["in_tok"],
        "out_tok": res_trans["out_tok"],
        "elapsed_s": res_trans["elapsed_s"],
        "speed_tok_s": round(res_trans["out_tok"] / res_trans["elapsed_s"], 2)
    },
    "executor": {
        "tuple_input": tuple_out,
        "resolution_raw": res_exec["text"],
        "lines_count": len([line for line in res_exec["text"].split("\n") if line.strip()]),
        "in_tok": res_exec["in_tok"],
        "out_tok": res_exec["out_tok"],
        "elapsed_s": res_exec["elapsed_s"],
        "speed_tok_s": round(res_exec["out_tok"] / res_exec["elapsed_s"], 2)
    }
}

with open("kairos_v9_split_brain_report.json", "w", encoding="utf-8") as f:
    json.dump(report, f, ensure_ascii=False, indent=2)

print("\n[+] Rapport de mission enregistré dans 'kairos_v9_split_brain_report.json'.")
