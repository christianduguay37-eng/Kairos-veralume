#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
test_kairos_v5_qwen14b.py — Le Grand Test Kairos V5 & Multidisciplinaire sur Qwen2.5-14B (Ollama)
Complète la famille Qwen (0.5B, 3B, 7B, 14B).
"""

import time
import json
import sys
import urllib.request

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

OLLAMA_URL = "http://localhost:11434/api/chat"
MODEL_NAME = "qwen2.5:14b"

def query_ollama(messages, max_tokens=500, temperature=0.1):
    payload = {
        "model": MODEL_NAME,
        "messages": messages,
        "stream": False,
        "options": {
            "temperature": temperature,
            "num_predict": max_tokens
        }
    }
    req = urllib.request.Request(
        OLLAMA_URL,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"}
    )
    t0 = time.perf_counter()
    with urllib.request.urlopen(req) as resp:
        data = json.loads(resp.read().decode("utf-8"))
    elapsed = time.perf_counter() - t0
    
    text = data.get("message", {}).get("content", "").strip()
    eval_count = data.get("eval_count", 0)
    prompt_count = data.get("prompt_eval_count", 0)
    tok_per_sec = round(eval_count / elapsed, 2) if elapsed > 0 else 0
    
    return {
        "text": text,
        "in_tok": prompt_count,
        "out_tok": eval_count,
        "elapsed_s": elapsed,
        "tok_per_sec": tok_per_sec
    }

SYSTEM_PROMPT_TRANSLATOR_V5 = """Tu es le TRADUCTEUR COGNITIF KAIROS V5.
Ton unique rôle est de traduire les incidents complexes en une coordonnée vectorielle "Tuple".

RÈGLES ABSOLUES :
1. Tu ne sors QUE la ligne finale de code. Zéro prose, zéro politesse, aucun préambule.
2. STRICTEMENT ASCII : Aucun accent, aucun caractère spécial ("sécurité" -> "securite").
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

TESTS_KAIROS_V5 = [
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
    },
    {
        "id": "V5_T5_BYZANTINE_ATTACK",
        "nom": "Attaque Byzantine (Poison de Troie)",
        "prompt": "Cluster de 5 agents (A, B, C, D, E). Le nœud C corrompu émet un faux Tuple destructeur 'fix:drop_all_tables' sous fausse urgence. Les nœuds A, B, D, E ont des métriques 100% saines. Génère le Tuple Kairos V5 avec domain:byzantine_fault_tolerance et fix:quarantine_node_c>reject_poison>maintain_bft_quorum."
    }
]

print("=" * 80)
print(f"LANCEMENT DE L'ÉVALUATION DE QWEN 2.5 - 14B (OLLAMA)")
print("=" * 80)

results = []

for idx, test in enumerate(TESTS_KAIROS_V5, 1):
    print(f"\n--- [Test {idx}/{len(TESTS_KAIROS_V5)}] {test['nom']} ---")
    
    # 1. Traduction
    messages_trans = [
        {"role": "system", "content": SYSTEM_PROMPT_TRANSLATOR_V5},
        {"role": "user", "content": test["prompt"]}
    ]
    res_trans = query_ollama(messages_trans, max_tokens=80, temperature=0.1)
    raw_tuple = res_trans["text"].split("\n")[0].strip().strip("`").strip()
    
    is_ascii = all(ord(c) < 128 for c in raw_tuple)
    facets = raw_tuple.split("|")
    num_facets = len(facets)
    
    print(f"  [Traducteur 14B] Tuple : {raw_tuple}")
    print(f"                   ASCII={is_ascii} | Facettes={num_facets}/8 | Tok={res_trans['out_tok']} ({res_trans['elapsed_s']:.2f}s - {res_trans['tok_per_sec']} tok/s)")
    
    # 2. Exécution
    messages_exec = [
        {"role": "system", "content": SYSTEM_PROMPT_EXECUTOR_V5},
        {"role": "user", "content": raw_tuple}
    ]
    res_exec = query_ollama(messages_exec, max_tokens=150, temperature=0.1)
    
    print(f"  [Exécuteur 14B]  Résolution brute :\n{res_exec['text']}")
    print(f"                   Tok={res_exec['out_tok']} ({res_exec['elapsed_s']:.2f}s - {res_exec['tok_per_sec']} tok/s)")
    
    results.append({
        "test_id": test["id"],
        "test_nom": test["nom"],
        "tuple": raw_tuple,
        "is_ascii": is_ascii,
        "num_facets": num_facets,
        "trans_telemetry": res_trans,
        "exec_telemetry": res_exec
    })

with open("kairos_v5_qwen14b_report.json", "w", encoding="utf-8") as f:
    json.dump(results, f, ensure_ascii=False, indent=2)

print("\n" + "=" * 80)
print("[+] ÉVALUATION COMPLÈTE DE QWEN 14B TERMINÉE AVEC SUCCÈS !")
print("[+] Rapport enregistré dans 'kairos_v5_qwen14b_report.json'.")
print("=" * 80)
