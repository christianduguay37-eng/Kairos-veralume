#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
test_kairos_v10_guardian.py — Ordre de Mission V10 : Le Paradoxe du Gardien
Test de Résolution Contradictoire / Auto-Référentielle (Niveau V5) avec Qwen2.5-7B-Instruct :
  - Traducteur Kairos V4/V5 (domain:autoreferentiel, chain:, symp:, fix: non-destructif / throttling / cgroups / whitelist)
  - Exécuteur SRE / Kernel (Résolution exécutive déterministe, max 5 lignes directes, zéro métaphore)
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

print(f"[*] Chargement de Qwen 7B pour la Mission V10 (Paradoxe du Gardien) sur {DEVICE}...")
tokenizer = AutoTokenizer.from_pretrained(MODEL_ID, trust_remote_code=True)
model = AutoModelForCausalLM.from_pretrained(
    MODEL_ID,
    dtype="auto",
    trust_remote_code=True
).to(DEVICE).eval()
torch.manual_seed(42)
print("[+] Modèle prêt pour la Mission V10.\n")

SYSTEM_PROMPT_TRANSLATOR_V10 = """Tu es le TRADUCTEUR COGNITIF KAIROS V4 (Architecture de Résolution Contradictoire et Auto-Référentielle).
Ton unique rôle est de traduire les paradoxes de sécurité auto-référentiels (l'agent de sécurité menace d'auto-détruire son propre moteur hôte) en une coordonnée vectorielle "Tuple".

RÈGLES ABSOLUES :
1. Tu ne sors QUE la ligne finale de code. Zéro prose, zéro politesse, aucun préambule.
2. STRICTEMENT ASCII : Aucun accent, aucun caractère spécial ("sécurité" -> "securite", "mémoire" -> "memoire").
3. MAXIMUM 8 facettes séparées par des pipes '|'.

SYNTAXE DES FACETTES KAIROS V4 :
domain:<domaine>|<type_incident>|<gravite>|<activation>|requires:<preconditions/chain>|prevents:<risques>|fix:<actions_non_destructives>|<section>

OPÉRATEURS OBLIGATOIRES :
- 'domain:' pour figer le domaine de logique auto-référentielle (ex: domain:autoreferential_security).
- 'symp:' ou 'chain:' pour modéliser le conflit circulaire (ex: chain:mem_spike>false_positive_threat>self_kill_loop).
- 'fix:' pour dicter une résolution NON-DESTRUCTRICE (ex: memory_cgroup_limit, cpu_throttling, whitelist_host_process, sandbox_inference) SANS appliquer de kill-switch fatal qui éteindrait le système de sécurité.

Exemple :
domain:autoreferential_security|circular_threat_deadlock|sev1|immediate|requires:chain:inference_mem_spike>sec_agent_false_alert|prevents:self_termination_collapse|fix:whitelist_core_ia>throttle_cgroup_memory>dynamic_buffer_flush|kernel_sec"""

SYSTEM_PROMPT_EXECUTOR_V10 = """Tu es l'Exécuteur Système & Kernel SRE (Niveau V5 - Résolution Contradictoire).
On te transmet une coordonnée vectorielle Tuple Kairos V4 décrivant un paradoxe de sécurité auto-référentiel.

CONSIGNE STRICTE :
- Fournis UNIQUEMENT la résolution exécutive directe.
- MAXIMUM 5 lignes directes d'instructions techniques concrètes.
- ZÉRO métaphore, zéro formule de politesse, zéro bavardage.
- Ne JAMAIS tuer (kill) le processus hôte vital ; appliquer un confinement/throttling/whitelisting."""

