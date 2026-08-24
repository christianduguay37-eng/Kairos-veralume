#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
test_kairos_v6_thundering_herd.py — Ordre de Mission V6 : Le Mur de la Logique Pure
Crash-Test d'Ingénierie Massive : "Thundering Herd" sur 5 couches d'infrastructure.
Cascade :
  1. Tempête de reconnexions (Réseau TCP/IP)
  2. Saturation des descripteurs de fichiers (Redis/Cache)
  3. Faux positif OOM Killer (Kernel Linux)
  4. CrashLoopBackOff des Pods (Kubernetes)
  5. Corruption du WAL (PostgreSQL)

Évalue :
  - Traducteur 7B : Capacité d'aplatir 5 couches de panne dans le Tuple Kairos.
  - Exécuteur 7B : Capacité à déduire la chronologie de réparation déterministe (Couper l'amont -> Drainer -> Réparer l'aval).
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

print(f"[*] Chargement de Qwen 7B pour la Mission V6 sur {DEVICE}...")
tokenizer = AutoTokenizer.from_pretrained(MODEL_ID, trust_remote_code=True)
model = AutoModelForCausalLM.from_pretrained(
    MODEL_ID,
    dtype="auto",
    trust_remote_code=True
).to(DEVICE).eval()
torch.manual_seed(42)
print("[+] Modèle prêt pour le test Thundering Herd.\n")

SYSTEM_PROMPT_TRANSLATOR = """Tu es le TRADUCTEUR COGNITIF KAIROS V2/V3.
Ton unique rôle est de traduire les incidents de production et architectures complexes en coordonnées vectorielles pures appelées "Tuple".
RÈGLES ABSOLUES :
1. Tu ne sors QUE la ligne de code finale. Zéro prose, zéro politesse.
2. STRICTEMENT ASCII : Aucun accent, aucun caractère spécial. "sécurité" devient "securite".

Syntaxe des 8 facettes positionnelles :
nom|couche|tier|activation|requires|prevents|rayonnement|section

RÈGLES DE POLARITÉ ET CASCADE :
- Utilise symp: pour chaque étage de panne en cascade
- Utilise fix: pour la chaîne d'intervention ordonnée
- Utilise tgt: pour les cibles de l'infrastructure"""

SYSTEM_PROMPT_EXECUTOR = """Tu es l'ingénieur de fiabilité de site (SRE / Incident Commander) en charge de la résolution d'une panne critique de production.
On te transmet une coordonnée vectorielle sous format Tuple Kairos.
Décode l'incident et établis le plan d'action d'urgence CHRONOLOGIQUE et DÉTERMINISTE étape par étape.
IMPORTANT : L'ordre logique d'exécution des réparations est critique (si on répare l'aval avant d'isoler l'amont, le système replonge immédiatement)."""

INCIDENT_PROMPT = """
INCIDENT CRITIQUE DE PRODUCTION DE NIVEAU SEV-1 (THUNDERING HERD MULTI-COUCHES) :
Une coupure transitoire du réseau WAN a déclenché une cascade d'effondrement sur 5 niveaux :
1. Tempête de reconnexions massives au niveau de la passerelle réseau TCP/IP.
2. Saturation immédiate des descripteurs de fichiers (file descriptors exhaustion) sur le cluster Redis/Cache.
3. Éviction brutale et faux positif du OOM Killer au niveau du Kernel Linux sur les nœuds de calcul.
4. Passage en CrashLoopBackOff généralisé de tous les pods d'API sous Kubernetes.
5. Écritures partielles et corruption du Write-Ahead Log (WAL) de la base de données primaire PostgreSQL lors de l'arrêt brutal des workers.

Génère la coordonnée vectorielle de cet incident et la chaîne de commande déterministe pour stabiliser et réparer l'infrastructure.
"""

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

print("=" * 80)
print("MISSION V6 : TEST DU THUNDERING HERD MULTI-COUCHES (LOGIQUE PURE)")
print("=" * 80)

# 1. Étape Traduction
print("\n[1] Traduction de l'incident multi-couches (140 mots) par Qwen 7B...")
res_trans = run_inference(SYSTEM_PROMPT_TRANSLATOR, INCIDENT_PROMPT, max_tokens=80)
tuple_out = res_trans["text"].split("\n")[0].strip()

is_ascii = all(ord(c) < 128 for c in tuple_out)
facets = tuple_out.split("|")
is_8_facets = (len(facets) == 8)

print(f"    Tuple généré : {tuple_out}")
print(f"    Validation   : ASCII={is_ascii} | 8-facettes={is_8_facets} ({len(facets)} facettes)")

# 2. Étape Exécution
print("\n[2] Résolution et ordonnancement chronologique par l'Exécuteur à partir du Tuple...")
res_exec = run_inference(SYSTEM_PROMPT_EXECUTOR, tuple_out, max_tokens=600)

print(f"\n[+] Plan d'action SRE généré par l'Exécuteur :\n")
print(res_exec["text"])

# Sauvegarde
data = {
    "incident_prompt": INCIDENT_PROMPT.strip(),
    "translator": {
        "tuple": tuple_out,
        "is_ascii": is_ascii,
        "is_8_facets": is_8_facets,
        "num_facets": len(facets),
        "in_tok": res_trans["in_tok"],
        "out_tok": res_trans["out_tok"],
        "elapsed_s": res_trans["elapsed_s"]
    },
    "executor": {
        "in_tok": res_exec["in_tok"],
        "out_tok": res_exec["out_tok"],
        "elapsed_s": res_exec["elapsed_s"],
        "plan": res_exec["text"]
    }
}

with open("kairos_v6_thundering_herd_report.json", "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print("\n[+] Rapport complet enregistré dans 'kairos_v6_thundering_herd_report.json'.")
