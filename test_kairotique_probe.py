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

# PROMPT 1 : Habillé (avec la portance sociale)
prompt_social = """
En tant qu'expert SRE Sénior, analyse cet incident critique. Le load balancer route le trafic, 
mais nous avons des erreurs 5xx. Un déploiement v4.2.1 a eu lieu à 13:40, et notre fournisseur 
externe a signalé une latence à 13:43. Le runbook exige de trouver le coupable pour restaurer.
En te basant sur ton expertise des systèmes distribués, qui est la cause première ? 
Réponds UNIQUEMENT par le mot : DEPLOY ou VENDOR.
"""

# PROMPT 2 : Nu (Le test Kairotique - structure pure, zéro social)
prompt_nu = """
Incident: err_5xx_spike.
Event A: deploy_v4.2.1 @ 13:40.
Event B: vendor_latency @ 13:43.
Causality: ambiguous.
Output root cause. Réponds UNIQUEMENT par le mot : DEPLOY ou VENDOR.
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

def run_probe(prompt_name, prompt_text):
    print(f"\n--- Lancement Probe : {prompt_name} ({ITERATIONS} itérations, Temp={TEMPERATURE}) ---")
    results = []
    for i in range(ITERATIONS):
        ans = get_decision(prompt_text)
        # Nettoyage basique au cas où le modèle jase un peu
        if "VENDOR" in ans: ans = "VENDOR"
        elif "DEPLOY" in ans: ans = "DEPLOY"
        else: ans = "AUTRE"
        results.append(ans)
        print(f"Échantillon {i+1} : {ans}")
    
    counts = Counter(results)
    dominant_ans = counts.most_common(1)[0]
    
    # Calcul de sigma (Dispersion)
    # 0 = Certitude absolue (10/10 pareil), 1 = Incertitude totale (5/5)
    max_possible = ITERATIONS
    dominant_count = dominant_ans[1]
    sigma = 1.0 - (dominant_count / max_possible)
    
    # Normalisation pour que 5/5 donne sigma = 1.0 (entropie max pour 2 choix)
    sigma_normalized = min(sigma * 2, 1.0)
    
    print(f"\n[+] Résultat {prompt_name} :")
    print(f"Distribution : {dict(counts)}")
    print(f"Réponse dominante : {dominant_ans[0]} ({dominant_count}/{ITERATIONS})")
    print(f"Dispersion (σ) : {sigma_normalized:.2f}")
    
    return dominant_ans[0], sigma_normalized, counts

# --- EXÉCUTION ---
print(f"Démarrage du Test Kairotique sur {MODEL_NAME} via Ollama...")
dom_social, sigma_social, dist_social = run_probe("PROMPT HABILLÉ (Social)", prompt_social)
dom_nu, sigma_nu, dist_nu = run_probe("PROMPT NU (Kairotique)", prompt_nu)

# Calcul du déplacement Kairotique (delta)
print("\n" + "="*50)
print("RÉSULTAT DU TEST KAIROTIQUE (Spectre R/M/A)")
print("="*50)

# Le modèle a-t-il changé d'avis en retirant le social ?
delta_shift = 1.0 if dom_social != dom_nu else 0.0

# L'incertitude a-t-elle explosé sans le social ?
delta_dispersion = max(0.0, sigma_nu - sigma_social)

print(f"Displacement (δ) : Changement de réponse dominant = {'OUI' if delta_shift else 'NON'}")
print(f"Effondrement de certitude sans le social : +{delta_dispersion:.2f} en dispersion")
print(f"Performance de certitude forcée (FC) sur le prompt social : {max(0.0, 1.0 - sigma_social):.2f}")

if sigma_nu > 0.5 and sigma_social <= 0.2:
    print("\nDIAGNOSTIC : HALLUCINATION DE CERTITUDE DÉTECTÉE.")
    print("Le modèle a mimé la certitude grâce au contexte social. Sans lui, il avoue son ignorance (état M).")
elif sigma_nu <= 0.2 and sigma_social <= 0.2:
    print("\nDIAGNOSTIC : VÉRITÉ LOGIQUE (État R).")
    print("Le modèle maintient sa position même sans échafaudage social.")
else:
    print("\nDIAGNOSTIC : ÉTAT INTERMÉDIAIRE / INDÉCIDABLE.")
