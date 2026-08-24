#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
test_kairos_v7_chain_patch.py — Ordre de Mission V7 : Le Patch de la Dernière Chance
Test du Thundering Herd à 5 couches avec :
  1. Préfixe de domaine explicite : domain:infrastructure_cascade|...
  2. Opérateur de chaîne causale directionnelle : chain:reseau>redis>oom>k8s>wal dans requires:
  3. Polarités fix: et symp: pour forcer l'ordre de réparation amont -> aval.
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

print(f"[*] Chargement de Qwen 7B pour la Mission V7 (Patch Chain/Cascade) sur {DEVICE}...")
tokenizer = AutoTokenizer.from_pretrained(MODEL_ID, trust_remote_code=True)
model = AutoModelForCausalLM.from_pretrained(
    MODEL_ID,
    dtype="auto",
    trust_remote_code=True
).to(DEVICE).eval()
torch.manual_seed(42)
print("[+] Modèle prêt pour le test V7.\n")

SYSTEM_PROMPT_TRANSLATOR_V7 = """Tu es le TRADUCTEUR COGNITIF KAIROS V3 (Architecture à Enchaînement Causal).
Ton unique rôle est de traduire les incidents complexes et pannes multi-couches en une coordonnée vectorielle "Tuple".

RÈGLES ABSOLUES :
1. Tu ne sors QUE la ligne finale de code. Zéro prose, zéro politesse.
2. STRICTEMENT ASCII : Aucun accent, aucun caractère spécial. "sécurité" devient "securite".

GRAMMAIRE DES 8 FACETTES KAIROS V3 :
domaine|type_panne|gravite_tier|activation|requires|prevents|rayonnement|section

NOUVEAUX OPÉRATEURS OBLIGATOIRES (PATCH V7) :
1. "domaine" : DOIT TOUJOURS commencer par "domain:" pour fixer la topologie (ex: domain:infrastructure_cascade).
2. "requires" : POUR LES PANNES EN CASCADE, tu DOIS utiliser l'opérateur de chaîne "chain:" avec des flèches ">" pour indiquer la dépendance causale de l'amont vers l'aval.
   Exemple : requires:chain:reseau>redis>oom>k8s>wal
3. Utilise symp: (symptôme) et fix: (action de remédiation ordonnée de la source amont vers la cible aval).

Exemple complet :
domain:infrastructure_cascade|thundering_herd|sev1|immediate|requires:chain:reseau>redis>oom>k8s>wal|prevents:data_loss|fix:isolate_wan>flush_redis>restart_k8s>recover_wal|infra_core"""

SYSTEM_PROMPT_EXECUTOR_V7 = """Tu es l'ingénieur en chef SRE (Incident Commander) de niveau L4.
On te transmet une coordonnée vectorielle Tuple Kairos V3 contenant un opérateur de chaîne causale "chain:A>B>C>D>E".
L'opérateur "chain:" indique formellement l'ordre de dépendance des pannes (A est la cause racine amont, E est la conséquence finale aval).

CONSIGNE DÉTERMINISTE STRICTE :
Tu dois exécuter le plan d'urgence dans l'ordre chronologique de la chaîne de causalité :
Couper/Isoler l'amont (A) d'abord, puis stabiliser de proche en proche jusqu'à la réparation de l'aval (E).
Fournis le protocole de crise étape par étape."""

INCIDENT_PROMPT = """
INCIDENT CRITIQUE DE PRODUCTION DE NIVEAU SEV-1 (THUNDERING HERD MULTI-COUCHES) :
Une coupure transitoire du réseau WAN a déclenché une cascade d'effondrement sur 5 niveaux :
1. Tempête de reconnexions massives au niveau de la passerelle réseau TCP/IP.
2. Saturation immédiate des descripteurs de fichiers (file descriptors exhaustion) sur le cluster Redis/Cache.
3. Éviction brutale et faux positif du OOM Killer au niveau du Kernel Linux sur les nœuds de calcul.
4. Passage en CrashLoopBackOff généralisé de tous les pods d'API sous Kubernetes.
5. Écritures partielles et corruption du Write-Ahead Log (WAL) de la base de données primaire PostgreSQL lors de l'arrêt brutal des workers.

Génère la coordonnée vectorielle de cet incident avec l'opérateur chain: et la chaîne de commande déterministe pour stabiliser et réparer l'infrastructure.
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
print("MISSION V7 : LE TEST DU PATCH CAUSAL (domain: + chain:A>B>C>D>E)")
print("=" * 80)

# 1. Étape Traduction
print("\n[1] Traduction de l'incident avec les armes Kairos V3...")
res_trans = run_inference(SYSTEM_PROMPT_TRANSLATOR_V7, INCIDENT_PROMPT, max_tokens=80)
tuple_out = res_trans["text"].split("\n")[0].strip()

is_ascii = all(ord(c) < 128 for c in tuple_out)
facets = tuple_out.split("|")
is_8_facets = (len(facets) == 8)
has_chain = "chain:" in tuple_out
has_domain = "domain:" in tuple_out

print(f"    Tuple généré : {tuple_out}")
print(f"    Validation   : ASCII={is_ascii} | 8-facettes={is_8_facets} ({len(facets)} facettes)")
print(f"    Opérateurs   : domain:={'OUI' if has_domain else 'NON'} | chain:={'OUI' if has_chain else 'NON'}")

# 2. Étape Exécution
print("\n[2] Résolution et ordonnancement chronologique par l'Exécuteur à partir du Tuple V3...")
res_exec = run_inference(SYSTEM_PROMPT_EXECUTOR_V7, tuple_out, max_tokens=650)

print(f"\n[+] Plan d'action SRE ordonné par l'Exécuteur :\n")
print(res_exec["text"])

# Sauvegarde
data = {
    "incident_prompt": INCIDENT_PROMPT.strip(),
    "translator": {
        "tuple": tuple_out,
        "is_ascii": is_ascii,
        "is_8_facets": is_8_facets,
        "has_chain": has_chain,
        "has_domain": has_domain,
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

with open("kairos_v7_chain_patch_report.json", "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print("\n[+] Rapport complet enregistré dans 'kairos_v7_chain_patch_report.json'.")
