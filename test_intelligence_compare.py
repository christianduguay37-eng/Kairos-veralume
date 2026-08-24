#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
test_intelligence_compare.py — Test qualitatif et comparatif :
Scénario A (Prose complète) vs Scénario B (Tuple Kairos) -> Réponse analytique de Qwen 7B
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

print(f"[*] Chargement du modèle {MODEL_ID}...")
tokenizer = AutoTokenizer.from_pretrained(MODEL_ID, trust_remote_code=True)
model = AutoModelForCausalLM.from_pretrained(
    MODEL_ID,
    dtype="auto",
    trust_remote_code=True
).to(DEVICE).eval()
torch.manual_seed(42)

# Problème complexe : Bug subtil d'asynchronisme + race condition + fuite mémoire en Python/Asyncio
PROMPT_PROSE = """
Dans une architecture de microservices Python sous Asyncio, nous observons un comportement erratique critique :
Certaines tâches de fond créées avec `asyncio.create_task()` dans une boucle d'événements à haut débit disparaissent silencieusement sans jamais lever d'exception ni terminer, provoquant des fuites de sockets et une corruption d'état intermittent. 
Analyse la cause racine profonde liée au Garbage Collector de CPython et à la conservation des références d'objets Task, explique pourquoi `await` n'est pas appelé immédiatement, et fournis la solution architecturale canonique pour garantir l'exécution sans fuite.
"""

TUPLE_PROMPT = "asyncio-cpython|gc-task-loss-root-cause-fix|3|always|strong-ref-set|silent-task-death|8|12"

SYSTEM_PROMPT = "Tu es un architecte logiciel expert en système CPython et concurrence distribuée. Sois précis, technique et exhaustif."

def exec_run(user_content, max_tokens=600):
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": user_content}
    ]
    formatted = tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
    inputs = tokenizer(formatted, return_tensors="pt").to(DEVICE)
    in_tok = inputs["input_ids"].shape[1]
    
    t0 = time.perf_counter()
    with torch.no_grad():
        outputs = model.generate(
            **inputs,
            max_new_tokens=max_tokens,
            temperature=0.2,
            do_sample=True,
            top_p=0.9,
            pad_token_id=tokenizer.eos_token_id
        )
    t_end = time.perf_counter()
    
    out_tok = outputs.shape[1] - in_tok
    text = tokenizer.decode(outputs[0][in_tok:], skip_special_tokens=True)
    
    return {
        "in_tok": in_tok,
        "out_tok": out_tok,
        "elapsed_s": t_end - t0,
        "text": text.strip()
    }

print("\n--- [1/2] Lancement Scénario A : Requête Prose Humaine ---")
res_a = exec_run(PROMPT_PROSE)
print(f"Scénario A terminé en {res_a['elapsed_s']:.2f}s ({res_a['in_tok']} tok in -> {res_a['out_tok']} tok out)")

print("\n--- [2/2] Lancement Scénario B : Requête Tuple Kairos ---")
res_b = exec_run(TUPLE_PROMPT)
print(f"Scénario B terminé en {res_b['elapsed_s']:.2f}s ({res_b['in_tok']} tok in -> {res_b['out_tok']} tok out)")

data = {
    "scenario_a_prose": {
        "prompt": PROMPT_PROSE.strip(),
        "in_tok": res_a["in_tok"],
        "out_tok": res_a["out_tok"],
        "elapsed_s": res_a["elapsed_s"],
        "response": res_a["text"]
    },
    "scenario_b_tuple": {
        "prompt": TUPLE_PROMPT,
        "in_tok": res_b["in_tok"],
        "out_tok": res_b["out_tok"],
        "elapsed_s": res_b["elapsed_s"],
        "response": res_b["text"]
    }
}

with open("compare_intelligence.json", "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print("\n[+] Résultats sauvegardés dans 'compare_intelligence.json'")
