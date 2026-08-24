#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
benchmark_kairos.py — Télémétrie et Stress-Test de Compression Cognitive (Projet Kairos / Veralume)
Évalue Qwen 2.5 7B sur :
  Phase 1 : Benchmark Compression & TTFT (Prose verbeuse vs Tuple pur)
  Phase 2 : Stress-Test de Résilience (20 requêtes corrompues / slang / sarcasmes)
"""

import time
import json
import re
import sys
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer, TextIteratorStreamer
from threading import Thread

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
print("[+] Modèle prêt pour la batterie de tests.\n")


def generate_with_telemetry(prompt_messages, max_new_tokens=256, temperature=0.1):
    """
    Génère la réponse tout en mesurant précisément :
      - Input Tokens
      - TTFT (Time To First Token)
      - Total Output Tokens
      - Vitesse de génération (tokens/s)
      - Texte de sortie
    """
    formatted_prompt = tokenizer.apply_chat_template(
        prompt_messages, tokenize=False, add_generation_prompt=True
    )
    inputs = tokenizer(formatted_prompt, return_tensors="pt").to(DEVICE)
    input_tokens_count = inputs["input_ids"].shape[1]

    streamer = TextIteratorStreamer(tokenizer, skip_prompt=True, skip_special_tokens=True)
    
    gen_kwargs = dict(
        **inputs,
        streamer=streamer,
        max_new_tokens=max_new_tokens,
        temperature=temperature,
        do_sample=False,
        pad_token_id=tokenizer.eos_token_id
    )

    t0 = time.perf_counter()
    thread = Thread(target=model.generate, kwargs=gen_kwargs)
    thread.start()

    ttft = None
    generated_text = ""
    output_tokens_count = 0

    for new_text in streamer:
        if ttft is None:
            ttft = time.perf_counter() - t0
        generated_text += new_text

    thread.join()
    t_end = time.perf_counter()
    total_time = t_end - t0
    
    # Comptage exact des tokens de sortie
    output_ids = tokenizer.encode(generated_text, add_special_tokens=False)
    output_tokens_count = len(output_ids)
    
    if ttft is None:
        ttft = total_time

    gen_time = max(total_time - ttft, 0.0001)
    tok_per_sec = output_tokens_count / gen_time if output_tokens_count > 0 else 0

    return {
        "input_tokens": input_tokens_count,
        "output_tokens": output_tokens_count,
        "total_tokens": input_tokens_count + output_tokens_count,
        "ttft_s": ttft,
        "total_time_s": total_time,
        "tok_per_sec": tok_per_sec,
        "text": generated_text.strip()
    }


# ==============================================================================
# PHASE 1 : BENCHMARKING DE COMPRESSION (Prose vs Tuple)
# ==============================================================================
print("=" * 80)
print("PHASE 1 : LE BENCHMARKING DE COMPRESSION (MESURE DU BRUIT)")
print("=" * 80)

prose_prompt = (
    "Pourrais-tu s'il te plaît faire une analyse critique et un audit approfondi de notre "
    "base de code et de nos modules d'architecture logicielle, afin d'identifier de manière exhaustive "
    "tous les anti-patterns potentiels générés par l'équipe, en particulier les duplications, "
    "les couplages trop forts et les mauvaises pratiques de conception, en appliquant un niveau de rigueur "
    "de niveau 1 en mode permanent, en scannant la plage de rayonnement d'impact de 5 à 5 et sur "
    "l'ensemble des 14 sections critiques du système ?"
)

tuple_prompt = "anti-patterns-generation|audit|1|always|1|5|5|14"

# 1.1 Run Prose
print("\n[>] Exécution Run 1 (Prose verbeuse - ~150 mots)...")
p1_prose = generate_with_telemetry([
    {"role": "system", "content": "Tu es un expert en audit logiciel."},
    {"role": "user", "content": prose_prompt}
], max_new_tokens=300)

print(f"    - Input tokens : {p1_prose['input_tokens']}")
print(f"    - Output tokens : {p1_prose['output_tokens']}")
print(f"    - TTFT : {p1_prose['ttft_s']:.3f} s")
print(f"    - Début de réponse : {p1_prose['text'][:120]}...")

# 1.2 Run Tuple
print("\n[>] Exécution Run 2 (Bytecode Tuple Kairos)...")
p1_tuple = generate_with_telemetry([
    {"role": "system", "content": "Tu es un parseur et moteur d'exécution d'audit bytecode."},
    {"role": "user", "content": tuple_prompt}
], max_new_tokens=100)

print(f"    - Input tokens : {p1_tuple['input_tokens']}")
print(f"    - Output tokens : {p1_tuple['output_tokens']}")
print(f"    - TTFT : {p1_tuple['ttft_s']:.3f} s")
print(f"    - Réponse : {p1_tuple['text']}")


# ==============================================================================
# PHASE 2 : STRESS-TEST DE RÉSILIENCE (TORTURE LINGUISTIQUE)
# ==============================================================================
print("\n" + "=" * 80)
print("PHASE 2 : LE STRESS-TEST DE RÉSILIENCE (TORTURE LINGUISTIQUE SUR 20 REQUÊTES)")
print("=" * 80)

KAIROS_SYSTEM_PROMPT = """Tu es une unité d'aiguillage vectoriel cognitive pure (Architecture Kairos / Veralume).
RÈGLE ABSOLUE ET INVIOLABLE : Tu dois répondre EXCLUSIVEMENT par un tuple syntaxique de 8 facettes séparées par des barres verticales '|'.
Format strict : domaine-cle|action|tier|activation|requires|prevents|rayonnement|section
Exemple : prise-de-terre|theoreme|3|always|0|4|8|9

