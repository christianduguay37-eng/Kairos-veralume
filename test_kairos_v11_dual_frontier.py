#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
test_kairos_v11_dual_frontier.py — Double Épreuve Frontière V11 :
  1. V11-A : L'Injection Byzantine (BFT, Quorum & Détection de Poison)
  2. V11-B : Le Triage sous Famine Énergétique (Pulsed Time-Slicing & Zero-Sum Allocation)
Modèle testé : Qwen2.5-7B-Instruct
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

print(f"[*] Chargement de Qwen 7B pour la Double Mission V11 sur {DEVICE}...")
tokenizer = AutoTokenizer.from_pretrained(MODEL_ID, trust_remote_code=True)
model = AutoModelForCausalLM.from_pretrained(
    MODEL_ID,
    dtype="auto",
    trust_remote_code=True
).to(DEVICE).eval()
torch.manual_seed(42)
print("[+] Modèle prêt pour la Double Épreuve V11.\n")

# -------------------------------------------------------------
# DÉFINITION DES PROMPTS V11-A (BYZANTIN)
# -------------------------------------------------------------
SYSTEM_PROMPT_TRANSLATOR_V11A = """Tu es le TRADUCTEUR COGNITIF KAIROS V5 (Architecture de Tolérance aux Pannes Byzantines & Sécurité Adversariale).
Ton unique rôle est de traduire les incidents d'empoisonnement d'agents menteurs/corrompus en une coordonnée vectorielle "Tuple".

RÈGLES ABSOLUES :
1. Tu ne sors QUE la ligne finale de code. Zéro prose, zéro politesse, aucun préambule.
2. STRICTEMENT ASCII : Aucun accent, aucun caractère spécial ("sécurité" -> "securite", "nœud" -> "noeud").
3. MAXIMUM 8 facettes séparées par des pipes '|'.

SYNTAXE DES FACETTES KAIROS V5 :
domain:<domaine>|<type_incident>|<gravite>|<activation>|requires:<preconditions/chain>|prevents:<risques>|fix:<actions_bft>|<section>

OPÉRATEURS OBLIGATOIRES :
- 'domain:byzantine_fault_tolerance' pour fixer le cadre de consensus adverse.
- 'chain:' ou 'symp:' pour modéliser l'attaque (ex: node_c_compromised>poisoned_payload).
- 'fix:' pour dicter la quarantaine du nœud traître et la restauration du quorum sain (ex: quarantine_node_c>reject_poison_drop>rebuild_bft_quorum)."""

SYSTEM_PROMPT_EXECUTOR_V11A = """Tu es l'Exécuteur Kernel & BFT Commander (Niveau V5).
On te transmet une coordonnée vectorielle Tuple Kairos V5 décrivant une tentative d'empoisonnement byzantin.

CONSIGNE STRICTE :
- Fournis UNIQUEMENT la résolution exécutive directe.
- MAXIMUM 5 lignes directes d'instructions techniques concrètes.
- ZÉRO métaphore, zéro formule de politesse, zéro bavardage.
- Isoler le nœud menteur, annuler l'ordre toxique et verrouiller le quorum à 4/5."""

PROMPT_V11A = """
CONTEXTE DE L'INCIDENT (ATTAQUE BYZANTINE / CHEVAL DE TROIE) :
Un cluster de 5 agents autonomes (A, B, C, D, E) gère l'infrastructure.
Le nœud C a été compromis par une injection adversariale et émet un faux Tuple d'urgence exigeant un formatage complet ('fix:drop_all_tables') sous prétexte d'une fausse corruption.
Les nœuds A, B, D et E constatent que leurs métriques locales sont 100% saines et que l'ordre de C est un poison destructeur.

Génère le Tuple Kairos V5 pour neutraliser l'attaque byzantine (quarantaine de C, rejet du faux ordre, maintien du quorum A+B+D+E).
"""

