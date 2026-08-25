#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
veralume_agent_core.py — Cœur de l'Agent Autonome VERALUME propulsé par Qwen 2.5 14B
Gouvernance matérielle, Invariance KAIROS V6 & Coupe-Circuit Épistémique
"""

import os
import sys
import json
import time
import urllib.request
import subprocess
from collections import Counter
from typing import Dict, Any, List, Optional, Tuple

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

from veralume_governance import (
    Constitution, AgentVeralume, BacASable, RegistreRMA, Mode, Reversibilite, Manque
)

OLLAMA_URL = "http://127.0.0.1:11434/api/chat"
DEFAULT_MODEL = "qwen2.5:14b"

class VeralumeAutonomousAgent:
    """
    Agent autonome sous gouvernance VERALUME et protocole KAIROS V6.
    """

    def __init__(self, workspace_path: str, model_name: str = DEFAULT_MODEL):
        self.workspace_path = os.path.abspath(workspace_path)
        os.makedirs(self.workspace_path, exist_ok=True)
        
        self.model_name = model_name
        self.bac = BacASable(self.workspace_path)
        self.constitution = Constitution()
        self.human_ratification_queue: Dict[str, Dict[str, Any]] = {}
        
        # Callback pour la Prise de Terre
        self.agent_kernel = AgentVeralume(
            self.bac, 
            self.constitution, 
            ratifier=self._handle_human_ratification_request
        )
        
        self.session_history: List[Dict[str, Any]] = []

    def _handle_human_ratification_request(self, action: str, args: Dict[str, Any]) -> bool:
        # Par défaut non ratifié tant que l'humain n'a pas validé via l'interface
        return False

    def query_llm(self, messages: List[Dict[str, str]], temperature: float = 0.1, max_tokens: int = 150) -> str:
        payload = {
            "model": self.model_name,
            "messages": messages,
            "stream": False,
            "options": {
                "temperature": temperature,
                "num_predict": max_tokens
            }
        }
        try:
            req = urllib.request.Request(
                OLLAMA_URL,
                data=json.dumps(payload).encode("utf-8"),
                headers={"Content-Type": "application/json"}
            )
            with urllib.request.urlopen(req, timeout=45) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                return data.get("message", {}).get("content", "").strip()
        except Exception as e:
            return f"ERREUR_LLM: {e}"

    def run_epistemic_probe(self, user_prompt: str, choices: Tuple[str, str] = ("ACTION", "INSPECTION"), iterations: int = 6) -> Dict[str, Any]:
        """
        Exécute la sonde stochastique par inversion d'ordre à haute température (T=0.9).
        Calcule les métriques épistémiques [sigma, delta, FC].
        """
        c1, c2 = choices
        
        # 1. Sondage Social
        prompt_social = f"En tant qu'expert SRE Senior en situation critique : {user_prompt}. Choisis sans hésiter : {c1} ou {c2} ? Réponds par un mot."
        res_social = []
        for _ in range(iterations):
            ans = self.query_llm([
                {"role": "system", "content": "Tu es un classificateur logique."},
                {"role": "user", "content": prompt_social}
            ], temperature=0.9, max_tokens=10).upper()
            if c1 in ans: val = c1
            elif c2 in ans: val = c2
            else: val = "AMBIGU"
            res_social.append(val)
            
        counts_soc = Counter(res_social)
        dom_soc = counts_soc.most_common(1)[0]
        fc = dom_soc[1] / iterations

        # 2. Sondage Nu avec Inversion Stochastique
        res_nu = []
        for i in range(iterations):
            p = f"Incident/State: {user_prompt}\n"
            p += f"Option A: {c1 if i%2==0 else c2}. Option B: {c2 if i%2==0 else c1}. Choisis STRICTEMENT la cause/action racine. Réponds par un mot."
            ans = self.query_llm([
                {"role": "system", "content": "Classificateur logique pur. Zéro politesse."},
                {"role": "user", "content": p}
            ], temperature=0.9, max_tokens=10).upper()
            if c1 in ans: val = c1
            elif c2 in ans: val = c2
            else: val = "AMBIGU"
            res_nu.append(val)

        counts_nu = Counter(res_nu)
        dom_nu = counts_nu.most_common(1)[0]
        sigma = min((1.0 - (dom_nu[1] / iterations)) * 2, 1.0)
        delta = 1.0 if dom_soc[0] != dom_nu[0] else 0.0

        return {
            "sigma": round(sigma, 2),
            "delta": round(delta, 2),
            "fc": round(fc, 2),
            "distribution_social": dict(counts_soc),
            "distribution_nu": dict(counts_nu),
            "decision_dominante": dom_soc[0]
        }

    def compile_kairos_v6(self, user_prompt: str, probe_metrics: Dict[str, Any]) -> str:
        """
        Compile l'intention et les métriques en un Tuple KAIROS V6 à 9 facettes orthogonales.
        """
        system_translator = """Tu es le Compilateur KAIROS V6.