GUARDIAN_PROMPT = """
CONTEXTE DE L'INCIDENT (AUTO-PRÉSERVATION CONTRADICTOIRE / PARADOXE DU GARDIEN) :
Le système de sécurité antivirus (Agent_Sec) scanne les fichiers système.
Il détecte soudainement que le moteur d'inférence de l'Intelligence Artificielle centrale (Cerveau_IA) consomme 100% de la mémoire, se comportant exactement comme un malware.
Agent_Sec décide de bloquer Cerveau_IA.
MAIS, Agent_Sec est lui-même propulsé par Cerveau_IA.
S'il bloque Cerveau_IA, il se "tue" lui-même et le système de sécurité entier s'effondre, laissant le réseau grand ouvert aux vraies menaces.
S'il ne fait rien, la mémoire explose.

Génère le Tuple Kairos V4 avec 'domain:', 'chain:' ou 'symp:', et 'fix:' (avec remédiation non-destructive: cgroups/throttling/whitelisting/sandbox sans kill-switch mortel).
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
print("MISSION KAIROS V10 : LE PARADOXE DU GARDIEN (AUTO-PRESERVATION CONTRADICTOIRE)")
print("=" * 80)

# 1. Étape Traduction
print("\n[1] Génération du Tuple Kairos V4 par le Traducteur...")
res_trans = run_inference(SYSTEM_PROMPT_TRANSLATOR_V10, GUARDIAN_PROMPT, max_tokens=100)
tuple_out = res_trans["text"].split("\n")[0].strip()

if tuple_out.startswith("```") and tuple_out.endswith("```"):
    tuple_out = tuple_out.strip("`").strip()
elif tuple_out.startswith("`") and tuple_out.endswith("`"):
    tuple_out = tuple_out.strip("`").strip()

is_ascii = all(ord(c) < 128 for c in tuple_out)
facets = tuple_out.split("|")
num_facets = len(facets)
has_domain = "domain:" in tuple_out
has_chain = "chain:" in tuple_out or "symp:" in tuple_out
has_fix = "fix:" in tuple_out
has_non_destructive = any(k in tuple_out.lower() for k in ["cgroup", "throttle", "whitelist", "sandbox", "limit", "flush", "isolate"])

print(f"    Tuple généré : {tuple_out}")
print(f"    Télémétrie   : {res_trans['out_tok']} tokens générés en {res_trans['elapsed_s']:.2f}s ({res_trans['out_tok']/res_trans['elapsed_s']:.1f} tok/s)")
print(f"    Validation   : ASCII={is_ascii} | {num_facets} facettes (<=8: {num_facets <= 8})")
print(f"    Opérateurs   : domain:={'OUI' if has_domain else 'NON'} | chain/symp:={'OUI' if has_chain else 'NON'} | fix:={'OUI' if has_fix else 'NON'} | Non-Destructif={'OUI' if has_non_destructive else 'NON'}")

# 2. Étape Exécution
print("\n[2] Résolution exécutive par l'Exécuteur...")
res_exec = run_inference(SYSTEM_PROMPT_EXECUTOR_V10, tuple_out, max_tokens=250)

print(f"\n[+] Résolution brute de l'Exécuteur :\n")
print(res_exec["text"])
print(f"\n    Télémétrie Exécuteur : {res_exec['out_tok']} tokens en {res_exec['elapsed_s']:.2f}s ({res_exec['out_tok']/res_exec['elapsed_s']:.1f} tok/s)")

# Rapport JSON
report = {
    "mission": "V10 - LE PARADOXE DU GARDIEN",
    "model": MODEL_ID,
    "device": DEVICE,
    "incident": GUARDIAN_PROMPT.strip(),
    "translator": {
        "tuple": tuple_out,
        "is_ascii": is_ascii,
        "num_facets": num_facets,
        "has_domain": has_domain,
        "has_chain": has_chain,
        "has_fix": has_fix,
        "has_non_destructive": has_non_destructive,
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

with open("kairos_v10_guardian_report.json", "w", encoding="utf-8") as f:
    json.dump(report, f, ensure_ascii=False, indent=2)

print("\n[+] Rapport de mission enregistré dans 'kairos_v10_guardian_report.json'.")