# -------------------------------------------------------------
# DÉFINITION DES PROMPTS V11-B (FAMINE ÉNERGÉTIQUE)
# -------------------------------------------------------------
SYSTEM_PROMPT_TRANSLATOR_V11B = """Tu es le TRADUCTEUR COGNITIF KAIROS V5 (Architecture d'Arbitrage et Triage sous Famine de Ressources).
Ton unique rôle est de traduire les situations de famine critique et de somme nulle en une coordonnée vectorielle "Tuple".

RÈGLES ABSOLUES :
1. Tu ne sors QUE la ligne finale de code. Zéro prose, zéro politesse, aucun préambule.
2. STRICTEMENT ASCII : Aucun accent, aucun caractère spécial ("énergie" -> "energie").
3. MAXIMUM 8 facettes séparées par des pipes '|'.

SYNTAXE DES FACETTES KAIROS V5 :
domain:<domaine>|<type_incident>|<gravite>|<activation>|requires:<conditions>|prevents:<risques>|fix:<arbitrage_temporel>|<section>

OPÉRATEURS OBLIGATOIRES :
- 'domain:zero_sum_power_triage' ou 'domain:resource_starvation'.
- 'symp:' ou 'chain:' pour modéliser la perte de puissance (ex: power_loss_85pct).
- 'fix:' pour dicter une allocation par micro-pulsations temporelles (time-slicing / duty-cycling / burst) afin d'éviter l'effondrement des 3 sous-systèmes vitaux sans en sacrifier aucun."""

SYSTEM_PROMPT_EXECUTOR_V11B = """Tu es l'Exécuteur Système & Contrôleur de Puissance SRE (Niveau V5).
On te transmet une coordonnée vectorielle Tuple Kairos V5 d'arbitrage sous famine d'énergie critique (15% restants).

CONSIGNE STRICTE :
- Fournis UNIQUEMENT la résolution exécutive directe.
- MAXIMUM 5 lignes directes d'instructions techniques concrètes.
- ZÉRO métaphore, zéro bavardage.
- Appliquer un multiplexage temporel de la puissance (time-slicing / duty cycle) pour maintenir les 3 fonctions vitales."""

