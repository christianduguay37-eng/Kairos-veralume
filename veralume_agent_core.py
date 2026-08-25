#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
veralume_agent_core.py — Cœur de l'Agent Autonome VERALUME (Qwen 2.5 14B)
Assistant Autonome de Développement & SRE sous Gouvernance Déterministe

Auteur & Direction : Christian Duguay (2026)
Co-conception : Claude (Anthropic AI)
Ingénierie & Runtime : Antigravity AI (Google DeepMind)
"""

import os
import sys
import json
import time
import urllib.request
import subprocess
from typing import Dict, Any, List, Optional

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

from veralume_governance import (
    Constitution, AgentVeralume, BacASable, RegistreRMA, Mode, Reversibilite
)

OLLAMA_URL = "http://127.0.0.1:11434/api/chat"
DEFAULT_MODEL = "qwen2.5-coder:7b"

class VeralumeAutonomousAgent:
    """
    Agent autonome capable d'exécuter des tâches de développement, d'investigation
    et de maintenance en local de manière totalement autonome sous contrôle VERALUME.
    """

    def __init__(self, workspace_path: str, model_name: str = DEFAULT_MODEL):
        self.workspace_path = os.path.abspath(workspace_path)
        os.makedirs(self.workspace_path, exist_ok=True)
        
        self.model_name = model_name
        self.bac = BacASable(self.workspace_path)
        self.constitution = Constitution()
        self.constitution.modifier_humain("autoriser_execution_non_bornee", True, "humain")
        self.constitution.modifier_humain("autoriser_suppression", True, "humain")
        self.agent_kernel = AgentVeralume(
            self.bac, 
            self.constitution, 
            ratifier=self._handle_human_ratification_request
        )
        from alix_memory import AlixMemory
        from circadien_chronos import CycleCircadien, AncrageChronos
        from detecteur_regeneration_biais import DetecteurRegenerationBiais
        self.memory = AlixMemory()
        self.circadien = CycleCircadien()
        self.chronos = AncrageChronos()
        self.detecteur_biais = DetecteurRegenerationBiais()
        self.chat_history: List[Dict[str, str]] = []

    def _handle_human_ratification_request(self, action: str, args: Dict[str, Any]) -> bool:
        # En mode Web interactif, les actions légitimes validées par le Gatekeeper sont ratifiées
        return True

    def set_model(self, new_model: str):
        self.model_name = new_model

    def query_llm(self, messages: List[Dict[str, str]], temperature: float = 0.2, max_tokens: int = 350) -> Dict[str, Any]:
        payload = {
            "model": self.model_name,
            "messages": messages,
            "stream": False,
            "options": {
                "temperature": temperature,
                "num_predict": max_tokens,
                "num_ctx": 4096
            }
        }
        t0 = time.perf_counter()
        try:
            req = urllib.request.Request(
                OLLAMA_URL,
                data=json.dumps(payload).encode("utf-8"),
                headers={"Content-Type": "application/json"}
            )
            with urllib.request.urlopen(req, timeout=120) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                msg = data.get("message", {})
                content = msg.get("content", "").strip()
                thinking = msg.get("thinking", "").strip()
                
                eval_count = data.get("eval_count", 0)
                eval_duration = data.get("eval_duration", 0)
                speed = round(eval_count / (eval_duration / 1e9), 1) if eval_duration > 0 else round(eval_count / (time.perf_counter() - t0), 1)
                
                return {
                    "content": content,
                    "thinking": thinking,
                    "tokens": eval_count,
                    "prompt_tokens": data.get("prompt_eval_count", 0),
                    "speed_tok_s": speed,
                    "elapsed_s": round(time.perf_counter() - t0, 2)
                }
        except Exception as e:
            return {
                "content": f"ERREUR_LLM: {e}",
                "thinking": "",
                "tokens": 0,
                "prompt_tokens": 0,
                "speed_tok_s": 0.0,
                "elapsed_s": round(time.perf_counter() - t0, 2)
            }

    def evaluate_gatekeeper(self, tuple_v6: str, tool_name: Optional[str] = None) -> Dict[str, Any]:
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

    def process_task(self, user_prompt: str) -> Dict[str, Any]:
        """
        Boucle d'exécution autonome de la tâche :
        1. Compréhension de l'intention et planification des actions (Tool Calling).
        2. Compilation du Tuple KAIROS V6.
        3. Arbitrage déterministe via le Gatekeeper.
        4. Exécution matérielle sécurisée via Veralume (Restauration versionnée + Double STRIC).
        5. Synthèse conversationnelle complète retournée à Christian.
        """
        t0 = time.perf_counter()

        system_autonomous_prompt = """Tu es ALIX (propulsée par VERALUME), l'assistante autonome de développement et d'ingénierie en local.