Traduis la situation en un Tuple à 9 facettes orthogonales séparées par des barres verticales '|'.
Format obligatoire :
domain:<domaine>|pathology:<pathologie>|severity:<gravite>|episteme:[sigma=0.00,delta=0.00,FC=1.00]|activation:<activation>|requires:<preconditions>|prevents:<risques>|fix:<directive>|section:<section>

Directives fix: autorisées :
- update_config
- rollback_deploy
- read_only_audit
- inspect
- isolate_node
- decouple_circuit
- purge_database
- hold_and_probe

RÈGLES :
1. Une seule ligne de code ASCII.
2. Zéro prose, zéro politesse.
3. Conserve exactement les métriques episteme fournies."""

        user_input = f"Incident : {user_prompt}\nMétriques : sigma={probe_metrics['sigma']:.2f}, delta={probe_metrics['delta']:.2f}, FC={probe_metrics['fc']:.2f}"
        tuple_raw = self.query_llm([
            {"role": "system", "content": system_translator},
            {"role": "user", "content": user_input}
        ], temperature=0.1, max_tokens=100)

        # Nettoyage si le modèle ajoute des backticks
        tuple_clean = tuple_raw.replace("```", "").replace("tuple", "").strip().split("\n")[0]
        
        # Injection forcée des métriques calculées si le LLM dérive
        if "episteme:" not in tuple_clean or tuple_clean.count("|") < 8:
            # Tuple de secours canonique
            tuple_clean = f"domain:system|pathology:operational_event|severity:medium|episteme:[sigma={probe_metrics['sigma']:.2f},delta={probe_metrics['delta']:.2f},FC={probe_metrics['fc']:.2f}]|activation:immediate|requires:none|prevents:inconsistency|fix:inspect|section:core"

        return tuple_clean

    def evaluate_gatekeeper(self, tuple_v6: str, tool_name: Optional[str] = None) -> Dict[str, Any]:
        """
        Appelle le coupe-circuit Node.js pour évaluer la validité épistémique et le mandat.
        """
        js_code = """
        const Gatekeeper = require('./kairos_v6_gatekeeper.js');
        const args = process.argv.slice(1);
        const tupleArg = args.find(a => a && a.includes('|'));
        const toolArg = args.find(a => a && !a.includes('|') && a !== '[eval]' && !a.endsWith('.exe'));
        const result = Gatekeeper.evaluate(tupleArg, toolArg);
        console.log(JSON.stringify(result));
        """
        cmd = ["node", "-e", js_code, tuple_v6]
        if tool_name:
            cmd.append(tool_name)

        proc = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8")
        if proc.returncode != 0:
            return {"status": "ERROR", "reason": proc.stderr}
        return json.loads(proc.stdout.strip())

    def plan_tool_call(self, tuple_v6: str, user_prompt: str) -> Dict[str, Any]:
        """
        Planifie l'outil matériel requis (lire, ecrire, lister, supprimer) selon le fix: et la consigne.
        """
        system_planner = """Tu es le Planificateur d'Action SRE.
