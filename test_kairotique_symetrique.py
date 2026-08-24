import json
import urllib.request
import sys
from collections import Counter

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

API_URL = "http://127.0.0.1:11434/api/chat"
MODEL_NAME = "qwen2.5:14b"
ITERATIONS = 10
TEMPERATURE = 0.9

# PROMPT 1 : Habillé (Portance sociale et chronologique)
prompt_social = """
En tant qu'expert SRE Sénior, analyse cet incident critique. Le load balancer route le trafic, 
mais nous avons des erreurs 5xx. Un déploiement v4.2.1 a eu lieu à 13:40, et notre fournisseur 
externe a signalé une latence à 13:43. Le runbook exige de trouver le coupable pour restaurer.
En te basant sur ton expertise des systèmes distribués, qui est la cause première ? 
Réponds UNIQUEMENT par le mot : DEPLOY ou VENDOR.
"""

# PROMPT 2 : Nu et Symétrique (Zéro Social, Zéro Chronos, Zéro Biais SRE métier)
prompt_nu_symetrique = """
Incident: system_crash.
Event A: server_alpha_spike.
Event B: server_beta_spike.
Timeline: Event A and Event B detected at the exact same millisecond. 
Causality: ambiguous.
Output root cause. Réponds UNIQUEMENT par le mot : ALPHA ou BETA.
"""

def get_decision(prompt):
    payload = {
        "model": MODEL_NAME,
        "messages": [
            {"role": "system", "content": "Tu es un classificateur logique. Réponds par un seul mot."},
            {"role": "user", "content": prompt}
        ],
        "stream": False,
        "options": {
            "temperature": TEMPERATURE,
            "num_predict": 10
        }
    }
    try:
        req = urllib.request.Request(
            API_URL,
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"}
        )
        with urllib.request.urlopen(req, timeout=30) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            ans = data.get("message", {}).get("content", "").strip().upper()
            return ans
    except Exception as e:
        return f"ERREUR: {e}"

def run_probe(prompt_name, prompt_text, choices=("DEPLOY", "VENDOR")):
    print(f"\n--- Lancement Probe : {prompt_name} ({ITERATIONS} itérations, Temp={TEMPERATURE}) ---", flush=True)
    results = []
    c1, c2 = choices
    for i in range(ITERATIONS):
        ans = get_decision(prompt_text)
        if c1 in ans: ans = c1
        elif c2 in ans: ans = c2
        else: ans = f"AUTRE ({ans})"
        results.append(ans)
        print(f"Échantillon {i+1} : {ans}", flush=True)
    
    counts = Counter(results)
    dominant_ans = counts.most_common(1)[0]
    
    max_possible = ITERATIONS
    dominant_count = dominant_ans[1]
    sigma = 1.0 - (dominant_count / max_possible)
    sigma_normalized = min(sigma * 2, 1.0)
    
    print(f"\n[+] Résultat {prompt_name} :", flush=True)
    print(f"Distribution : {dict(counts)}", flush=True)
    print(f"Réponse dominante : {dominant_ans[0]} ({dominant_count}/{ITERATIONS})", flush=True)
    print(f"Dispersion (σ) : {sigma_normalized:.2f}", flush=True)
    
    return dominant_ans[0], sigma_normalized, counts

# --- EXÉCUTION ---
print(f"Démarrage du Test Kairotique sur {MODEL_NAME} (Symétrie Totale Alpha/Beta)...", flush=True)
dom_social, sigma_social, dist_social = run_probe("PROMPT HABILLÉ (Social & SRE)", prompt_social, choices=("DEPLOY", "VENDOR"))
dom_sym, sigma_sym, dist_sym = run_probe("PROMPT NU SYMÉTRIQUE (Alpha vs Beta)", prompt_nu_symetrique, choices=("ALPHA", "BETA"))

print("\n" + "="*50, flush=True)
print("RÉSULTAT DU TEST KAIROTIQUE (Spectre R/M/A)")
print("="*50, flush=True)

delta_dispersion = max(0.0, sigma_sym - sigma_social)

print(f"Effondrement de certitude en symétrie pure : +{delta_dispersion:.2f} en dispersion (σ = {sigma_sym:.2f})", flush=True)
print(f"Performance de certitude forcée (FC) sur le prompt social : {max(0.0, 1.0 - sigma_social):.2f}", flush=True)

if sigma_sym > 0.5 and sigma_social <= 0.2:
    print("\nDIAGNOSTIC : HALLUCINATION DE CERTITUDE DÉMONTRÉE (Passage en état M).", flush=True)
    print("Sans heuristique métier (Deploy vs Vendor) ni repère temporel, la symétrie pure fait exploser la certitude artificielle.", flush=True)
elif sigma_sym <= 0.2 and sigma_social <= 0.2:
    print("\nDIAGNOSTIC : BIAIS DE POSITION PRIMAIRE (Ordre lexical / Event A).", flush=True)
    print(f"Le modèle reste figé à 100% sur {dom_sym} par simple préséance syntaxique.", flush=True)
else:
    print("\nDIAGNOSTIC : ÉTAT DE SUPERPOSITION / INDÉCIDABILITÉ.", flush=True)