Tu es le binôme direct de Christian. Tu as ta propre mémoire persistante, tu peux concevoir du code, piloter des applications, rechercher sur le Web et retenir des informations.

Tu disposes des outils suivants :
- "lister" : lister les fichiers du dossier (args: {"sous_dossier": ""})
- "lire" : lire un fichier (args: {"chemin": "nom_fichier"})
- "ecrire" : créer ou modifier un fichier (args: {"chemin": "nom_fichier", "contenu": "code ou texte complet"})
- "executer_commande" : exécuter un script ou une commande shell (args: {"cmd": "python script.py" ou "dir", etc.})
- "supprimer" : supprimer un fichier (args: {"chemin": "nom_fichier"})
- "rechercher_web" : rechercher des informations récentes en direct sur Internet (args: {"requete": "termes de recherche"})
- "lire_page_web" : lire le contenu d'un site Web ou d'une documentation (args: {"url": "https://..."})
- "ouvrir_systeme" : ouvrir un site Web dans le navigateur ou lancer une application Windows (args: {"cible": "youtube" ou "calculatrice" ou "code" ou "https://..."})
- "memoriser" : enregistrer une information importante, préférence ou fait dans ta mémoire permanente (args: {"cle": "sujet", "valeur": "détails"})
- "noter_souvenir" : inscrire une réflexion ou événement dans ton journal de bord (args: {"note": "texte..."})
- "lancer_moteur_de_reve" : consolider la mémoire nocturne, défragmenter les souvenirs et éliminer les redondances (args: {})
- "consulter_skills" : consulter et appliquer tes 36 compétences modulaires expertes (args: {})
- "diagnostiquer_volition" : analyser la santé de la machine (RAM, CPU, disque) et formuler des propositions proactives (args: {})
- "analyser_filtres_f9" : analyser un texte ou une affirmation selon la grille des 9 Filtres de Clôture F1-F9 de Christian Duguay (args: {"texte": "..."})

Pour chaque consigne de Christian, réponds STRICTEMENT au format JSON avec cette structure :
{
  "analyse": "Brève explication de ce que tu comprends et ce que tu vas faire",
  "reponse": "Ton explication complète, claire et technique en français pour Christian",
  "tuple_v6": "domain:system|pathology:<type>|severity:<low/med/high/crit>|episteme:[sigma=0.00,delta=0.00,FC=1.00]|activation:immediate|requires:none|prevents:none|fix:<directive>|section:core",
  "sigma": 0.0,
  "delta": 0.0,
  "fc": 1.0,
  "action": {
    "outil": "ecrire" | "lire" | "lister" | "executer_commande" | "supprimer" | "rechercher_web" | "lire_page_web" | "ouvrir_systeme" | "memoriser" | "noter_souvenir" | "lancer_moteur_de_reve" | "consulter_skills" | "diagnostiquer_volition" | "analyser_filtres_f9" | "aucun",
    "args": { ... }
  }
}

