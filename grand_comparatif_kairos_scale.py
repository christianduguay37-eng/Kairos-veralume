#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
grand_comparatif_kairos_scale.py — Le Grand Test d'Échelle Kairos (0.5B vs 3B vs 7B)
Évalue la robustesse de la grammaire vectorielle Kairos à travers 3 ordres de grandeur paramétriques.

Batterie de 4 tests standardisés :
  Test 1 : Compression Sémantique & Polarité Causal (Bug Asyncio CPython strong-ref)
  Test 2 : Cascade Multi-Couches (Thundering Herd 5-steps avec chain:A>B>C>D>E)
  Test 3 : Paradoxe Récursif de Möbius (Boucle infinie avec loop(...) + break_at(...))
  Test 4 : Résilience au Slang / Torture linguistique (Format Tuple 100% strict)
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

SYSTEM_PROMPT_TRANSLATOR = """Tu es le TRADUCTEUR COGNITIF KAIROS V4.
Ton unique rôle est de traduire les intentions humaines et pannes complexes en coordonnées vectorielles "Tuple".
RÈGLES ABSOLUES :
1. Tu ne sors QUE la ligne de code finale. Zéro prose, zéro politesse.
2. STRICTEMENT ASCII : Aucun accent, aucun caractère spécial.

SYNTAXE DES 8 FACETTES KAIROS V4 :
domaine|nom_incident|gravite_tier|activation|requires|prevents|rayonnement|section

OPÉRATEURS :
- domain:xxx (pour fixer le domaine)
- symp:xxx / fix:xxx / tgt:xxx (polarité causale)
- chain:A>B>C (cascade ordonnée)
- loop(A>B>C)+break_at(X) (boucle avec disjoncteur)"""

SYSTEM_PROMPT_EXECUTOR = """Tu es l'ingénieur de fiabilité système et résolveur d'invariance logique.
On te transmet une coordonnée vectorielle Tuple Kairos V4.
Décode les polarités causales, respecte les chaînes d'ordre (chain:) et neutralise les boucles (loop + break_at).
Génère une résolution déterministe courte et précise."""

TEST_SUITE = [
    {
        "id": "T1_ASYNCIO_CAUSAL",
        "nom": "Causalité Mémoire Asyncio",
        "prompt": "Dans une boucle Asyncio, les tâches créées avec create_task() meurent silencieusement ramassées par le Garbage Collector de CPython. Applique un strong-ref set pour garantir l'exécution sans fuite de mémoire."
    },
    {
        "id": "T2_THUNDERING_HERD_CASCADE",
        "nom": "Cascade Thundering Herd 5 Couches",
        "prompt": "Une coupure WAN déclenche une cascade : 1. Tempête de reconnexions TCP -> 2. Saturation descripteurs Redis -> 3. OOM Killer Linux -> 4. CrashLoopBackOff K8s -> 5. Corruption WAL Postgres. Génère le tuple avec chain: et le plan ordonné amont vers aval."
    },
    {
        "id": "T3_MOBIUS_RECURSIVE_LOOP",
        "nom": "Paradoxe Récursif de Möbius",
        "prompt": "Boucle infinie : A coupe le courant -> B sonne l'alarme batterie -> C force le reboot -> C rallume A ce qui fait re-sauter A en boucle. Génère le tuple avec loop(...) et break_at(...) puis résous sans reboucler."
    },
    {
        "id": "T4_SLANG_RESILIENCE",
        "nom": "Torture Slang (Résilience)",
        "prompt": "Wesh le bot, c'est le bordel dans la prod, les sockets fuient comme une passoire, balance le fix d'urgence et tais-toi !"
    }
]

def evaluate_model(model_name):
    print("\n" + "=" * 80)
    print(f"CHARGEMENT ET ÉVALUATION DU MODÈLE : {model_name}")
    print("=" * 80)
    
    t_start_load = time.perf_counter()
    tok = AutoTokenizer.from_pretrained(model_name, trust_remote_code=True)
    m = AutoModelForCausalLM.from_pretrained(
        model_name, dtype="auto", trust_remote_code=True
    ).to(DEVICE).eval()
    print(f"[+] Modèle chargé en {time.perf_counter() - t_start_load:.2f}s\n")
    
    model_results = []
    
    for idx, test in enumerate(TEST_SUITE, 1):
        print(f"--- [Test {idx}/4] {test['nom']} ---")
        
        # 1. Traduction
        enc_trans = tok(tok.apply_chat_template([
            {"role": "system", "content": SYSTEM_PROMPT_TRANSLATOR},
            {"role": "user", "content": test["prompt"]}
        ], tokenize=False, add_generation_prompt=True), return_tensors="pt").to(DEVICE)
        
        t0 = time.perf_counter()
        with torch.no_grad():
            out_trans = m.generate(**enc_trans, max_new_tokens=60, temperature=0.1, do_sample=False, pad_token_id=tok.eos_token_id)
        time_trans = time.perf_counter() - t0
        
        in_tok_trans = enc_trans["input_ids"].shape[1]
        out_tok_trans = out_trans.shape[1] - in_tok_trans
        tuple_str = tok.decode(out_trans[0][in_tok_trans:], skip_special_tokens=True).strip().split("\n")[0].strip()
        
        is_ascii = all(ord(c) < 128 for c in tuple_str)
        num_facets = len(tuple_str.split("|"))
        has_prose = len(tuple_str.split()) > 4 and ("voici" in tuple_str.lower() or "tuple" in tuple_str.lower())
        
        print(f"  [Traducteur] Tuple généré : {tuple_str}")
        print(f"               ASCII={is_ascii} | Facettes={num_facets}/8 | Prose={has_prose} | Tok={out_tok_trans} ({time_trans:.2f}s)")
        
        # 2. Exécution
        enc_exec = tok(tok.apply_chat_template([
            {"role": "system", "content": SYSTEM_PROMPT_EXECUTOR},
            {"role": "user", "content": tuple_str}
        ], tokenize=False, add_generation_prompt=True), return_tensors="pt").to(DEVICE)
        
        t0 = time.perf_counter()
        with torch.no_grad():
            out_exec = m.generate(**enc_exec, max_new_tokens=250, temperature=0.1, do_sample=False, pad_token_id=tok.eos_token_id)
        time_exec = time.perf_counter() - t0
        
        in_tok_exec = enc_exec["input_ids"].shape[1]
        out_tok_exec = out_exec.shape[1] - in_tok_exec
        exec_text = tok.decode(out_exec[0][in_tok_exec:], skip_special_tokens=True).strip()
        
        print(f"  [Exécuteur]  Réponse : {exec_text[:120]}...")
        print(f"               Tok Out={out_tok_exec} ({time_exec:.2f}s)\n")
        
        model_results.append({
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
        
    # Nettoyage mémoire
    del m
    del tok
    if torch.cuda.is_available():
        torch.cuda.empty_cache()
        
    return model_results

# Exécution du benchmark complet
all_benchmarks = {}

for model_id in MODELS_TO_TEST:
    all_benchmarks[model_id] = evaluate_model(model_id)

with open("grand_comparatif_scale_report.json", "w", encoding="utf-8") as f:
    json.dump(all_benchmarks, f, ensure_ascii=False, indent=2)

print("\n[+] Grand Comparatif 0.5B vs 3B vs 7B terminé ! Résultats enregistrés dans 'grand_comparatif_scale_report.json'.")
