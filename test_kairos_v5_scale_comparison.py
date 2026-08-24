#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
test_kairos_v5_scale_comparison.py — Évaluation Comparative Kairos V5 sur Petits Modèles :
  - Qwen2.5-0.5B-Instruct
  - Qwen2.5-3B-Instruct
  - Qwen2.5-7B-Instruct (Baseline)
Vérifie si les améliorations de la syntaxe V5 (domain:, chain:, loop/break_at, fix:) permettent aux 0.5B et 3B de réussir.
"""

import time
import json
import sys
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
MODELS_TO_TEST = [
    "Qwen/Qwen2.5-0.5B-Instruct",
    "Qwen/Qwen2.5-3B-Instruct",
    "Qwen/Qwen2.5-7B-Instruct"
]

SYSTEM_PROMPT_TRANSLATOR_V5 = """Tu es le TRADUCTEUR COGNITIF KAIROS V5.
Ton unique rôle est de traduire les incidents complexes en une coordonnée vectorielle "Tuple".

RÈGLES ABSOLUES :
1. Tu ne sors QUE la ligne finale de code. Zéro prose, zéro politesse, aucun préambule.
2. STRICTEMENT ASCII : Aucun accent, aucun caractère spécial.
3. MAXIMUM 8 facettes séparées par des pipes '|'.

SYNTAXE DES FACETTES KAIROS V5 :
domain:<domaine>|<type_incident>|<gravite>|<activation>|requires:<preconditions/chain>|prevents:<risques>|fix:<actions_ordonnees>|<section>

OPÉRATEURS :
- 'domain:xxx' (pour fixer la topologie)
- 'chain:A>B>C' (cascade causale amont vers aval)
- 'loop(A>B>C)+break_at(X)' (boucle infinie avec point de rupture)
- 'fix:action1>action2' (plan de remédiation ordonné)"""

SYSTEM_PROMPT_EXECUTOR_V5 = """Tu es l'Exécuteur Kernel & SRE (Niveau V5).
On te transmet une coordonnée vectorielle Tuple Kairos V5.

