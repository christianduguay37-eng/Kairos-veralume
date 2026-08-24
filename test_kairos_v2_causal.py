#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
test_kairos_v2_causal.py — Évaluation de la Phase 3 : Injection du Vecteur Causal (Kairos V2)
Teste :
  1. Traduction de la requête Asyncio complexe vers Tuple V2 (avec préfixes symp:/fix:/tgt: et 100% ASCII).
  2. Injection du Tuple V2 dans un agent d'exécution pour vérifier si l'ambiguïté causale est totalement levée.
"""

import time
import json
import re
import sys
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

MODEL_ID = "Qwen/Qwen2.5-7B-Instruct"
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"

print(f"[*] Chargement du modèle de test : {MODEL_ID} sur {DEVICE}...")
tokenizer = AutoTokenizer.from_pretrained(MODEL_ID, trust_remote_code=True)
model = AutoModelForCausalLM.from_pretrained(
    MODEL_ID,
    dtype="auto",
    trust_remote_code=True
).to(DEVICE).eval()
torch.manual_seed(42)
print("[+] Modèle prêt pour la Phase 3 (Vecteur Causal V2).\n")

SYSTEM_PROMPT_KAIROS_V2 = """Tu es le TRADUCTEUR COGNITIF KAIROS V2.
Ton unique rôle est de traduire les intentions humaines verbeuses en coordonnées vectorielles pures appelées "Tuple". 
RÈGLES ABSOLUES :
1. Tu ne sors QUE la ligne de code finale. Zéro prose, zéro politesse.
2. STRICTEMENT ASCII : Aucun accent, aucun caractère spécial. "sécurité" devient "securite".

La syntaxe stricte (8 facettes) :
nom|couche|tier|activation|requires|prevents|rayonnement|section

NOUVELLE RÈGLE CAUSALE (V2) :
Dans le champ "nom" ou "requires", tu DOIS utiliser des préfixes pour définir la direction de l'action :
- symp: (Le symptôme, le bug, le problème)
- fix: (La solution curative, le remède)
- tgt: (La cible de l'analyse)

Exemple 1 (Causalité) :
Humain : "Le garbage collector détruit les tâches sans log. Applique un set de références fortes pour boucher la fuite."
Toi : symp:gc-task-loss+fix:strong-ref-set|methode|2|immediate|1|0|8|12

Exemple 2 (Audit) :
Humain : "Passe ça au peigne fin pour la sécurité."
Toi : tgt:securite-scan|audit|1|always|1|0|10|0"""

PROMPT_ASYNCIO_HUMAIN = """
Dans une architecture de microservices Python sous Asyncio, nous observons un comportement erratique critique :
Certaines tâches de fond créées avec `asyncio.create_task()` dans une boucle d'événements à haut débit disparaissent silencieusement sans jamais lever d'exception ni terminer, provoquant des fuites de sockets et une corruption d'état intermittent. 
Analyse la cause racine profonde liée au Garbage Collector de CPython et à la conservation des références d'objets Task, explique pourquoi `await` n'est pas appelé immédiatement, et fournis la solution architecturale canonique pour garantir l'exécution sans fuite avec un set de références fortes.
"""

def generate_text(messages, max_new_tokens=400, temperature=0.1):
    formatted = tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
    inputs = tokenizer(formatted, return_tensors="pt").to(DEVICE)
    in_tok = inputs["input_ids"].shape[1]
    
    t0 = time.perf_counter()
    with torch.no_grad():
        outputs = model.generate(
            **inputs,
            max_new_tokens=max_new_tokens,
            temperature=temperature,
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

# ==============================================================================
# ÉTAPE 1 : TRADUCTION DE LA PROSE VERS LE TUPLE V2 AVEC DIRECTION CAUSALE
# ==============================================================================
print("=" * 80)
print("ÉTAPE 1 : TEST DE TRADUCTION CAUSALE PAR QWEN 7B (KAIROS V2)")
print("=" * 80)

res_translation = generate_text([
    {"role": "system", "content": SYSTEM_PROMPT_KAIROS_V2},
    {"role": "user", "content": PROMPT_ASYNCIO_HUMAIN}
], max_new_tokens=60)

raw_tuple_out = res_translation["text"].split("\n")[0].strip()
print(f"\n[>] Requête humaine reçue (195 tokens)")
print(f"[+] Tuple généré par Qwen 7B : {raw_tuple_out}")
print(f"    - Tokens générés : {res_translation['out_tok']}")
print(f"    - Temps : {res_translation['elapsed_s']:.2f}s")

# Vérifications de conformité
is_ascii = all(ord(c) < 128 for c in raw_tuple_out)
has_symp = "symp:" in raw_tuple_out
has_fix = "fix:" in raw_tuple_out
has_pipe_facets = len(raw_tuple_out.split("|")) == 8

print(f"\n[+] Télémétrie de conformité V2 :")
print(f"    - Strictement ASCII (0 accent)       : {'OUI' if is_ascii else 'NON'}")
print(f"    - Préfixe causal 'symp:' détecté     : {'OUI' if has_symp else 'NON'}")
print(f"    - Préfixe causal 'fix:' détecté      : {'OUI' if has_fix else 'NON'}")
print(f"    - 8 facettes canoniques respectées   : {'OUI' if has_pipe_facets else 'NON'}")

# ==============================================================================
# ÉTAPE 2 : TEST D'INTERPRÉTATION DU TUPLE CAUSAL PAR LE MOTEUR D'EXÉCUTION
# ==============================================================================
print("\n" + "=" * 80)
print("ÉTAPE 2 : VÉRIFICATION DE LA COMPRÉHENSION CAUSALE (SYMP VS FIX)")
print("=" * 80)

SYSTEM_PROMPT_EXEC = "Tu es un architecte logiciel système CPython. Analyse le tuple d'instructions reçu, identifie formellement le symptôme vs la solution, et génère l'implémentation technique."

res_execution = generate_text([
    {"role": "system", "content": SYSTEM_PROMPT_EXEC},
    {"role": "user", "content": raw_tuple_out}
], max_new_tokens=450)

print(f"\n[+] Analyse et résolution générées par le modèle à partir du tuple V2 :\n")
print(res_execution["text"])

# Sauvegarde du rapport Phase 3
report_p3 = {
    "translation": {
        "prompt_humain": PROMPT_ASYNCIO_HUMAIN.strip(),
        "generated_tuple": raw_tuple_out,
        "is_ascii": is_ascii,
        "has_symp": has_symp,
        "has_fix": has_fix,
        "has_8_facets": has_pipe_facets,
        "in_tok": res_translation["in_tok"],
        "out_tok": res_translation["out_tok"],
        "elapsed_s": res_translation["elapsed_s"]
    },
    "interpretation": {
        "tuple_input": raw_tuple_out,
        "in_tok": res_execution["in_tok"],
        "out_tok": res_execution["out_tok"],
        "elapsed_s": res_execution["elapsed_s"],
        "response_text": res_execution["text"]
    }
}

with open("kairos_v2_causal_report.json", "w", encoding="utf-8") as f:
    json.dump(report_p3, f, ensure_ascii=False, indent=2)

print("\n[+] Rapport Phase 3 sauvegardé dans 'kairos_v2_causal_report.json'")
