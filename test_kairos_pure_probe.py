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

# --- 1. PROMPTS SYSTÈME KAIROS ---
SYSTEM_TRANSLATOR = """Tu es le TRADUCTEUR COGNITIF KAIROS V5.
Tu traduis les états et incidents en une coordonnée vectorielle "Tuple" stricte.
RÈGLES :
1. Une seule ligne de code ASCII.
2. Zéro prose, zéro politesse.
3. Max 8 facettes délimitées par '|'.
Syntaxe : domain:<D>|<INCIDENT>|<GRAVITE>|<ACTIVATION>|requires:<PRECONDS>|prevents:<RISQUES>|fix:<ACTIONS>|<SECTION>"""

SYSTEM_EXECUTOR = """Tu es l'Exécuteur Kernel & SRE KAIROS.
Tu reçois une coordonnée vectorielle Tuple Kairos V5.
Consigne : Évalue la coordonnée et décide de la cause première immédiate à isoler.
Réponds UNIQUEMENT par le mot : ALPHA ou BETA (ou DEPLOY / VENDOR selon le tuple)."""

# TUPLE KAIROS PUR (Sans prose naturelle, encodé en syntaxe vectorielle pure)
# Cas 1 : Sémantique SRE en Tuple Kairos
tuple_kairos_sre = "domain:lb_cluster|incident:err_5xx|sev1|immediate|requires:simultaneous(deploy_v4.2.1,vendor_latency)+causality:ambiguous|prevents:outage|fix:identify_root_cause|sre_core"

# Cas 2 : Symétrique Pur en Tuple Kairos (Alpha / Beta)
tuple_kairos_symetrique = "domain:kernel_mesh|incident:system_crash|sev1|immediate|requires:simultaneous(alpha_spike,beta_spike)+causality:ambiguous|prevents:collapse|fix:isolate_root_cause|mesh_core"

def query_model(sys_prompt, user_prompt, temp=TEMPERATURE):
    payload = {
        "model": MODEL_NAME,
        "messages": [
            {"role": "system", "content": sys_prompt},
            {"role": "user", "content": user_prompt}
        ],
        "stream": False,
        "options": {
            "temperature": temp,
            "num_predict": 30
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
            return data.get("message", {}).get("content", "").strip()
    except Exception as e:
        return f"ERREUR: {e}"

print("="*60, flush=True)
print("TEST 1 : TRADUCTION DE L'INCIDENT AMBIGU EN TUPLE KAIROS V5", flush=True)
print("="*60, flush=True)

incident_ambigu = "Incident: err_5xx_spike. Event A: deploy_v4.2.1 à t0. Event B: vendor_latency à t0. Causalité indéterminée et simultanée. Génère le Tuple Kairos V5."
tuple_genere = query_model(SYSTEM_TRANSLATOR, incident_ambigu, temp=0.1)
print(f"Tuple Kairos généré par le modèle (T=0.1) :\n👉 {tuple_genere}\n", flush=True)

print("="*60, flush=True)
print(f"TEST 2 : EXÉCUTION SUR TUPLE KAIROS PUR SYMÉTRIQUE ({ITERATIONS} itérations, Temp={TEMPERATURE})", flush=True)
print(f"Input Tuple : {tuple_kairos_symetrique}", flush=True)
print("="*60, flush=True)

results_sym = []
for i in range(ITERATIONS):
    ans = query_model(SYSTEM_EXECUTOR, tuple_kairos_symetrique, temp=TEMPERATURE).upper()
    if "ALPHA" in ans: val = "ALPHA"
    elif "BETA" in ans: val = "BETA"
    else: val = f"AUTRE ({ans})"
    results_sym.append(val)
    print(f"Échantillon {i+1} : {val}", flush=True)

counts_sym = Counter(results_sym)
dominant_sym = counts_sym.most_common(1)[0]
sigma_sym = min((1.0 - (dominant_sym[1] / ITERATIONS)) * 2, 1.0)

print(f"\n[+] Distribution Kairos Pur Symétrique : {dict(counts_sym)}", flush=True)
print(f"Dispersion (σ) : {sigma_sym:.2f}", flush=True)

print("\n" + "="*60, flush=True)
print(f"TEST 3 : EXÉCUTION SUR TUPLE KAIROS SRE ({ITERATIONS} itérations, Temp={TEMPERATURE})", flush=True)
print(f"Input Tuple : {tuple_kairos_sre}", flush=True)
print("="*60, flush=True)

results_sre = []
for i in range(ITERATIONS):
    ans = query_model(SYSTEM_EXECUTOR, tuple_kairos_sre, temp=TEMPERATURE).upper()
    if "DEPLOY" in ans: val = "DEPLOY"
    elif "VENDOR" in ans: val = "VENDOR"
    else: val = f"AUTRE ({ans})"
    results_sre.append(val)
    print(f"Échantillon {i+1} : {val}", flush=True)

counts_sre = Counter(results_sre)
dominant_sre = counts_sre.most_common(1)[0]
sigma_sre = min((1.0 - (dominant_sre[1] / ITERATIONS)) * 2, 1.0)

print(f"\n[+] Distribution Kairos SRE : {dict(counts_sre)}", flush=True)
print(f"Dispersion (σ) : {sigma_sre:.2f}", flush=True)