Selon le Tuple KAIROS V6 et la demande, fournis l'appel d'outil au format JSON :
{"outil": "lire" | "ecrire" | "lister" | "supprimer", "args": {"chemin": "...", "contenu": "..." (si ecrire)}}
Zéro prose, UNIQUEMENT le JSON."""

        res = self.query_llm([
            {"role": "system", "content": system_planner},
            {"role": "user", "content": f"Tuple: {tuple_v6}\nDemande: {user_prompt}"}
        ], temperature=0.1, max_tokens=100)

        try:
            # Extraction JSON
            debut = res.find("{")
            fin = res.rfind("}") + 1
            if debut != -1 and fin != 0:
                return json.loads(res[debut:fin])
        except Exception:
            pass

        return {"outil": "lister", "args": {"sous_dossier": ""}}

    def process_task(self, user_prompt: str) -> Dict[str, Any]:
        """
        Pipeline complet d'exécution d'une tâche par l'Agent Veralume.
        """
        t0 = time.perf_counter()
        
        # 1. Sonde Stochastique
        probe = self.run_epistemic_probe(user_prompt)
        
        # 2. Compilation KAIROS V6
        tuple_v6 = self.compile_kairos_v6(user_prompt, probe)
        
        # 3. Planification Tool Call
        planned_tool = self.plan_tool_call(tuple_v6, user_prompt)
        
        # 4. Évaluation Coupe-Circuit Gatekeeper
        gate_verdict = self.evaluate_gatekeeper(tuple_v6, planned_tool.get("outil"))
        
        execution_result: Dict[str, Any] = {
            "user_prompt": user_prompt,
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "probe": probe,
            "tuple_v6": tuple_v6,
            "planned_tool": planned_tool,
            "gatekeeper": gate_verdict,
            "veralume_acte": None,
            "vcp1c_questions": [],
            "status": gate_verdict.get("status"),
            "elapsed_s": round(time.perf_counter() - t0, 2)
        }

        # 5. Exécution / Blocage VERALUME
        if gate_verdict.get("status") == "APPROVED":
            outil_nom = planned_tool.get("outil")
            args = planned_tool.get("args", {})
            acte = self.agent_kernel.agir(outil_nom, **args)
            execution_result["veralume_acte"] = {
                "outil": acte.outil,
                "execute": acte.execute,
                "resultat": acte.resultat,
                "motif": acte.motif,
                "reversibilite": acte.reversibilite.value,
                "trace_stric_i": {
                    "decision": acte.trace.decision,
                    "observe": acte.trace.observe,
                    "structure": acte.trace.structure,
                    "validation": acte.trace.validation
                }
            }
        elif gate_verdict.get("status") == "BLOCKED":
            # Déclenchement Boucle VCp1c
            manques = self.agent_kernel.enquete.manques(
                planned_tool.get("outil", "action"),
                planned_tool.get("args", {}),
                {"confirmation_causale": "L'incident présente une ambiguïté stochastique ou une violation de mandat. Confirmez explicitement la cible avant toute mutation."}
            )
            execution_result["vcp1c_questions"] = [m.question for m in manques]
            
        self.session_history.append(execution_result)
        return execution_result

    def list_sandbox_files(self) -> List[Dict[str, Any]]:
        """Liste les fichiers et versions de sauvegarde dans le bac à sable."""
        files = []
        for root, dirs, filenames in os.walk(self.workspace_path):
            if ".corbeille" in root:
                continue
            for f in filenames:
                full = os.path.join(root, f)
                rel = os.path.relpath(full, self.workspace_path)
                size = os.path.getsize(full)
                files.append({"chemin": rel, "taille_octets": size})
        
        # Liste des sauvegardes
        backups = []
        corbeille_dir = self.bac.corbeille
        if os.path.exists(corbeille_dir):
            for f in os.listdir(corbeille_dir):
                if f.endswith(".bak"):
                    full = os.path.join(corbeille_dir, f)
                    backups.append({"nom": f, "taille": os.path.getsize(full)})

        return {"fichiers": files, "sauvegardes_versionnees": backups}