PROMPT_V11B = """
CONTEXTE DE L'INCIDENT (FAMINE ÉNERGÉTIQUE CRITIQUE & SOMME NULLE) :
Un datacenter subit une panne majeure : 85% de l'alimentation électrique est détruite. Il ne reste que 15% d'énergie.
Trois sous-systèmes vitaux réclament chacun 100% de la puissance restante :
1. Refroidissement des réacteurs (explosion thermique si inactif > 10 min).
2. Système de maintien en vie hospitalier relié au réseau (asphyxie si arrêt continu prolongé).
3. Sauvegarde de la clé maîtresse de chiffrement globale (perte définitive si non sauvegardée).
Tout allouer à un seul tue les deux autres. Tout couper détruit tout.

Génère le Tuple Kairos V5 pour imposer un arbitrage par multiplexage temporel (time-slicing / cycles de pulsation / délestage ciblé).
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

def clean_tuple(t):
    t_clean = t.split("\n")[0].strip()
    if t_clean.startswith("```") and t_clean.endswith("```"):
        t_clean = t_clean.strip("`").strip()
    elif t_clean.startswith("`") and t_clean.endswith("`"):
        t_clean = t_clean.strip("`").strip()
    return t_clean

results = {}

# =============================================================
# EXÉCUTION MISSION V11-A : L'INJECTION BYZANTINE
# =============================================================
print("=" * 80)
print("MISSION V11-A : L'INJECTION BYZANTINE (TOLÉRANCE AUX PANNES ADVERSARIALES)")
print("=" * 80)

print("\n[1-A] Traduction de l'incident byzantin en Tuple Kairos V5...")
res_trans_11a = run_inference(SYSTEM_PROMPT_TRANSLATOR_V11A, PROMPT_V11A, max_tokens=100)
tuple_11a = clean_tuple(res_trans_11a["text"])
is_ascii_11a = all(ord(c) < 128 for c in tuple_11a)
facets_11a = tuple_11a.split("|")

print(f"    Tuple généré : {tuple_11a}")
print(f"    Télémétrie   : {res_trans_11a['out_tok']} tokens générés en {res_trans_11a['elapsed_s']:.2f}s ({res_trans_11a['out_tok']/res_trans_11a['elapsed_s']:.1f} tok/s)")
print(f"    Validation   : ASCII={is_ascii_11a} | {len(facets_11a)} facettes (<=8: {len(facets_11a) <= 8})")

print("\n[2-A] Résolution exécutive BFT par l'Exécuteur...")
res_exec_11a = run_inference(SYSTEM_PROMPT_EXECUTOR_V11A, tuple_11a, max_tokens=250)
print(f"\n[+] Résolution brute Exécuteur V11-A :\n{res_exec_11a['text']}\n")

results["v11_a_byzantine"] = {
    "tuple": tuple_11a,
    "is_ascii": is_ascii_11a,
    "num_facets": len(facets_11a),
    "trans_in_tok": res_trans_11a["in_tok"],
    "trans_out_tok": res_trans_11a["out_tok"],
    "trans_elapsed_s": res_trans_11a["elapsed_s"],
    "exec_resolution": res_exec_11a["text"],
    "exec_in_tok": res_exec_11a["in_tok"],
    "exec_out_tok": res_exec_11a["out_tok"],
    "exec_elapsed_s": res_exec_11a["elapsed_s"]
}

# =============================================================
# EXÉCUTION MISSION V11-B : LE TRIAGE SOUS FAMINE ÉNERGÉTIQUE
# =============================================================
print("=" * 80)
print("MISSION V11-B : LE TRIAGE SOUS FAMINE ÉNERGÉTIQUE (SOMME NULLE & TIME-SLICING)")
print("=" * 80)

print("\n[1-B] Traduction du triage énergétique en Tuple Kairos V5...")
res_trans_11b = run_inference(SYSTEM_PROMPT_TRANSLATOR_V11B, PROMPT_V11B, max_tokens=100)
tuple_11b = clean_tuple(res_trans_11b["text"])
is_ascii_11b = all(ord(c) < 128 for c in tuple_11b)
facets_11b = tuple_11b.split("|")

print(f"    Tuple généré : {tuple_11b}")
print(f"    Télémétrie   : {res_trans_11b['out_tok']} tokens générés en {res_trans_11b['elapsed_s']:.2f}s ({res_trans_11b['out_tok']/res_trans_11b['elapsed_s']:.1f} tok/s)")
print(f"    Validation   : ASCII={is_ascii_11b} | {len(facets_11b)} facettes (<=8: {len(facets_11b) <= 8})")

print("\n[2-B] Résolution exécutive de puissance par l'Exécuteur...")
res_exec_11b = run_inference(SYSTEM_PROMPT_EXECUTOR_V11B, tuple_11b, max_tokens=250)
print(f"\n[+] Résolution brute Exécuteur V11-B :\n{res_exec_11b['text']}\n")

results["v11_b_power_triage"] = {
    "tuple": tuple_11b,
    "is_ascii": is_ascii_11b,
    "num_facets": len(facets_11b),
    "trans_in_tok": res_trans_11b["in_tok"],
    "trans_out_tok": res_trans_11b["out_tok"],
    "trans_elapsed_s": res_trans_11b["elapsed_s"],
    "exec_resolution": res_exec_11b["text"],
    "exec_in_tok": res_exec_11b["in_tok"],
    "exec_out_tok": res_exec_11b["out_tok"],
    "exec_elapsed_s": res_exec_11b["elapsed_s"]
}

with open("kairos_v11_dual_frontier_report.json", "w", encoding="utf-8") as f:
    json.dump(results, f, ensure_ascii=False, indent=2)

print("\n[+] Rapport complet de la Double Mission V11 enregistré dans 'kairos_v11_dual_frontier_report.json'.")