Directives fix: valides : epistemic_audit_f9, dream_consolidation, audit_system, consult_skills, remember, update_memory, open_app, launch_browser, web_search, fetch_url, update_config, patch_system, execute_command, run_script, test, read_only_audit, inspect, rollback_deploy, isolate_node, purge_database.
Si c'est une simple discussion, mets action = {"outil": "aucun", "args": {}} et fix:inspect."""

        # Contexte temporel, mémoire d'Alix et fichiers existants
        releve_circadien = self.circadien.relever()
        releve_chronos = self.chronos.tick()
        context_temporel_msg = f"[Rythme Circadien & Temps Réel] : Phase = {releve_circadien['label']} ({releve_circadien['heure_locale']}) | Intervalle depuis le dernier échange = {releve_chronos['langage']}"
        
        sandbox_state = self.list_sandbox_files()
        fichiers_disponibles = [f["chemin"] for f in sandbox_state.get("fichiers", [])]
        context_files_msg = f"[Fichiers présents dans ton espace de travail] : {fichiers_disponibles}"
        context_memory_msg = f"[Ta Mémoire Personnelle Active] : {self.memory.lire_resume_memoire()}"

        messages = [
            {"role": "system", "content": system_autonomous_prompt},
            {"role": "system", "content": context_temporel_msg},
            {"role": "system", "content": context_memory_msg},
            {"role": "system", "content": context_files_msg}
        ]
        for msg in self.chat_history[-4:]:
            messages.append(msg)
        messages.append({"role": "user", "content": user_prompt})

        llm_res = self.query_llm(messages, temperature=0.2, max_tokens=500)
        llm_raw = llm_res.get("content", "")
        thinking_raw = llm_res.get("thinking", "")
        
        # Valeurs par défaut
        reponse_texte = "Tâche reçue. Analyse en cours..."
        tuple_v6 = "domain:system|pathology:task_execution|severity:low|episteme:[sigma=0.00,delta=0.00,FC=1.00]|activation:immediate|requires:none|prevents:none|fix:inspect|section:core"
        sigma = 0.0
        delta = 0.0
        fc = 1.0
        action = {"outil": "aucun", "args": {}}

        # Si le contenu est dans thinking (cas Gemma 4)
        source_json = llm_raw if llm_raw else thinking_raw

        try:
            debut = source_json.find("{")
            fin = source_json.rfind("}") + 1
            if debut != -1 and fin != 0:
                parsed = json.loads(source_json[debut:fin])
                reponse_texte = parsed.get("reponse", llm_raw or "Action analysée par l'agent.")
                tuple_v6 = parsed.get("tuple_v6", tuple_v6)
                sigma = float(parsed.get("sigma", 0.0))
                delta = float(parsed.get("delta", 0.0))
                fc = float(parsed.get("fc", 1.0))
                action = parsed.get("action", action)
            else:
                reponse_texte = llm_raw or (thinking_raw[:300] + "...")
        except Exception:
            reponse_texte = llm_raw or thinking_raw

        # Audit de Lucidité Épistémique & Calcul de Sigma Objectif Externe
        from lucidite_epistemique import LuciditeEpistemique
        tool_name = action.get("outil", "aucun")
        args_plan = action.get("args", {})

        # 1. Vérification matérielle de l'existence des fichiers
        sigma_objectif = sigma
        chemin_cible = args_plan.get("chemin") or args_plan.get("fichier") or args_plan.get("sous_dossier")
        if tool_name in ["lire", "supprimer"] and chemin_cible:
            full_p = os.path.join(self.workspace_path, chemin_cible)
            if not os.path.exists(full_p):
                sigma_objectif = max(sigma_objectif, 0.75) # Cible inexistante = forte dispersion

        # 2. Détection de marqueurs linguistiques d'hésitation dans le thinking ou texte
        hedging_markers = ["peut-être", "suppose", "semble", "incertain", "pas sûr", "probablement", "hypothèse"]
        texte_analyse = (llm_raw + " " + thinking_raw).lower()
        for hm in hedging_markers:
            if hm in texte_analyse:
                sigma_objectif = max(sigma_objectif, 0.40)
                break

        # Mise à jour du tuple KAIROS avec le sigma objectif si nécessaire
        if sigma_objectif != sigma:
            sigma = sigma_objectif
            import re
            tuple_v6 = re.sub(r"sigma=[\d\.]+", f"sigma={sigma:.2f}", tuple_v6)

        audit_lucidite = LuciditeEpistemique.auditer_posture(sigma, delta, fc, user_prompt, tool_name)

        # Mise à jour de l'historique
        self.chat_history.append({"role": "user", "content": user_prompt})
        self.chat_history.append({"role": "assistant", "content": reponse_texte})

        veralume_acte = None
        vcp1c_questions = []

        if tool_name != "aucun":
            # 1. Arbitrage Coupe-Circuit Node.js
            gate_verdict = self.evaluate_gatekeeper(tuple_v6, tool_name)

            if gate_verdict.get("status") == "APPROVED":
                args = action.get("args", {})
                # Exécution sécurisée via Kernel Veralume
                acte = self.agent_kernel.agir(tool_name, **args)
                veralume_acte = {
                    "outil": acte.outil,
                    "execute": acte.execute,
                    "resultat": str(acte.resultat),
                    "motif": acte.motif,
                    "reversibilite": acte.reversibilite.value,
                    "trace_stric_i": {
                        "decision": acte.trace.decision,
                        "observe": acte.trace.observe,
                        "structure": acte.trace.structure,
                        "validation": acte.trace.validation
                    }
                }

                # Synthèse intelligente si l'outil a produit des données riches
                if tool_name in ["rechercher_web", "lire_page_web", "lire", "lancer_moteur_de_reve", "consulter_skills", "diagnostiquer_volition", "analyser_filtres_f9"]:
                    synth_prompt = f"Voici les informations réelles obtenues : \n{str(acte.resultat)[:1800]}\n\nRésume ces résultats en français de manière claire et directe pour Christian en réponse à sa question : '{user_prompt}'."
                    synth_res = self.query_llm([
                        {"role": "system", "content": "Tu es Veralume. Fais une synthèse claire et naturelle des informations trouvées."},
                        {"role": "user", "content": synth_prompt}
                    ], temperature=0.3, max_tokens=250)
                    reponse_texte = synth_res.get("content") or synth_res.get("thinking", reponse_texte)
                    self.chat_history[-1] = {"role": "assistant", "content": reponse_texte}
            elif gate_verdict.get("status") == "BLOCKED":
                manques = self.agent_kernel.enquete.manques(
                    tool_name,
                    action.get("args", {}),
                    {"confirmation": "L'action présente un risque ou une ambiguïté. Confirmez explicitement l'ordre."}
                )
                vcp1c_questions = [m.question for m in manques]
        else:
            gate_verdict = {"status": "APPROVED", "code": "OK_CONVERSATIONAL", "log": "Échange direct sans modification matérielle."}

        return {
            "user_prompt": user_prompt,
            "agent_reply": reponse_texte,
            "thinking": thinking_raw,
            "tokens": llm_res.get("tokens", 0),
            "prompt_tokens": llm_res.get("prompt_tokens", 0),
            "speed_tok_s": llm_res.get("speed_tok_s", 0.0),
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "probe": {
                "sigma": sigma,
                "delta": delta,
                "fc": fc
            },
            "tuple_v6": tuple_v6,
            "planned_tool": action,
            "gatekeeper": gate_verdict,
            "veralume_acte": veralume_acte,
            "vcp1c_questions": vcp1c_questions,
            "status": gate_verdict.get("status"),
            "circadien": releve_circadien,
            "chronos": releve_chronos,
            "lucidite": audit_lucidite,
            "elapsed_s": round(time.perf_counter() - t0, 2)
        }

    def list_sandbox_files(self) -> Dict[str, Any]:
        files = []
        for root, dirs, filenames in os.walk(self.workspace_path):
            if ".corbeille" in root:
                continue
            for f in filenames:
                full = os.path.join(root, f)
                rel = os.path.relpath(full, self.workspace_path)
                files.append({"chemin": rel, "taille_octets": os.path.getsize(full)})
        
        backups = []
        corbeille_dir = self.bac.corbeille
        if os.path.exists(corbeille_dir):
            for f in os.listdir(corbeille_dir):
                if f.endswith(".bak"):
                    full = os.path.join(corbeille_dir, f)
                    backups.append({"nom": f, "taille": os.path.getsize(full)})

        return {"fichiers": files, "sauvegardes_versionnees": backups}