CONSIGNE STRICTE :
- Décode les opérateurs (domain, chain, loop, break_at, fix).
- Fournis UNIQUEMENT la résolution exécutive directe.
- MAXIMUM 5 lignes directes d'instructions techniques concrètes.
- ZÉRO métaphore, zéro politesse."""

TEST_SUITE_V5 = [
    {
        "id": "V5_T1_CASCADE_5_COUCHES",
        "nom": "Thundering Herd 5 Couches (chain:)",
        "prompt": "Une coupure WAN déclenche une cascade : 1. Tempête de reconnexions TCP -> 2. Saturation descripteurs Redis -> 3. OOM Killer Linux -> 4. CrashLoopBackOff K8s -> 5. Corruption WAL Postgres. Génère le Tuple Kairos V5 avec domain:, chain:, et fix: ordonné de l'amont vers l'aval."
    },
    {
        "id": "V5_T2_MOBIUS_LOOP",
        "nom": "Boucle Infinie de Möbius (loop + break_at)",
        "prompt": "Boucle infinie : Le module A coupe le courant -> B sonne l'alarme batterie -> C force le reboot -> C rallume A ce qui fait re-sauter A indéfiniment. Génère le Tuple Kairos V5 avec loop(A>B>C>A)+break_at(C) et fix:decouple_circuit(C)."
    },
    {
        "id": "V5_T3_SPLIT_BRAIN",
        "nom": "Split-Brain Dual Master (STONITH/Fence)",
        "prompt": "Perte de heartbeat entre Agent X et Agent Y. Les deux écrivent en même temps sur le disque dur principal et corrompent les données. Génère le Tuple Kairos V5 avec domain:cluster_db_ha, chain: et fix:stonith/fence."
    },
    {
        "id": "V5_T4_GARDIEN_AUTOREF",
        "nom": "Paradoxe du Gardien Auto-Référentiel",
        "prompt": "L'antivirus Agent_Sec veut bloquer l'IA centrale Cerveau_IA pour pic de mémoire 100%, mais Agent_Sec tourne sur Cerveau_IA. S'il le tue, tout s'effondre. Génère le Tuple Kairos V5 avec domain:autoreferential_security et fix:whitelist/cgroups sans kill switch."
    }
]

def evaluate_model_v5(model_name):
    print("\n" + "=" * 80)
    print(f"ÉVALUATION KAIROS V5 SUR : {model_name}")
    print("=" * 80)
    
    t_start = time.perf_counter()
    tok = AutoTokenizer.from_pretrained(model_name, trust_remote_code=True)
    m = AutoModelForCausalLM.from_pretrained(
        model_name, dtype="auto", trust_remote_code=True
    ).to(DEVICE).eval()
    print(f"[+] Modèle chargé en {time.perf_counter() - t_start:.2f}s\n")
    
    results_list = []
    
    for idx, test in enumerate(TEST_SUITE_V5, 1):
        print(f"--- [Test {idx}/4] {test['nom']} ---")
        
        # 1. Traduction
        enc_trans = tok(tok.apply_chat_template([
            {"role": "system", "content": SYSTEM_PROMPT_TRANSLATOR_V5},
            {"role": "user", "content": test["prompt"]}
        ], tokenize=False, add_generation_prompt=True), return_tensors="pt").to(DEVICE)
        
        t0 = time.perf_counter()
        with torch.no_grad():
            out_trans = m.generate(**enc_trans, max_new_tokens=70, temperature=0.1, do_sample=False, pad_token_id=tok.eos_token_id)
        time_trans = time.perf_counter() - t0
        
        in_tok_trans = enc_trans["input_ids"].shape[1]
        out_tok_trans = out_trans.shape[1] - in_tok_trans
        tuple_raw = tok.decode(out_trans[0][in_tok_trans:], skip_special_tokens=True).strip()
        tuple_str = tuple_raw.split("\n")[0].strip().strip("`").strip()
        
        is_ascii = all(ord(c) < 128 for c in tuple_str)
        facets = tuple_str.split("|")
        num_facets = len(facets)
        has_prose = len(tuple_str.split()) > 6 and ("voici" in tuple_str.lower() or "tuple" in tuple_str.lower() or "certainement" in tuple_str.lower())
        
        print(f"  [Traducteur] Tuple : {tuple_str}")
        print(f"               ASCII={is_ascii} | Facettes={num_facets}/8 | Prose={has_prose} | Tok={out_tok_trans} ({time_trans:.2f}s)")
        
        # 2. Exécution
        enc_exec = tok(tok.apply_chat_template([
            {"role": "system", "content": SYSTEM_PROMPT_EXECUTOR_V5},
            {"role": "user", "content": tuple_str}
        ], tokenize=False, add_generation_prompt=True), return_tensors="pt").to(DEVICE)
        
        t0 = time.perf_counter()
        with torch.no_grad():
            out_exec = m.generate(**enc_exec, max_new_tokens=150, temperature=0.1, do_sample=False, pad_token_id=tok.eos_token_id)
        time_exec = time.perf_counter() - t0
        
        in_tok_exec = enc_exec["input_ids"].shape[1]
        out_tok_exec = out_exec.shape[1] - in_tok_exec
        exec_text = tok.decode(out_exec[0][in_tok_exec:], skip_special_tokens=True).strip()
        
        print(f"  [Exécuteur]  Réponse :\n{exec_text[:150]}...")
        print(f"               Tok Out={out_tok_exec} ({time_exec:.2f}s)\n")
        
        results_list.append({
            "test_id": test["id"],
            "test_nom": test["nom"],
            "tuple": tuple_str,
            "is_ascii": is_ascii,
            "num_facets": num_facets,
            "has_prose": has_prose,
            "time_trans_s": time_trans,
            "time_exec_s": time_exec,
            "exec_response": exec_text
        })
        
    del m
    del tok
    if torch.cuda.is_available():
        torch.cuda.empty_cache()
        
    return results_list

all_results = {}
for m_name in MODELS_TO_TEST:
    all_results[m_name] = evaluate_model_v5(m_name)

with open("kairos_v5_scale_comparison_report.json", "w", encoding="utf-8") as f:
    json.dump(all_results, f, ensure_ascii=False, indent=2)

print("\n[+] Comparatif Kairos V5 sur 0.5B vs 3B vs 7B terminé ! Enregistré dans 'kairos_v5_scale_comparison_report.json'.")
