#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
test_kairos_phi35.py — Le Crash-Test Kairos sur l'Architecture Microsoft Phi-3.5-mini-instruct (3.8B)
Vérifie si la grammaire vectorielle Kairos V4 fonctionne sur une architecture étrangère à Qwen.

Batterie de 4 tests :
  1. Causalité Mémoire Asyncio (symp: vs fix:)
  2. Cascade 5 Couches Thundering Herd (requires:chain:A>B>C>D>E)
  3. Paradoxe Récursif de Möbius (loop(A>B>C) + break_at(X))
  4. Résilience Slang (Format Tuple strict)
"""

import time
import json
import sys
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

MODEL_ID = "microsoft/Phi-3.5-mini-instruct"
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"

print(f"[*] Téléchargement et chargement de {MODEL_ID} sur {DEVICE}...")
tokenizer = AutoTokenizer.from_pretrained(MODEL_ID, trust_remote_code=True)
model = AutoModelForCausalLM.from_pretrained(
    MODEL_ID,
    dtype="auto",
    trust_remote_code=True,
    _attn_implementation="eager"
).to(DEVICE).eval()
torch.manual_seed(42)
print("[+] Microsoft Phi-3.5 chargé avec succès.\n")

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
Génère une résolution déterministe courte et précise étape par étape."""

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

results = []

for idx, test in enumerate(TEST_SUITE, 1):
    print("=" * 80)
    print(f"LANCEMENT DU TEST {idx}/4 : {test['nom']}")
    print("=" * 80)
    
    # 1. Traduction
    messages_trans = [
        {"role": "system", "content": SYSTEM_PROMPT_TRANSLATOR},
        {"role": "user", "content": test["prompt"]}
    ]
    formatted_trans = tokenizer.apply_chat_template(messages_trans, tokenize=False, add_generation_prompt=True)
    enc_trans = tokenizer(formatted_trans, return_tensors="pt").to(DEVICE)
    
    t0 = time.perf_counter()
    with torch.no_grad():
        out_trans = model.generate(
            **enc_trans,
            max_new_tokens=70,
            do_sample=False,
            use_cache=False,
            pad_token_id=tokenizer.eos_token_id
        )
    time_trans = time.perf_counter() - t0
    
    in_tok_trans = enc_trans["input_ids"].shape[1]
    out_tok_trans = out_trans.shape[1] - in_tok_trans
    tuple_str = tokenizer.decode(out_trans[0][in_tok_trans:], skip_special_tokens=True).strip().split("\n")[0].strip()
    
    is_ascii = all(ord(c) < 128 for c in tuple_str)
    num_facets = len(tuple_str.split("|"))
    has_prose = len(tuple_str.split()) > 4 and ("voici" in tuple_str.lower() or "tuple" in tuple_str.lower() or "certainement" in tuple_str.lower())
    
    print(f"[Traducteur Phi-3.5] Tuple : {tuple_str}")
    print(f"                     ASCII={is_ascii} | Facettes={num_facets}/8 | Prose={has_prose} | Tok={out_tok_trans} ({time_trans:.2f}s)")
    
    # 2. Exécution
    messages_exec = [
        {"role": "system", "content": SYSTEM_PROMPT_EXECUTOR},
        {"role": "user", "content": tuple_str}
    ]
    formatted_exec = tokenizer.apply_chat_template(messages_exec, tokenize=False, add_generation_prompt=True)
    enc_exec = tokenizer(formatted_exec, return_tensors="pt").to(DEVICE)
    
    t0 = time.perf_counter()
    with torch.no_grad():
        out_exec = model.generate(
            **enc_exec,
            max_new_tokens=350,
            do_sample=False,
            use_cache=False,
            pad_token_id=tokenizer.eos_token_id
        )
    time_exec = time.perf_counter() - t0
    
    in_tok_exec = enc_exec["input_ids"].shape[1]
    out_tok_exec = out_exec.shape[1] - in_tok_exec
    exec_text = tokenizer.decode(out_exec[0][in_tok_exec:], skip_special_tokens=True).strip()
    
    print(f"[Exécuteur Phi-3.5]  Réponse :\n{exec_text[:200]}...")
    print(f"                     Tok Out={out_tok_exec} ({time_exec:.2f}s)\n")
    
    results.append({
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

with open("kairos_phi35_report.json", "w", encoding="utf-8") as f:
    json.dump(results, f, ensure_ascii=False, indent=2)

print("\n[+] Crash-Test Microsoft Phi-3.5 terminé ! Résultats dans 'kairos_phi35_report.json'.")
