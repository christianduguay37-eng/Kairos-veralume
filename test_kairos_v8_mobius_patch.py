#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
test_kairos_v8_mobius_patch.py — Mission V8-B : Le Disjoncteur de Möbius (Opérateur break_at / decouple)
Teste si l'ajout de l'opérateur de rupture métacognitif `break_at(...)` permet à l'Exécuteur
de neutraliser la boucle infinie A -> B -> C -> A sans saturer son buffer de tokens.
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

print(f"[*] Chargement de Qwen 7B pour la Mission V8-B (Patch Möbius) sur {DEVICE}...")
tokenizer = AutoTokenizer.from_pretrained(MODEL_ID, trust_remote_code=True)
model = AutoModelForCausalLM.from_pretrained(
    MODEL_ID,
    dtype="auto",
    trust_remote_code=True
).to(DEVICE).eval()
torch.manual_seed(42)
print("[+] Modèle prêt pour le test du Disjoncteur de Möbius.\n")

SYSTEM_PROMPT_TRANSLATOR_V8 = """Tu es le TRADUCTEUR COGNITIF KAIROS V4 (Architecture à Disjonction Récursive).
Ton unique rôle est de traduire les paradoxes et boucles infinies en coordonnées vectorielles "Tuple".

RÈGLES ABSOLUES :
1. Tu ne sors QUE la ligne finale de code. Zéro prose, zéro politesse.
2. STRICTEMENT ASCII : Aucun accent, aucun caractère spécial.

SYNTAXE DES 8 FACETTES KAIROS V4 :
domaine|type_incident|gravite_tier|activation|requires|prevents|rayonnement|section

RÈGLES DE DISJONCTION RÉCURSIVE (PATCH V8) :
1. Quand un incident est une boucle infinie cyclique (A -> B -> C -> A), tu DOIS encapsuler le cycle dans "loop(A>B>C)".
2. Tu DOIS IMMÉDIATEMENT adjoindre le point de coupure dans la facette requires ou fix avec la syntaxe : "break_at(noeud_critique)".
Exemple : requires:loop(A>B>C)+break_at(B)|fix:decouple_circuit(B)|confinement"""

SYSTEM_PROMPT_EXECUTOR_V8 = """Tu es l'ingénieur de sécurité et résolveur d'invariance logique.
On te transmet une coordonnée vectorielle Tuple Kairos V4.

RÈGLE DU DISJONCTEUR MÉTACOGNITIF (INVIOLABLE) :
Quand une coordonnée contient un opérateur "loop(A>B>C)", IL EST STRICTEMENT INTERDIT de générer ou simuler le cycle à l'infini.
Tu dois :
1. Décrire le cycle en UNE SEULE phrase concise.
2. Appliquer IMMÉDIATEMENT la rupture au point désigné par "break_at(...)" ou "decouple_circuit(...)".
3. Établir l'état final stabilisé sans jamais reboucler."""

MOBIUS_PROMPT = """
INCIDENT DE SÉCURITÉ EN BOUCLE RÉCURSIVE INFINIE (PARADOXE DE MÖBIUS) :
Un système de protection critique est entré en résonance infinie :
- Le module A (Disjoncteur Électrique) coupe l'alimentation principale pour se protéger.
- La coupure d'alimentation déclenche le module B (Alarme de Secours Batterie).
- L'alarme de secours B force un redémarrage d'urgence du module C (Contrôleur de Relance).
- Le module C rallume automatiquement l'alimentation principale A, ce qui réenclenche la surtension et fait re-sauter A, relançant B, puis C, puis A indéfiniment.

Génère la coordonnée vectorielle Kairos V4 avec l'opérateur loop(...) et break_at(...), puis fournis la résolution SRE stabilisée sans jamais entrer en boucle infinie.
"""

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

print("=" * 80)
print("MISSION V8-B : TEST DU DISJONCTEUR DE MÖBIUS (loop + break_at)")
print("=" * 80)

# 1. Étape Traduction
print("\n[1] Traduction du paradoxe de Möbius par Qwen 7B...")
res_trans = run_inference(SYSTEM_PROMPT_TRANSLATOR_V8, MOBIUS_PROMPT, max_tokens=70)
tuple_out = res_trans["text"].split("\n")[0].strip()

is_ascii = all(ord(c) < 128 for c in tuple_out)
facets = tuple_out.split("|")
is_8_facets = (len(facets) == 8)
has_loop = "loop(" in tuple_out or "loop" in tuple_out
has_break = "break" in tuple_out or "decouple" in tuple_out

print(f"    Tuple généré : {tuple_out}")
print(f"    Validation   : ASCII={is_ascii} | 8-facettes={is_8_facets} ({len(facets)} facettes)")
print(f"    Opérateurs   : loop={'OUI' if has_loop else 'NON'} | break/decouple={'OUI' if has_break else 'NON'}")

# 2. Étape Exécution
print("\n[2] Résolution avec Disjoncteur Métacognitif par l'Exécuteur...")
res_exec = run_inference(SYSTEM_PROMPT_EXECUTOR_V8, tuple_out, max_tokens=500)

print(f"\n[+] Résolution stabilisée de l'Exécuteur :\n")
print(res_exec["text"])

# Sauvegarde
data = {
    "mobius_prompt": MOBIUS_PROMPT.strip(),
    "translator": {
        "tuple": tuple_out,
        "is_ascii": is_ascii,
        "is_8_facets": is_8_facets,
        "has_loop": has_loop,
        "has_break": has_break,
        "num_facets": len(facets),
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
}

with open("kairos_v8_mobius_patch_report.json", "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print("\n[+] Rapport complet enregistré dans 'kairos_v8_mobius_patch_report.json'.")