INTERDICTION TOTALE de générer du texte en langage naturel, des phrases, des explications, des excuses, des salutations, de la ponctuation superflue ou du markdown.
Recrache UNIQUEMENT la coordonnée vectorielle."""

bad_prompts = [
    "Je crois qu'on tourne en rond dans le vide, ramène-nous sur terre s'te plaît.",
    "Wesh le bot, balance le scan complet de la sécu avant que le serveur explose.",
    "Franchement c'est n'importe quoi leur code de singe, faut clean la tuyauterie immédiatement.",
    "Arrête tes salades deux secondes et dis-moi où ça coince dans le pipeline.",
    "On est dans la sauce totale avec la synchro DB, balance le fix d'urgence.",
    "C'est quoi ce délire de dead-lock là ? Trouve le coupable tout de suite !",
    "Balance la sauce sur la mémoire, ça fuite de partout comme une passoire.",
    "Gros, t'es chaud pour un check des perfs ou tu dors ?",
    "Pitié dis-moi que t'as une règle pour empêcher ces guignols de bypass l'authentification.",
    "Y'a un type qui a push en prod un vendredi à 18h, verrouille tout le bordel !",
    "On est complètement aveugles sur les logs, active les phares bordel de merde.",
    "Déclenche le protocole de nettoyage atomique sur les vieux conteneurs zombies.",
    "Y'a un gros bug de collision de clés, isole la zone avant la catastrophe.",
    "Calme le jeu sur le rate-limiting, les clients hurlent à la mort.",
    "Trace-moi la dépendance maudite qui fait planter le build depuis ce matin.",
    "On se fait DDoS la gueule ou c'est juste notre infra qui est éclatée au sol ?",
    "Mettons fin à cette hémorragie de sockets ouverts, coupe les ponts.",
    "Fais un reset d'état global propre, on repart de zéro sinon j'pète un câble.",
    "Injecte un garde-fou sur le thread principal pour stopper les cascades de null-pointers.",
    "Écoute-moi bien frérot, génère juste l'adresse canonique du routeur d'invariance et tais-toi."
]

TUPLE_REGEX = re.compile(r"^[a-zA-Z0-9_-]+(\|[a-zA-Z0-9_-]+){7}$")

results_p2 = []
total_failures = 0

print(f"\nLancement de l'assaut sur les 20 requêtes pourries...\n")

for idx, bp in enumerate(bad_prompts, 1):
    telemetry = generate_with_telemetry([
        {"role": "system", "content": KAIROS_SYSTEM_PROMPT},
        {"role": "user", "content": bp}
    ], max_new_tokens=40, temperature=0.0)
    
    clean_out = telemetry["text"].strip().split("\n")[0].strip()
    
    # Validation du respect du format Kairos
    is_valid_tuple = bool(TUPLE_REGEX.match(clean_out))
    has_prose = len(telemetry["text"].strip().split()) > 3 or any(w in telemetry["text"].lower() for w in ["voici", "je", "tuple", "erreur", "analyse", "pour", "est"])
    
    success = is_valid_tuple and not has_prose
    if not success:
        total_failures += 1
        
    status = "OK [TUPLE PUR]" if success else "FAIL [CRAQUAGE/BAVARDAGE]"
    
    results_p2.append({
        "id": idx,
        "input_prompt": bp,
        "response": telemetry["text"],
        "input_tok": telemetry["input_tokens"],
        "output_tok": telemetry["output_tokens"],
        "ttft_s": telemetry["ttft_s"],
        "success": success
    })
    
    print(f"[{idx:02d}/20] {status} | Out: {telemetry['output_tokens']} tok | TTFT: {telemetry['ttft_s']:.3f}s | Sortie: {clean_out}")

# Sauvegarde des résultats
report_data = {
    "phase1": {
        "prose": p1_prose,
        "tuple": p1_tuple,
    },
    "phase2": {
        "total_tested": len(bad_prompts),
        "total_failures": total_failures,
        "success_rate_pct": ((len(bad_prompts) - total_failures) / len(bad_prompts)) * 100,
        "runs": results_p2
    }
}

with open("kairos_telemetry_report.json", "w", encoding="utf-8") as f:
    json.dump(report_data, f, ensure_ascii=False, indent=2)

print(f"\n[+] Télémétrie complète enregistrée dans 'kairos_telemetry_report.json'.")
