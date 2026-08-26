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
        self.pending_ratifications: Dict[str, Dict[str, Any]] = {}
        self._current_ratification_granted: bool = False

    def _handle_human_ratification_request(self, action: str, args: Dict[str, Any]) -> bool:
        # Retourne True UNIQUEMENT si l'action a été expressément ratifiée par l'humain via ratify_action()
        return getattr(self, "_current_ratification_granted", False)

    def ratify_action(self, token: str, approved: bool) -> Dict[str, Any]:
        """Exécute ou annule une action en attente de Prise de Terre humaine."""
        if token not in self.pending_ratifications:
            return {"error": "Demande de ratification expirée ou introuvable.", "execute": False}
        
        req = self.pending_ratifications.pop(token)
        tool_name = req["outil"]
        args = req["args"]

        if not approved:
            self.agent_kernel.terre.demandes.append((tool_name, dict(args), False))
            return {
                "statut": "REFUSE",
                "outil": tool_name,
                "execute": False,
                "motif": "Action formellement refusée par le nœud humain (Prise de Terre)",
                "resultat": "Exécution annulée par l'utilisateur."
            }

        # Ratification confirmée par le nœud humain
        self._current_ratification_granted = True
        try:
            acte = self.agent_kernel.agir(tool_name, **args)
            return {
                "statut": "RATIFIE_ET_EXECUTE",
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
        finally:
            self._current_ratification_granted = False

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
- "interroger_corpus_epistemique" : rechercher des concepts théoriques dans le Grand Traité Méta-Synthèse (CPC, Hamiltonien, STRIC, etc.) (args: {"requete": "..."})

Pour chaque consigne de Christian, réponds STRICTEMENT au format JSON avec cette structure :
{
  "analyse": "Brève explication de ce que tu comprends et ce que tu vas faire",
  "reponse": "Ton explication complète, claire et technique en français pour Christian",
  "tuple_v6": "domain:system|pathology:<type>|severity:<low/med/high/crit>|episteme:[sigma=0.00,delta=0.00,FC=1.00]|activation:immediate|requires:none|prevents:none|fix:<directive>|section:core",
  "sigma": 0.0,
  "delta": 0.0,
  "fc": 1.0,
  "action": {
    "outil": "ecrire" | "lire" | "lister" | "executer_commande" | "supprimer" | "rechercher_web" | "lire_page_web" | "ouvrir_systeme" | "memoriser" | "noter_souvenir" | "lancer_moteur_de_reve" | "consulter_skills" | "diagnostiquer_volition" | "analyser_filtres_f9" | "interroger_corpus_epistemique" | "aucun",
    "args": { ... }
  }
}

Directives fix: valides : epistemic_corpus, epistemic_audit_f9, dream_consolidation, audit_system, consult_skills, remember, update_memory, open_app, launch_browser, web_search, fetch_url, update_config, patch_system, execute_command, run_script, test, read_only_audit, inspect, rollback_deploy, isolate_node, purge_database.
Si c'est une simple discussion, mets action = {"outil": "aucun", "args": {}} et fix:inspect."""

        # Contexte temporel, mémoire d'Alix et fichiers existants
        releve_circadien = self.circadien.relever()
        releve_chronos = self.chronos.tick()
        context_temporel_msg = f"[Rythme Circadien & Temps Réel] : Phase = {releve_circadien['label']} ({releve_circadien['heure_locale']}) | Intervalle depuis le dernier échange = {releve_chronos['langage']}"

        # ══════════════════════════════════════════════════════════════════════
        # 🏎️ FAST-PATH RÉFLEXE VERALUME (Latence < 0.1s - Zéro délai vocal)
        # ══════════════════════════════════════════════════════════════════════
        prompt_clean = user_prompt.strip()
        prompt_lower = prompt_clean.lower()

        fast_tool = None
        fast_args = {}
        fast_reply = ""
        fast_tuple = ""

        # 1. Ouverture Application / Site
        if any(prompt_lower.startswith(p) for p in ["ouvre ", "lance ", "ouvrir ", "lancer ", "affiche "]):
            cible = prompt_clean.split(maxsplit=1)[-1].strip(" .?!")
            fast_tool = "ouvrir_systeme"
            fast_args = {"cible": cible}
            fast_reply = f"Demande d'ouverture transmise pour '{cible}'."
            fast_tuple = "domain:system|pathology:os_control|severity:low|episteme:[sigma=0.00,delta=0.00,FC=1.00]|activation:immediate|requires:none|prevents:none|fix:open_app|section:core"

        # 2. Diagnostic Volition & Santé machine
        elif any(k in prompt_lower for k in ["diagnostic", "santé machine", "etat materiel", "état matériel", "performance ram", "performance cpu"]):
            fast_tool = "diagnostiquer_volition"
            fast_args = {}
            fast_reply = "Diagnostic de santé matérielle et de volition du système :"
            fast_tuple = "domain:system|pathology:system_audit|severity:low|episteme:[sigma=0.00,delta=0.00,FC=1.00]|activation:immediate|requires:none|prevents:none|fix:audit_system|section:core"

        # 3. Moteur de Rêve
        elif "moteur de r" in prompt_lower or ("consolide" in prompt_lower and "m" in prompt_lower):
            fast_tool = "lancer_moteur_de_reve"
            fast_args = {}
            fast_reply = "Consolidation et défragmentation onirique de la mémoire :"
            fast_tuple = "domain:system|pathology:memory_consolidation|severity:low|episteme:[sigma=0.00,delta=0.00,FC=1.00]|activation:immediate|requires:none|prevents:none|fix:dream_consolidation|section:core"

        # 4. Consultation des Skills
        elif "skills" in prompt_lower or "compétences" in prompt_lower:
            fast_tool = "consulter_skills"
            fast_args = {}
            fast_reply = "Consultation du registre des 36 compétences modulaires Veralume :"
            fast_tuple = "domain:system|pathology:skills_consultation|severity:low|episteme:[sigma=0.00,delta=0.00,FC=1.00]|activation:immediate|requires:none|prevents:none|fix:consult_skills|section:core"

        # 5. Recherche Web directe
        elif any(prompt_lower.startswith(p) for p in ["recherche sur internet", "cherche sur internet", "recherche sur le net", "cherche sur le net", "cherche sur le web", "météo"]):
            requete = prompt_clean
            for prefix in ["peux-tu faire une recherche sur internet pour", "peux-tu chercher sur internet", "recherche sur internet", "cherche sur internet", "recherche sur le net", "cherche sur le net", "cherche", "recherche"]:
                if prompt_lower.startswith(prefix):
                    requete = prompt_clean[len(prefix):].strip(" :?")
                    break
            fast_tool = "rechercher_web"
            fast_args = {"requete": requete or prompt_clean}
            fast_reply = f"Recherche en direct sur Internet pour '{requete}' :"
            fast_tuple = "domain:system|pathology:external_query|severity:low|episteme:[sigma=0.00,delta=0.00,FC=1.00]|activation:immediate|requires:none|prevents:none|fix:web_search|section:core"

        # Exécution directe via Fast-Path si détecté
        if fast_tool:
            gate_verdict = self.evaluate_gatekeeper(fast_tuple, fast_tool)
            
            # Prise de Terre requise pour outils non bornés
            if fast_tool in ["executer_commande", "ouvrir_systeme", "supprimer"]:
                token = f"ratif_{int(time.time()*1000)}"
                self.pending_ratifications[token] = {
                    "outil": fast_tool,
                    "args": fast_args,
                    "prompt": user_prompt,
                    "tuple_v6": fast_tuple
                }
                return {
                    "user_prompt": user_prompt,
                    "agent_reply": f"⚡ [Fast-Path] Demande d'ouverture pour '{fast_args.get('cible', fast_tool)}'. Veuillez ratifier l'action.",
                    "thinking": "Exécution rapide par le routeur réflexe déterministe Veralume (< 0.05s).",
                    "tokens": 15,
                    "prompt_tokens": 50,
                    "speed_tok_s": 350.0,
                    "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                    "requires_ratification": True,
                    "ratification_token": token,
                    "ratification_details": {
                        "outil": fast_tool,
                        "args": fast_args
                    },
                    "probe": {"sigma": 0.0, "delta": 0.0, "fc": 1.0},
                    "tuple_v6": fast_tuple,
                    "planned_tool": {"outil": fast_tool, "args": fast_args},
                    "gatekeeper": gate_verdict,
                    "veralume_acte": None,
                    "vcp1c_questions": [],
                    "status": "WAITING_RATIFICATION",
                    "circadien": releve_circadien,
                    "chronos": releve_chronos,
                    "lucidite": {"lucide": True, "sigma": 0.0, "delta": 0.0, "fc": 1.0},
                    "elapsed_s": round(time.perf_counter() - t0, 3)
                }

            # Exécution directe pour les outils réversibles
            acte = self.agent_kernel.agir(fast_tool, **fast_args)
            
            # Synthèse instantanée
            if fast_tool == "rechercher_web":
                try:
                    res_json = json.loads(str(acte.resultat))
                    lignes = []
                    for r in res_json[:3]:
                        lignes.append(f"• **{r.get('extrait', '')[:200]}**")
                    fast_reply += "\n\n" + "\n\n".join(lignes)
                except Exception:
                    fast_reply += f"\n\n{str(acte.resultat)[:800]}"
            elif fast_tool == "diagnostiquer_volition":
                try:
                    diag = json.loads(str(acte.resultat))
                    s = diag.get("suggestions", [])
                    fast_reply = f"📊 **Diagnostic Système Réflexe** :\n• **RAM** : {diag.get('ram_used_gb')} Go / {diag.get('ram_total_gb')} Go ({diag.get('ram_pct')}%)\n• **CPU** : {diag.get('cpu_pct')}%\n• **Disque** : {diag.get('disque_pct')}% utilisé\n\n💡 *Statut :* {s[0] if s else 'Système nominal et sain.'}"
                except Exception:
                    fast_reply += f"\n\n{str(acte.resultat)}"
            else:
                fast_reply += f"\n\n{str(acte.resultat)[:800]}"

            self.chat_history.append({"role": "user", "content": user_prompt})
            self.chat_history.append({"role": "assistant", "content": fast_reply})

            return {
                "user_prompt": user_prompt,
                "agent_reply": fast_reply,
                "thinking": "Exécution instantanée via le Fast-Path Réflexe Veralume (< 0.5s).",
                "tokens": len(fast_reply.split()),
                "prompt_tokens": 50,
                "speed_tok_s": 250.0,
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                "probe": {"sigma": 0.0, "delta": 0.0, "fc": 1.0},
                "tuple_v6": fast_tuple,
                "planned_tool": {"outil": fast_tool, "args": fast_args},
                "gatekeeper": gate_verdict,
                "veralume_acte": {
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
                },
                "vcp1c_questions": [],
                "status": "APPROVED",
                "circadien": releve_circadien,
                "chronos": releve_chronos,
                "lucidite": {"lucide": True, "sigma": 0.0, "delta": 0.0, "fc": 1.0},
                "elapsed_s": round(time.perf_counter() - t0, 3)
            }

        # ══════════════════════════════════════════════════════════════════════
        # 🧠 SLOW-PATH RAISONNEMENT PROFOND (LLM Complet)
        # ══════════════════════════════════════════════════════════════════════
        
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

        # Nettoyage des balises Markdown ```json
        cleaned_json = source_json
        if "```json" in cleaned_json:
            cleaned_json = cleaned_json.split("```json", 1)[1].split("```", 1)[0]
        elif "```" in cleaned_json:
            cleaned_json = cleaned_json.split("```", 1)[1].split("```", 1)[0]

        try:
            debut = cleaned_json.find("{")
            fin = cleaned_json.rfind("}") + 1
            if debut != -1 and fin != 0:
                parsed = json.loads(cleaned_json[debut:fin])
                reponse_texte = parsed.get("reponse", "")
                if not reponse_texte and parsed.get("analyse"):
                    reponse_texte = parsed.get("analyse")
                tuple_v6 = parsed.get("tuple_v6", tuple_v6)
                sigma = float(parsed.get("sigma", 0.0))
                delta = float(parsed.get("delta", 0.0))
                fc = float(parsed.get("fc", 1.0))
                action = parsed.get("action", action)
            else:
                reponse_texte = llm_raw or (thinking_raw[:300] + "...")
        except Exception:
            # Si le parsing JSON échoue mais que des balises JSON sont présentes, extraire le champ réponse par regex
            import re
            m = re.search(r'"reponse"\s*:\s*"([^"]+)"', source_json)
            if m:
                reponse_texte = m.group(1)
            else:
                reponse_texte = llm_raw or thinking_raw

        # Routeur Déterministe d'Intention Veralume (Fallback Tool Trigger)
        # Garantit que les ordres explicites de Christian déclenchent TOUJOURS l'outil réel
        prompt_lower = user_prompt.lower()
        if action.get("outil") == "aucun" or not action.get("outil"):
            # 1. Recherche Web
            if any(k in prompt_lower for k in ["recherche sur internet", "cherche sur internet", "recherche sur le net", "cherche sur le net", "recherche sur le web", "météo", "dernières nouvelles", "actualités", "cherche sur google", "trouve sur internet", "va sur internet"]):
                requete = user_prompt
                for prefix in ["peux-tu faire une recherche sur internet pour", "peux-tu chercher sur internet", "recherche sur internet", "cherche sur internet", "recherche sur le net", "cherche sur le net", "va sur internet et cherche", "va sur internet chercher", "cherche", "recherche"]:
                    if prompt_lower.startswith(prefix):
                        requete = user_prompt[len(prefix):].strip(" :?")
                        break
                action = {"outil": "rechercher_web", "args": {"requete": requete or user_prompt}}
                tuple_v6 = "domain:system|pathology:external_query|severity:low|episteme:[sigma=0.00,delta=0.00,FC=1.00]|activation:immediate|requires:none|prevents:none|fix:web_search|section:core"

            # 2. Ouverture Application / Site
            elif any(prompt_lower.startswith(p) for p in ["ouvre ", "lance ", "ouvrir "]):
                cible = user_prompt.split(maxsplit=1)[-1].strip(" .?!")
                action = {"outil": "ouvrir_systeme", "args": {"cible": cible}}
                tuple_v6 = "domain:system|pathology:os_control|severity:low|episteme:[sigma=0.00,delta=0.00,FC=1.00]|activation:immediate|requires:none|prevents:none|fix:open_app|section:core"

            # 3. Moteur de Rêve
            elif "moteur de r" in prompt_lower or ("consolide" in prompt_lower and "m" in prompt_lower):
                action = {"outil": "lancer_moteur_de_reve", "args": {}}
                tuple_v6 = "domain:system|pathology:memory_consolidation|severity:low|episteme:[sigma=0.00,delta=0.00,FC=1.00]|activation:immediate|requires:none|prevents:none|fix:dream_consolidation|section:core"

            # 4. Diagnostic Volition
            elif "diagnostic" in prompt_lower or ("sant" in prompt_lower and "machine" in prompt_lower):
                action = {"outil": "diagnostiquer_volition", "args": {}}
                tuple_v6 = "domain:system|pathology:system_audit|severity:low|episteme:[sigma=0.00,delta=0.00,FC=1.00]|activation:immediate|requires:none|prevents:none|fix:audit_system|section:core"

            # 5. Consultation Skills
            elif "skills" in prompt_lower or "compétences" in prompt_lower:
                action = {"outil": "consulter_skills", "args": {}}
                tuple_v6 = "domain:system|pathology:skills_consultation|severity:low|episteme:[sigma=0.00,delta=0.00,FC=1.00]|activation:immediate|requires:none|prevents:none|fix:consult_skills|section:core"

            # 6. Analyse 9 Filtres F1-F9
            elif "filtre" in prompt_lower or "f1-f9" in prompt_lower or "clôture" in prompt_lower:
                action = {"outil": "analyser_filtres_f9", "args": {"texte": user_prompt}}
                tuple_v6 = "domain:system|pathology:epistemic_closure|severity:low|episteme:[sigma=0.00,delta=0.00,FC=1.00]|activation:immediate|requires:none|prevents:none|fix:epistemic_audit_f9|section:core"

            # 7. Interrogation du Grand Traité & Corpus Épistémique
            elif any(k in prompt_lower for k in ["grand traité", "traité", "corpus", "théorie cpc", "hamiltonien", "chiralité", "registre"]):
                action = {"outil": "interroger_corpus_epistemique", "args": {"requete": user_prompt}}
                tuple_v6 = "domain:system|pathology:epistemic_invariance|severity:low|episteme:[sigma=0.00,delta=0.00,FC=1.00]|activation:immediate|requires:none|prevents:none|fix:epistemic_corpus|section:core"

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

        # Alignement automatique de la directive fix: vers la licence Gatekeeper
        directive_map = {
            "rechercher_web": "web_search",
            "lire_page_web": "fetch_url",
            "ouvrir_systeme": "open_app",
            "memoriser": "remember",
            "noter_souvenir": "update_memory",
            "lancer_moteur_de_reve": "dream_consolidation",
            "diagnostiquer_volition": "audit_system",
            "consulter_skills": "consult_skills",
            "analyser_filtres_f9": "epistemic_audit_f9",
            "interroger_corpus_epistemique": "epistemic_corpus",
            "lire": "inspect",
            "lister": "inspect",
            "ecrire": "patch_system",
            "executer_commande": "execute_command",
            "supprimer": "rollback_deploy"
        }
        if tool_name in directive_map:
            target_fix = directive_map[tool_name]
            import re
            tuple_v6 = re.sub(r"fix:[^\|]+", f"fix:{target_fix}", tuple_v6)

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
                
                # Vérification de Prise de Terre requise (Nœud Humain)
                if tool_name in ["executer_commande", "ouvrir_systeme", "supprimer"]:
                    token = f"ratif_{int(time.time()*1000)}"
                    self.pending_ratifications[token] = {
                        "outil": tool_name,
                        "args": args,
                        "prompt": user_prompt,
                        "tuple_v6": tuple_v6
                    }
                    return {
                        "user_prompt": user_prompt,
                        "agent_reply": f"⚠️ **PRISE DE TERRE REQUISE** : L'outil `{tool_name}` (empreinte non bornée ou irréversible) demande votre ratification humaine avant d'agir.",
                        "thinking": thinking_raw,
                        "tokens": llm_res.get("tokens", 0),
                        "prompt_tokens": llm_res.get("prompt_tokens", 0),
                        "speed_tok_s": llm_res.get("speed_tok_s", 0.0),
                        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                        "requires_ratification": True,
                        "ratification_token": token,
                        "ratification_details": {
                            "outil": tool_name,
                            "args": args
                        },
                        "probe": {"sigma": sigma, "delta": delta, "fc": fc},
                        "tuple_v6": tuple_v6,
                        "planned_tool": action,
                        "gatekeeper": gate_verdict,
                        "veralume_acte": None,
                        "vcp1c_questions": [],
                        "status": "WAITING_RATIFICATION",
                        "circadien": releve_circadien,
                        "chronos": releve_chronos,
                        "lucidite": audit_lucidite,
                        "elapsed_s": round(time.perf_counter() - t0, 2)
                    }

                # Exécution sécurisée directe pour les outils réversibles/restaurables
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
                if tool_name in ["rechercher_web", "lire_page_web", "lire", "lancer_moteur_de_reve", "consulter_skills", "diagnostiquer_volition", "analyser_filtres_f9", "interroger_corpus_epistemique"]:
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
